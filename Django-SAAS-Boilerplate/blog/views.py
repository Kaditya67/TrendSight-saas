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
    blog = get_object_or_404(Blog, slug=slug, draft=False)
    return render(request, 'html/blog/blog-view.html', {
        'blog': blog
    })


@require_http_methods(['GET'])
def list_blogs(request):

    page_number = request.GET.get("page", 1)
    blogs = Blog.objects.filter(draft=False).order_by('-datetime')

    paginator = Paginator(blogs, per_page=15)
    page = paginator.get_page(page_number)
    
    return render(request, 'html/blog/blog-list.html', {
                                                'blogs': page,
                                            })


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