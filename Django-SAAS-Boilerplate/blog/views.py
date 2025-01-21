import json
from tokenize import Comment
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .models import Blog
from .forms import BlogForm, BlogImageForm

from utils.decorators import login_required_rest_api

@require_http_methods(['GET'])
def get_blog(request, slug):
    blog = Blog.objects.get(slug=slug)
    interaction, created = BlogInteraction.objects.get_or_create(blog=blog)
    return JsonResponse({
        'blog': {
            'title': blog.title,
            'body': blog.body,
            'likes': interaction.likes,
            'dislikes': interaction.dislikes
        }
    })

from .models import Blog, BlogInteraction
from django.db.models import Count
from django.db.models import F
@require_http_methods(['GET'])

def list_blogs(request):
    filter_type = request.GET.get('filter', 'latest')  # Default to 'latest'
    page_number = request.GET.get("page", 1)
    
    # Debugging print: Check the filter_type value
    print(f"Filter type received: {filter_type}")
    
    if filter_type == 'most_liked':
        # Debugging print: Check the sorting behavior for most liked blogs
        blogs = Blog.objects.annotate(like_count=F('interaction__likes')).order_by('-like_count')
    elif filter_type == 'most_viewed':
        # Debugging print: Check the sorting behavior for most viewed blogs
        blogs = Blog.objects.annotate(view_count=F('interaction__views')).order_by('-view_count')
    elif filter_type == 'most_commented':
        # Debugging print: Check the sorting behavior for most commented blogs
        blogs = Blog.objects.annotate(comment_count=Count('interaction__comments')).order_by('-comment_count')
    elif filter_type == 'oldest':
        # Debugging print: Check the sorting behavior for oldest blogs
        blogs = Blog.objects.all().order_by('datetime')
    else:
        # Default to 'latest'
        blogs = Blog.objects.all().order_by('-datetime')
    
    paginator = Paginator(blogs, per_page=6)
    page = paginator.get_page(page_number)

    # Debugging print: Check the final list of blogs before rendering
    
    
    # Pass the blogs and filter_type to the template
    return render(request, 'blog/list_blogs.html', {'blogs': page, 'filter_type': filter_type})


BLOG_PERMISSIONS = ['blog.add_blog', 'blog.change_blog']


@login_required_rest_api
@require_http_methods(['POST'])
def upload_image(request):
    
    if request.user.has_perms(BLOG_PERMISSIONS):
        form = BlogImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save()
            return JsonResponse({'url': image.image.url}, status=201)

        else: 
            return JsonResponse({'error': form.errors.as_text()}, status=400)


    return JsonResponse({'error': 'Invalid form submission'}, status=401)



@require_http_methods(['GET', 'POST'])
@login_required_rest_api
def create_blog(request):
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.user = request.user  # Set the user as the author of the blog
            blog.save()
            return redirect('blog:view_blog', slug=blog.slug)  # Redirect to the newly created blog's view page
        else:
            return render(request, 'html/blog/blog_create.html', {'form': form})

    else:
        form = BlogForm()
        return render(request, 'html/blog/blog_create.html', {'form': form})
    



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Blog, BlogInteraction

@csrf_exempt  # Disable CSRF for this example (you can add CSRF protection in production)
def update_like(request, blog_id):
    if request.method == 'POST':
        action = request.POST.get('action')

        # Get the blog interaction or create it if it doesn't exist
        blog = Blog.objects.get(id=blog_id)
        interaction, created = BlogInteraction.objects.get_or_create(blog=blog)

        # Update like count
        if action == 'like':
            interaction.likes += 1
        elif action == 'dislike':
            interaction.dislikes += 1

        # Save the updated interaction
        interaction.save()

        # Return the updated like count
        return JsonResponse({
            'like_count': interaction.likes
        })

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import BlogInteraction
import json

@csrf_exempt
def update_interaction(request, blog_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action')  # Expect 'like' or 'dislike'

        interaction, _ = BlogInteraction.objects.get_or_create(blog_id=blog_id)

        if action == 'like':
            interaction.likes += 1
        elif action == 'dislike':
            interaction.dislikes += 1
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)

        interaction.save()

        return JsonResponse({
            'likes': interaction.likes,
            'dislikes': interaction.dislikes,
        }, status=200)

    return JsonResponse({'error': 'Invalid request'}, status=400)
