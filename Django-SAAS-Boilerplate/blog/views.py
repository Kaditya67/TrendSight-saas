import json
import re
from tokenize import Comment

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, F, Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST
from blog.models import Blog
from utils.decorators import login_required_rest_api
from .forms import BlogForm, BlogImageForm
from .models import BlogImage, BlogView, TextBlogs  # Assuming this is your blog model
from .models import Blog, BlogInteraction, Comment, UserLike


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, F
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from .models import Blog

from django.db.models import F

@require_http_methods(['GET'])
def list_blogs(request):
    filter_type = request.GET.get('filter', 'latest')  # Default to 'latest'
    page_number = request.GET.get("page", 1)

    if filter_type == 'most_liked':
        blogs = Blog.objects.select_related('interaction') \
            .annotate(like_count=F('interaction__likes')) \
            .order_by('-like_count', '-datetime')
    elif filter_type == 'most_viewed':
        blogs = Blog.objects.select_related('interaction') \
            .annotate(view_count=F('interaction__views')) \
            .order_by('-view_count', '-datetime')
    elif filter_type == 'most_commented':
        blogs = Blog.objects.select_related('interaction') \
            .annotate(comment_count=F('interaction__comments')) \
            .order_by('-comment_count', '-datetime')
    elif filter_type == 'oldest':
        blogs = Blog.objects.all().order_by('datetime')
    else:  # Latest
        blogs = Blog.objects.all().order_by('-datetime')

    paginator = Paginator(blogs, per_page=6)

    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return render(request, 'blog/list_blogs.html', {
        'page': page,
        'blogs': page,
        'filter_type': filter_type
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
    




@receiver(post_save, sender=Blog)
def create_blog_interaction(sender, instance, created, **kwargs):
    if created:  # Only create BlogInteraction for new Blog instances
        BlogInteraction.objects.create(blog=instance)






def search_blog(request):
    query = request.GET.get('q', '')
    if query:
        blogs = Blog.objects.filter(title__icontains=query)
    else:
        blogs = Blog.objects.all()
    return render(request, 'blog/list_blogs.html', {'blogs': blogs, 'query': query})






def update_like(request, slug):
    if request.method == 'POST':
        blog = get_object_or_404(Blog, slug=slug)
        user = request.user

        # Check if the user has already liked the blog
        user_like, created = UserLike.objects.get_or_create(user=user, blog=blog)

        if created:
            # If the like was just created, increment the like count
            blog_interaction = get_object_or_404(BlogInteraction, blog=blog)
            blog_interaction.likes += 1
            blog_interaction.save()
            return JsonResponse({'status': 'liked'})
        else:
            # If the like already exists, remove it and decrement the like count
            user_like.delete()
            blog_interaction = get_object_or_404(BlogInteraction, blog=blog)
            blog_interaction.likes -= 1
            blog_interaction.save()
            return JsonResponse({'status': 'unliked'})

    return JsonResponse({'error': 'Invalid request'}, status=400)



def comment_blog(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    blog_interaction = get_object_or_404(BlogInteraction, blog=blog)
    user = request.user

    # Check if the user has already commented
    existing_comment = Comment.objects.filter(blog_interaction=blog_interaction, user=user).first()

    if request.method == 'POST':
        comment_text = request.POST.get('comment_text')

        if existing_comment:
            # If the user has already commented, update the existing comment
            existing_comment.text = comment_text
            existing_comment.save()
        else:
            # Save the new comment if no existing comment
            Comment.objects.create(blog_interaction=blog_interaction, user=user, text=comment_text)

        # Update the comment count (no need to update manually as it's already tracked by related_name)
        blog_interaction.comments_count = blog_interaction.comments.count()
        blog_interaction.save()

        # Redirect back to the list_blogs page with the updated comments
        return redirect('blog:list_blogs')

    # Render the template with the existing comment if any
    return render(request, 'blog/list_blogs.html', {
        'blog': blog,
        'existing_comment': existing_comment,
    })




@require_POST
def increment_view(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    blog_interaction = get_object_or_404(BlogInteraction, blog=blog)

    # Increment the view count
    blog_interaction.views = F('views') + 1
    blog_interaction.save()

    return JsonResponse({'status': 'success', 'views': blog_interaction.views})




@login_required
def text_blogs(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        author = request.POST.get('author')  # Name entered by the user
        date = request.POST.get('published_date')

        if(title,content):
            blog = TextBlogs.objects.create(
                title=title,
                content=content,
                author=author,  # Now this accepts the name directly
                published_date=date
            )
            return render(request, 'blog/text_blogs.html', {'blog': blog})  # Render after creation
        else:
            # Handle the case where not all fields are filled
            return render(request, 'blog/text_blogs.html', {'error': 'All fields must be filled.'})

    return render(request, 'blog/text_blogs.html')







from django.shortcuts import render
from blog.models import TextBlogs  # Import your model

# def view_blogs(request):
#     blogs = TextBlogs.objects.all().order_by('-created_at')  # Fetch all blogs ordered by latest
#     for blog in blogs:
#         match = re.search(r'<img[^>]*src="([^"]+)"', blog.content)
#         blog.first_image = match.group(1) if match else None
#     return render(request, 'blog/view_blogs.html', {'blogs': blogs})



from django.shortcuts import render, get_object_or_404
from .models import TextBlogs

def view_individual_blog(request, slug):
    blog = get_object_or_404(TextBlogs, slug=slug)
    print("Blog Upload Title:", BlogUpload.title)
    print("Blog Upload Content:", BlogUpload.content)
    print("Blog Upload Sequence:", BlogUpload.sequence)

    return render(request, 'blog/text_indiv.html', {'blog': blog})



from django.shortcuts import render, redirect
from .forms import BlogUploadForm
from .models import BlogUpload
import os

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import BlogUpload
from .forms import BlogUploadForm
import os
import docx
import pdfplumber
from pptx import Presentation





from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Count, F
from .models import TextBlogs, BlogUpload

from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Count, F
from django.views.decorators.http import require_http_methods
from .models import BlogUpload, TextBlogs

from django.db.models import F
from django.shortcuts import render
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods







import zipfile
import xml.etree.ElementTree as ET
from io import BytesIO

import base64
import imghdr
import zipfile
import xml.etree.ElementTree as ET
from django.core.files.base import ContentFile
from bs4 import BeautifulSoup
import mammoth



def extract_text_from_file(blog_upload):
    """Extracts text and images while preserving their order"""
    file_path = blog_upload.uploaded_file.path
    sequence = []  # Ordered sequence of text and image placeholders
    text = []  # To store extracted text
    images = []  # To store extracted images
    img_count = 0  # Initialize the image counter

    if file_path.endswith(".docx"):
        # Open the DOCX file and convert it to HTML
        with open(file_path, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
            html = result.value  # Extracted HTML content
            soup = BeautifulSoup(html, 'html.parser')

            # Process both text and images in the DOCX file
            for element in soup.find_all(['p', 'img']):
                if element.name == 'p':  # Extract text
                    text_content = element.get_text(strip=True)
                    if text_content:
                        text.append(text_content)
                        sequence.append("text")  # Add text to the sequence
                elif element.name == 'img':  # Handle images
                    img_src = element.get('src')
                    if img_src and img_src.startswith('data:image'):  # Check if base64 encoded
                        # Extract base64 data
                        img_data = img_src.split('base64,')[1]
                        img_data = base64.b64decode(img_data)
                        
                        # Determine image format
                        img_format = imghdr.what(None, img_data)
                        if img_format:
                            image_name = f"{blog_upload.id}_docx_image_{img_count}.{img_format}"
                            image_file = ContentFile(img_data, name=image_name)
                            blog_image = BlogImage.objects.create(image=image_file)
                            images.append(blog_image)
                            sequence.append("image")  # Add image to the sequence
                            img_count += 1

        # Extract images from DOCX file using rels (relationships)
        with zipfile.ZipFile(file_path, "r") as docx_zip:
            rels_data = docx_zip.read("word/_rels/document.xml.rels")
            
            # Parse the XML content of the rels file
            root = ET.fromstring(rels_data)
            
            # Iterate through each relationship to find image entries
            img_count = 0  # Reset the image counter for rel-based images
            for rel in root.findall(".//{http://schemas.openxmlformats.org/officeDocument/2006/relationships}Relationship"):
                target_ref = rel.attrib.get("Target", "")
                if "image" in target_ref:  # If the Target is an image
                    image_file_path = f"word/{target_ref}"  # Path to the image within the DOCX file
                    try:
                        image_data = docx_zip.read(image_file_path)
                        
                        # Determine image format
                        img_format = imghdr.what(None, image_data)
                        if img_format:
                            image_name = f"{blog_upload.id}_docx_image_{img_count}.{img_format}"
                            image_file = ContentFile(image_data, name=image_name)
                            blog_image = BlogImage.objects.create(image=image_file)
                            blog_upload.extracted_images.add(blog_image)  # Associate with BlogUpload
                            blog_upload.save()

                            images.append(blog_image.image.url)  # Store image URL
                            sequence.append(f"image_{len(images)-1}")  # Maintain order
                            img_count += 1
                    except KeyError:
                        continue  # If image file is missing, continue

    # Other formats: PDF and PPTX handling (unchanged)

    # Save extracted data to the blog model
    blog_upload.content = "\n".join(text)  # Save all extracted text as the content
    blog_upload.sequence = sequence  # Save the sequence of content (text and images)
    blog_upload.extracted_images.set(images)  # Save the extracted images
    blog_upload.save()

    # Debugging: Print the extracted content
    print("Extracted Sequence:", sequence)
    print("Extracted Text:", text)
    print("Extracted Images:", images)




from django.shortcuts import render, get_object_or_404

from django.shortcuts import render, get_object_or_404
from .models import BlogUpload



from django.shortcuts import get_object_or_404, redirect
from .models import BlogUpload, TextBlogs

@login_required
def delete_blog(request, blog_id):
    # Check if it's a text blog
    try:
        blog = TextBlogs.objects.get(id=blog_id)
        blog.delete()
    except TextBlogs.DoesNotExist:
        # If it's not a text blog, try to delete from the BlogUpload model
        blog = BlogUpload.objects.get(id=blog_id)
        blog.delete()
    
    return redirect('blog:view_blogs')

from django.shortcuts import render, redirect
from .models import TextBlogs, BlogUpload
from .forms import BlogUploadForm
# Ensure this function is properly defined
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import BlogUpload, TextBlogs
from .forms import BlogUploadForm
 # Ensure this function is correctly imported

@login_required
@require_http_methods(["GET", "POST"])
def view_blogs(request):
    """Handles viewing, filtering, and uploading blogs."""

    # Fetch text and uploaded blogs
    text_blogs = TextBlogs.objects.all().order_by('-created_at')
    uploaded_blogs = BlogUpload.objects.all()

    # Handle Blog Upload (Only for Superusers)
    if request.method == "POST" and request.user.is_superuser:
        form = BlogUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_blog = form.save()
            extract_text_from_file(uploaded_blog)  # Extract text if needed
            return redirect('blog:view_blogs')
    else:
        form = BlogUploadForm()

    # Handle Filtering
    filter_type = request.GET.get('filter', 'latest')  # Default filter
    if filter_type == 'most_viewed':
        uploaded_blogs = uploaded_blogs.order_by('-view_count')  # Requires `view_count` field in `BlogUpload`
    elif filter_type == 'oldest':
        uploaded_blogs = uploaded_blogs.order_by('uploaded_at')
    else:  # Default: Latest
        uploaded_blogs = uploaded_blogs.order_by('-uploaded_at')

    # Handle Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(uploaded_blogs, per_page=6)

    try:
        uploaded_blogs = paginator.page(page_number)
    except PageNotAnInteger:
        uploaded_blogs = paginator.page(1)
    except EmptyPage:
        uploaded_blogs = paginator.page(paginator.num_pages)

    return render(request, 'blog/view_blogs.html', {
        'text_blogs': text_blogs,
        'uploaded_blogs': uploaded_blogs,
        'filter_type': filter_type,
        'form': form
    })



from django.shortcuts import render
from .models import TextBlogs, BlogUpload

from django.shortcuts import render
from .models import TextBlogs, BlogUpload

def search_blogs(request):
    query = request.GET.get('q', '').strip()
    
    text_blogs = TextBlogs.objects.filter(title__icontains=query) if query else TextBlogs.objects.all()
    uploaded_blogs = BlogUpload.objects.filter(title__icontains=query) if query else BlogUpload.objects.all()

    return render(request, 'blog/view_blogs.html', {
        'text_blogs': text_blogs, 
        'uploaded_blogs': uploaded_blogs, 
        'query': query
    })


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from .models import BlogUpload, BlogView

@require_POST
def increment_views(request, blog_id):
    # Fetch the blog using the id
    blog = get_object_or_404(BlogUpload, id=blog_id)

    # Increment the view count
    blog.view_count = F('view_count') + 1
    blog.save()

    return JsonResponse({'status': 'success', 'views': blog.view_count})



from django.core.paginator import Paginator
from django.db.models import Count, F
from django.shortcuts import render

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from .models import BlogUpload



def view_uploaded_blog(request, blog_id):
    # Fetch the specific blog
    uploaded_blog = get_object_or_404(BlogUpload, id=blog_id)
    
    # Get 3 random related blogs (excluding the current blog)
    related_blogs = BlogUpload.objects.exclude(id=blog_id).order_by('?')[:3]

    # Extract stored sequence, text, and images
    content_sequence = uploaded_blog.sequence  # This maintains the order of elements
    texts = uploaded_blog.content.split("\n")  # Assuming text is stored as newline-separated
    images = uploaded_blog.extracted_images.all()  # Extracted images from ManyToMany field

    # Prepare combined content list
    combined_content = []
    text_idx = 0
    image_idx = 0

    for item in content_sequence:
        if item == "text":
            if text_idx < len(texts):  
                combined_content.append({"type": "text", "content": texts[text_idx]})
                text_idx += 1
        elif item == "image":
            if image_idx < len(images):  
                combined_content.append({"type": "image", "content": images[image_idx]})
                image_idx += 1

    # Prepare context for rendering
    context = {
        'blog': uploaded_blog,
        'combined_content': combined_content,
        'related_blogs': related_blogs,  # Add related blogs to context
    }

    return render(request, 'blog/text_indiv.html', context)


