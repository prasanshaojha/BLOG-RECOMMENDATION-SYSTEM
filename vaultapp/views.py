# from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login
import pandas as pd
import numpy as np
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse , HttpResponseRedirect
from vaultapp.models import PublicLetter,LetterReaction,Comment, BlogPost, BlogInteraction
from django.shortcuts import render, redirect
from vaultapp.form import LetterForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import Letter
from .utils import calculate_combined_priority
# from django.contrib.admin.views.decorators import staff_member_required
from .models import Letter, PublicLetter, BlogInteraction
from django.http import JsonResponse


def create_or_schedule_letter(request):
    # FUTURA CREATE LETTER SECTION 
    letter_content = request.POST['content']
    letter_send_time = request.POST['send_date']
    is_public = request.POST.get('is_public', False)
    recipient_email = request.POST['recipient_email']
    
    # Create a letter object
    letter = Letter(
        recipient_email=recipient_email,
        content=letter_content,
        send_date=letter_send_time,
        is_public=is_public
    )
    
    # Calculate priority dynamically
    letter.priority = calculate_combined_priority(letter)

    # Save the letter with priority
    letter.save()

    return HttpResponse("Letter Scheduled Successfully!")



# REDIRECT TO THE LETTER IS SHEDULED SECTION

def letter_scheduled(request):
    return render(request, 'vaultapp/letter_scheduled.html')

# def letter_scheduled(request):
#     return render(request, 'vaultapp/letter_scheduled.html')

from vaultapp.utils import calculate_combined_priority  # Import priority calculation function

def write_letter(request):
    blogs = BlogPost.objects.all().order_by('-created_at')[:6]

    if request.method == 'POST':
        form = LetterForm(request.POST)
        
        if form.is_valid():
            letter = form.save(commit=False)  # Don't save yet, modify first
            
            # Check if user is authenticated
            if request.user.is_authenticated:
                letter.user = request.user  
            else:
                messages.info(request, "You need to log in before sending the letter.")
                return redirect('signin1')  
            
            letter.status = 'scheduled'  # Set status to scheduled
            
            # ✅ Calculate and set the priority
            letter.priority = calculate_combined_priority(letter)

            letter.save()  # Now save with priority

            messages.success(request, "Your letter has been scheduled successfully.")
            return redirect('letter_scheduled')  # Redirect to confirmation page
        else:
            messages.error(request, "There was an error with your submission.")
    else:
        form = LetterForm()

    return render(request, 'vaultapp/write_letter.html', {'form': form, 'blogs': blogs})



def blog_interaction(request, public_letter_id):
    public_letter = PublicLetter.objects.get(id=public_letter_id)

    if request.user.is_authenticated:
        # For authenticated users, assign their User instance
        interaction = BlogInteraction.objects.create(
            public_letter=public_letter,
            user=request.user,  # Assign the authenticated user
            interaction_type=request.POST.get('interaction_type')  # e.g., 'view'
        )
    else:
        # For unauthenticated (anonymous) users, do not assign user, instead use session_id
        interaction = BlogInteraction.objects.create(
            public_letter=public_letter,
            session_id=request.session.session_key,  
            interaction_type=request.POST.get('interaction_type')  
        )
    
    return HttpResponse("Interaction created.")

# FOR BLOG IN FUTURA
def blog_detail(request, id):
    try:
        blog = BlogPost.objects.get(id=id)
    except BlogPost.DoesNotExist:
        return redirect('error_page')  
    return render(request, 'vaultapp/blog_detail.html', {'blog': blog})




def home(request):
    # Fetching trending posts (limited to 6)
    trending_posts = PublicLetter.objects.filter(is_published=True).order_by('-shared_date')[:6]
    
    latest_posts = PublicLetter.objects.filter(is_published=True).order_by('-shared_date')[:10]

    # Rendering the home page with both sets of posts
    return render(request, 'vaultapp/home.html', {
        'trending_posts': trending_posts,
        'latest_posts': latest_posts
    })


def about(request):
    return render(request,'vaultapp/about.html')

# READ LETTER VIEW 
def post_list(request):
    posts = PublicLetter.objects.filter(is_published= True)
    return render(request, 'vaultapp/post.html', {'object_list': posts})

