from django import forms
from .models import Blog, BlogImage



class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'slug', 'body','video_url', 'thumbnail', 'draft']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 5, 'cols': 40}),
        }




class BlogImageForm(forms.ModelForm):

    class Meta:
        model = BlogImage
        fields = '__all__'


from django import forms
from .models import BlogUpload

class BlogUploadForm(forms.ModelForm):
    class Meta:
        model = BlogUpload
        fields = ['title', 'uploaded_file']
