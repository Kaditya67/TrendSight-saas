from django.urls import path
from django.shortcuts import redirect
from . import views

from .views import list_blogs, get_blog, update_interaction, update_like, upload_image,create_blog

app_name = 'blog'

urlpatterns = [

    path('blog', lambda request: redirect('list-blogs'), name='blogs'),
        
    path('image/upload/', upload_image, name='image-upload'),
    path('list_blogs/', list_blogs, name='list_blogs'),
    path('search/', views.search_blog, name='search'),

    # path('<str:blogid>/', get_blog, name='get-blog'),
    path('<slug:slug>/', get_blog, name='get_blog'),
    path('create/',create_blog, name='create_blog'),
    # path('blog/like/<int:blog_id>/', like_blog, name='like_blog'),
    # path('blog/dislike/<int:blog_id>/',dislike_blog, name='dislike_blog'),
    # path('blog/comment/<int:blog_id>/', comment_blog, name='comment_blog'),
    path('update-like/<int:blog_id>/', update_like, name='update_like'),
    path('interaction/<int:blog_id>/', update_interaction, name='update_interaction'),
]
