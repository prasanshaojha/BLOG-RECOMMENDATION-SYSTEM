from django.contrib import admin
from django.urls import path,include
from django.conf import  settings
from django.conf.urls.static import static
from vaultapp import views
from vaultapp.views import *
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('admin/', admin.site.urls, name= 'admin'),
    path('admin_tools_status/',include('admin_tools_stats.urls')),
    path('', home, name= 'home'),
    path('about/',about, name= 'about'),
    path('blog/<int:id>/', views.blog_detail, name='blog_detail'),
    path('posts/', views.post_list, name='post_list'),
    path('post/<int:id>/', views.post_detail, name='post_detail'),
    path('post/<int:id>/add-comment/', views.add_comment, name='add_comment'),
    path('like/<int:id>/', views.like_post, name='like_post'),
    path('signup/', views.signup, name='signup'), 
    # path('', views.home, name='home'),
    path('signin/', views.signin, name='signin'),
    path('write-letter/signin/', views.signin, name='signin1'),
    # path('home/', views.home, name='home'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('write-letter/', views.write_letter, name='write_letter'),
    path('write-letter/scheduled/',  views.letter_scheduled, name='letter_scheduled'),
    # path('write-letter/vaultapp/signin.html', views.signup, name='signup'),
    # path('write-letter/vaultapp/letter_scheduled.html', views.letter_scheduled, name='letter_scheduled'),
    path('post/<int:id>/', views.BlogPost, name='post_detail'),
    path('contact/', contact_view, name='contact'),
    path('success/', success_view, name='success'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