# BLOG DETAIL VIEW 
def post_detail(request, id):
    post = PublicLetter.objects.get(id=id)
    comments = Comment.objects.filter(public_letter=post, parent_comment__isnull=True).prefetch_related('replies')
    
    # Track the view interaction for authenticated and unauthenticated users
    if not request.session.get(f'viewed_post_{id}', False):
        if request.user.is_authenticated:
            BlogInteraction.objects.create(
                public_letter=post,
                user=request.user,  # Assign the authenticated user
                interaction_type='view'
            )
        else:
            BlogInteraction.objects.create(
                public_letter=post,
                session_id=request.session.session_key,  # Track anonymous users with session_id
                interaction_type='view'
            )
        # Mark the post as viewed in the session
        request.session[f'viewed_post_{id}'] = True

    # Increment the view count for the post
    post.view_count += 1
    post.save()

    # Check if the user has reacted to the post (like/dislike)
    user_reacted = LetterReaction.objects.filter(public_letter=post, user=request.user).exists()
    like_count = LetterReaction.objects.filter(public_letter=post).count()

    # Fetch blog recommendations using TF-IDF (based on description similarity)
    public_letters = PublicLetter.objects.filter(is_published=True).values('id', 'description', 'title')
    df = pd.DataFrame(public_letters)
    df['description'] = df['description'].fillna('')  # Handle empty descriptions

    # Apply TF-IDF recommendation system
    custom_tfidf = PublicLetter.recommend_blogs()  # Reuse the recommendation method from the model

    # Extract recommendations for the current post
    recommendations = next(
        (rec['recommended_blogs'] for rec in custom_tfidf if rec['id'] == post.id),
        []
    )
    
    # Fetch recommended blog objects from IDs (based on TF-IDF recommendations)
    recommended_blogs = PublicLetter.objects.filter(id__in=[rec['id'] for rec in recommendations])

    # -- Collaborative Filtering Section --
    
    # 1. Fetch all interactions (user-blog interactions)
    interactions = BlogInteraction.objects.all()
    
    # 2. Prepare the interaction matrix
    interaction_data = [
        {
            'user': interaction.user.id if interaction.user else None,
            'public_letter': interaction.public_letter.id,
            'interaction_type': interaction.interaction_type,
            'weight': post.get_interaction_weight(interaction.interaction_type)
        }
        for interaction in interactions
    ]
    
    # Create the interaction matrix DataFrame
    df_interactions = pd.DataFrame(interaction_data)
    
    # Remove rows where 'user' is NaN (for anonymous users without interaction)
    df_interactions = df_interactions.dropna(subset=['user'])
    
    # Pivot table to create the interaction matrix (users x blogs)
    interaction_matrix = df_interactions.pivot_table(
        index='user',
        columns='public_letter',
        values='weight',
        aggfunc='sum'
    )
    
    # Ensure no NaN values (representing no interaction) in the interaction matrix
    interaction_matrix = interaction_matrix.fillna(0)

    # 3. Compute the user similarity matrix (cosine similarity)
    user_similarity = PublicLetter.cosine_similarity(interaction_matrix.values)
    
    # Convert to DataFrame for easier access
    user_similarity_df = pd.DataFrame(
        user_similarity,
        index=interaction_matrix.index,
        columns=interaction_matrix.index
    )
    
    # Find similar users to the current user (i.e., the user who is viewing the post)
    if request.user.is_authenticated:
        similar_users = user_similarity_df[request.user.id].sort_values(ascending=False).iloc[1:6].index
    else:
        similar_users = user_similarity_df.iloc[:, 0].sort_values(ascending=False).iloc[1:6].index
    
    # Fetch blog posts interacted with by similar users
    similar_users_interactions = interaction_matrix.loc[similar_users]
    
    # Sum the interactions for each blog post across these similar users
    post_scores = similar_users_interactions.sum(axis=0)
    
    # Sort blog posts by score in descending order
    recommended_posts = post_scores.sort_values(ascending=False)
    
    # Filter out posts the user has already interacted with
    user_interactions = interaction_matrix.loc[request.user.id]
    recommended_posts = recommended_posts[user_interactions == 0]

    # Get the top N recommended blog posts (limit to top 5)
    recommended_blogs2 = PublicLetter.objects.filter(id__in=recommended_posts.head(5).index)
    recommendation_info = post.collaborative_recommend_blogs()

   
    interaction_matrix_limited = interaction_matrix.iloc[:, :10]

# Convert to HTML
    interaction_matrix_html = interaction_matrix_limited.to_html(classes="table table-striped")
 
# Add this DataFrame to your recommendation_info dictionary
    recommendation_info['Cosine_Similarity_Matrix'] = user_similarity_df.to_html()

# Convert the DataFrame to HTML for displaying in the template
    user_similarity_html = user_similarity_df.to_html()
    interaction_df_preview = recommendation_info.get('Interaction_DataFrame', '').to_html()
    filtered_nan_user_preview = recommendation_info.get('Filtered_NaN_user', '').to_html()
    similar_users_list = [{'user_id': user, 'similarity_score': user_similarity_df.at[user, request.user.id]} for user in similar_users]

# Convert the similar users into a DataFrame for rendering as an HTML table
    similar_users_df = pd.DataFrame(similar_users_list)

# Convert the DataFrame to HTML
    similar_users_html = similar_users_df.to_html(index=False)
    context = {
        'post': post,
        'comments': comments,
        'recommended_blogs': recommended_blogs,  
        'recommended_blogs2': recommended_blogs2,  
        'like_count': like_count,
        'user_reacted': user_reacted,
        'interaction_matrix': interaction_matrix_html,  
        'user_similarity_matrix': user_similarity_html,
        'similar_user': similar_users_html,
        'interaction_df_preview': interaction_df_preview,  
        'filtered_nan_user_preview': filtered_nan_user_preview, 
        
    }

    return render(request, 'vaultapp/post_detail.html', context)


