from django.urls import path
from django.shortcuts import redirect

from .views import list_blogs, get_blog, upload_image,create_blog

# app_name = 'blog'

urlpatterns = [

    path('blog', lambda request: redirect('list-blogs'), name='blogs'),
        
    path('image/upload/', upload_image, name='image-upload'),
    path('', list_blogs, name='list-blogs'),

    # path('<str:blogid>/', get_blog, name='get-blog'),
    path('<slug:slug>/', get_blog, name='get_blog'),
    path('create/',create_blog, name='create_blog'),
    
]
