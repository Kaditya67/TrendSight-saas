from django.urls import path
from django.shortcuts import redirect
from . import views

from .views import delete_blog, increment_view, increment_views, list_blogs, search_blogs ,text_blogs, update_like,upload_image,create_blog,view_blogs, view_uploaded_blog

app_name = 'blog'

urlpatterns = [

    path('blog', lambda request: redirect('list-blogs'), name='blogs'),
        
    path('image/upload/', upload_image, name='image-upload'),
    path('list_blogs/', list_blogs, name='list_blogs'),
    path('search/', views.search_blog, name='search'),
    path('search_blogs/', search_blogs, name='search_blogs'),

    # path('<str:blogid>/', get_blog, name='get-blog'),
    # path('<slug:slug>/', get_blog, name='get_blog'),
    path('create/',create_blog, name='create_blog'),
    # path('blog/like/<int:blog_id>/', like_blog, name='like_blog'),
    # path('blog/dislike/<int:blog_id>/',dislike_blog, name='dislike_blog'),
    # path('blog/comment/<int:blog_id>/', comment_blog, name='comment_blog'),
    # path('update-like/<int:blog_id>/', update_like, name='update_like'),
    path('interaction/<slug:slug>/', update_like, name='update_like'),
    path('comment_blog/<slug:slug>/', views.comment_blog, name='comment_blog'),
    path('list_blogs/<slug:slug>/', views.list_blogs, name='list_blogs'), 
    path('increment_view/<slug:slug>/', views.increment_view, name='increment_view'),
    path('increment_views/<int:blog_id>/', views.increment_views, name='increment_views'),

    path('text_blogs/',text_blogs,name='text_blogs'),
    path('view_blogs/', view_blogs, name='view_blogs'), 
    path('text_indiv/<slug:slug>/', views.view_individual_blog, name='view_individual_blog'), 
    # path('upload/', blog_upload, name='blog_upload'),
    path('blogs/uploaded/<int:blog_id>/', view_uploaded_blog, name='view_uploaded_blog'),  
    path('delete/<int:blog_id>/',delete_blog,name='delete_blog') 
]
