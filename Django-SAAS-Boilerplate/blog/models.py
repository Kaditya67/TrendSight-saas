from urllib.parse import parse_qs, urlparse
from django.db import models
from django.template.defaultfilters import slugify

from user.models import User
from utils.common import generate_uniqueid


def generate_id():
    # table =  apps.get_model('blog', 'Blog')
    return generate_uniqueid(Blog, 'blog_id')


class Blog(models.Model):

    blog_id = models.CharField(max_length=20, unique=True, blank=True, default=generate_id)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    thumbnail = models.ImageField(null=True, blank=True, upload_to='blogs/')

    slug = models.SlugField(blank=True, unique=True)

    title = models.CharField(max_length=200, default="", unique=True)  
    body = models.TextField(null=True, blank=True)

    draft = models.BooleanField(default=False, blank=True)
    datetime = models.DateTimeField(auto_now=True) # stays at last updated
    video_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs) -> None:
        
        if not self.slug:
            self.slug = slugify(self.title)

        return super().save(*args, **kwargs)
    
    def youtube_video_id(self):
        if self.video_url:
            parsed_url = urlparse(self.video_url)
            if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
                query = parse_qs(parsed_url.query)
                video_id = query.get('v')
                return video_id[0] if video_id else None
            elif parsed_url.hostname == 'youtu.be':
                return parsed_url.path[1:]  # Remove the leading '/'
        return None


class BlogImage(models.Model):

    blog = models.ForeignKey(to=Blog, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='blogs/')

    def __str__(self) -> str:
        return f'{self.image.url}'
    

class BlogInteraction(models.Model):
    blog = models.OneToOneField(Blog, on_delete=models.CASCADE, related_name='interaction')
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Interactions for {self.blog.title}"

    
    # Optional: If you want to store comments as well, you can create a related model.
    # For simplicity, let's assume comments are stored in a separate model
    # that references the BlogInteraction model.
    
  
    

class Comment(models.Model):
    blog_interaction = models.ForeignKey(BlogInteraction, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Assuming you want to track who commented
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.blog_interaction.blog.title}"


class UserLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'blog')  # Ensures a user can only like a blog once

    def __str__(self):
        return f"{self.user.username} liked {self.blog.title}"