@login_required
def toggle_like(request, public_letter_id):
    try:
        public_letter = PublicLetter.objects.get(id=public_letter_id)
        
        # Check if the user has already reacted to this post
        user_reacted = LetterReaction.objects.filter(public_letter=public_letter, user=request.user).exists()
        
        # Toggle the like status
        if user_reacted:
            # If the user already liked, remove the like
            reaction = LetterReaction.objects.get(public_letter=public_letter, user=request.user)
            reaction.delete()  # Unlike the post
            liked = False
        else:
            # If the user has not reacted, create a new reaction
            reaction = LetterReaction.objects.create(public_letter=public_letter, user=request.user)
            liked = True

        # Get the total like count for the post
        like_count = LetterReaction.objects.filter(public_letter=public_letter).count()

        # Return the response with the updated like status and like count
        return JsonResponse({'liked': liked, 'like_count': like_count, 'user_reacted': user_reacted})

    except PublicLetter.DoesNotExist:
        return JsonResponse({'error': 'Public letter not found'}, status=404)


def like_post(request, id):
    if request.method == "POST":
        public_letter = get_object_or_404(PublicLetter, id=id)

        # Check if the user is authenticated
        if request.user.is_authenticated:
            # For authenticated users, handle the like/unlike logic
            reaction, created = LetterReaction.objects.get_or_create(
                public_letter=public_letter,
                user=request.user
            )

            if not created:
                # If the reaction already exists, remove it (unlike)
                reaction.delete()
                liked = False
            else:
                # If no reaction existed, create it (like)
                liked = True

            # Record the like interaction in BlogInteraction for authenticated users
            BlogInteraction.objects.create(
                public_letter=public_letter,
                user=request.user,
                interaction_type='like'
            )

            # Return updated like count
            like_count = public_letter.likes.count()

            return JsonResponse({
                'liked': liked,
                'like_count': like_count,
            })

        else:
            # If the user is not authenticated, return a message prompting them to login
            return JsonResponse({
                'error': 'You must be logged in to like this post.'
            }, status=401)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def add_comment(request, id):
    if request.method == 'POST':
        # Check if the user is authenticated
        if request.user.is_authenticated:
            content = request.POST.get('content')
            parent_comment_id = request.POST.get('parent_comment_id')

            # Validate content
            if not content:
                return render(request, 'vaultapp/post_detail.html', {
                    'error': 'Content cannot be empty',
                    'id': id,
                })

            # Get the public letter
            public_letter = get_object_or_404(PublicLetter, id=id)

            # Get the parent comment (if provided)
            parent_comment = None
            if parent_comment_id:
                parent_comment = Comment.objects.filter(id=parent_comment_id).first()

            # Create the comment
            comment = Comment.objects.create(
                public_letter=public_letter,
                content=content,
                user=request.user,
                parent_comment=parent_comment
            )

            # Record the comment interaction in BlogInteraction for authenticated users
            BlogInteraction.objects.create(
                public_letter=public_letter,
                user=request.user,
                interaction_type='comment',
            )

            # Redirect to the post detail page
            return redirect('post_detail', id=id)

        else:
            # For unauthenticated (anonymous) users, prompt to log in
            return JsonResponse({
                'error': 'You must be logged in to comment on this post.'
            }, status=401)

    return render(request, 'vaultapp/post_detail.html', {'id': id})




#signup
def signup(request):
    if request.method == 'POST':
        # Extract form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        # Password validation
        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'vaultapp/signup.html')
        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters.")
            return render(request, 'vaultapp/signup.html')

        # Check if the email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'vaultapp/signup.html')

        # Create the user
        user = User.objects.create_user(username=name, email=email, password=password)
        user.save()

        # Automatically log the user in
        login(request, user)

        messages.success(request, "Account created successfully! You are now logged in.")
        return redirect('home')  # Redirect to the homepage or dashboard

    return render(request, 'vaultapp/signup.html')

#signin
def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Login the user
            login(request, user)

            # Show success message
            messages.success(request, "Logged in successfully!")

            # Redirect to the home page or dashboard
            return redirect('home')  # Replace 'home' with your desired URL name
        else:
            # Invalid credentials
            messages.error(request, "Invalid email or password.")
            return render(request, 'vaultapp/signin.html')

    return render(request, 'vaultapp/signin.html')





def contact_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Check if email and message are provided
        if email and message:
            # Sending email
            send_mail(
                'Contact Us Message',  # Subject
                message,  # Message content
                email,  # From email
                ['your_email@example.com'],  # To email (can be your admin email)
                fail_silently=False,
            )
            return HttpResponseRedirect('/success/')  # Redirect to a success page
        
        # If email or message is missing, return an error message
        else:
            return HttpResponse("Both email and message are required.", status=400)
    
    return render(request, 'contact.html')  # Return the contact form page
# views.py
def success_view(request):
    return render(request, 'vaultapp/success.html')  # Display a success message page


