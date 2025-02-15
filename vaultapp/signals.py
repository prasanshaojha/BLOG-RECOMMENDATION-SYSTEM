from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from .models import LetterReaction, Comment, PublicLetter, BlogInteraction

# Signal to create a BlogInteraction when a reaction (like) is added
@receiver(post_save, sender=LetterReaction)
def create_blog_interaction_on_reaction(sender, instance, created, **kwargs):
    if created:
        BlogInteraction.objects.create(
            public_letter=instance.public_letter,
            user=instance.user,
            interaction_type='like',  # Set the interaction type to 'like'
            timestamp=instance.reacted_at,
        )

# Signal to create a BlogInteraction when a comment is added
@receiver(post_save, sender=Comment)
def create_blog_interaction_on_comment(sender, instance, created, **kwargs):
    if created:
        BlogInteraction.objects.create(
            public_letter=instance.public_letter,
            user=instance.user,
            interaction_type='comment',  # Set the interaction type to 'comment'
            timestamp=instance.created_at,
        )

# Signal to create a BlogInteraction when a public letter view count is updated
@receiver(post_save, sender=PublicLetter)
def create_blog_interaction_on_view(sender, instance, created, **kwargs):
    if not created:  # React only to updates
        view_count_diff = instance.view_count  # Get the updated view count
        for _ in range(view_count_diff):
            BlogInteraction.objects.create(
                public_letter=instance,
                interaction_type='view',  # Set the interaction type to 'view'
                timestamp=now(),
                session_id=None,  # Track anonymous users if necessary
            )
