from django.contrib import admin
from django.db import models
from django.utils.safestring import mark_safe

from unfold.admin import ModelAdmin, StackedInline
from unfold.contrib.forms.widgets import WysiwygWidget

from .models import Blog, BlogImage

from .widgets import CSSAdminCode, UnfoldTrix


class InlineBlogImgAdmin(StackedInline):

    model = BlogImage
    extra = 0

class JSReadonly:
    """
         The admin widget trix-editor can't be customized in view only mode, 
         so add this code so readonly body can have the same css as Trix editor
         and avoid conflicting styling for heading
    """
    # https://stackoverflow.com/questions/14832739/django-admin-how-to-display-widget-on-readonly-field
    def __html__(self):
        return (
            """
            <script type="text/javascript">
                window.addEventListener("load", () => {
                    let labels = document.querySelectorAll("label")
                    let body = null;
                    console.log("labels: ", labels)
                    labels.forEach(lbl => {
                        if (lbl.innerText.toLowerCase() === "body:"){
                            body = lbl
                            body?.nextElementSibling?.classList.add("trix-editor")
                        }
                    })

                })
                
            </script>
            """
        )


@admin.register(Blog)
class BlogAdmin(ModelAdmin):
    
    inlines = [InlineBlogImgAdmin]

    search_fields = ['title']
    list_display = ['title', 'slug', 'datetime', 'draft']

    list_filter = ['datetime']

    readonly_fields = ['blog_id', 'datetime',  'id', ]

    autocomplete_fields = ['user']

    # formfield_overrides = {
    #     models.TextField: {
    #         "widget": WysiwygWidget,
    #     }
    # }

    # https://stackoverflow.com/questions/14832739/django-admin-how-to-display-widget-on-readonly-field
    
    class Media:
        css = {
             'all': (CSSAdminCode(),)
        }
        js = [
            JSReadonly(),
        ]

    def get_sub_title(self, obj):
        return obj.title[:60]

    get_sub_title.short_description = 'title'

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        
        if "body" in form.base_fields:
            # form.base_fields["body"].widget = TrixEditorWidget()
            # form.base_fields["body"].widget = WysiwygWidget()
            form.base_fields["body"].widget = UnfoldTrix()
            form.base_fields["body"].help_text = "To upload images and files you must save your blog first"
        
        return form


    def get_fieldsets(self, request, obj=None):

        fieldsets = [
            ('Details', {
          'fields': ('id', 'blog_id', 'title', 'slug', 'thumbnail','video_url')
            }),
            ('Body', {
                'fields': ('body', )
            }),
            ('Status', {
                'fields': ('draft', 'datetime')
            }),
        ]

        if obj and not self.has_change_permission(request, obj):
            fieldsets[1][1]['fields'] = ('get_body', )

        return fieldsets

    def get_body(self, obj):
        
        if not self.has_change_permission(self.request, obj) or not self.has_add_permission(self.request):
            return mark_safe(obj.body)
        
        return obj
    
    get_body.short_description = 'body'

    
    def changelist_view(self, request, extra_context=None):
        self.request = request
        return super().changelist_view(request, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.request = request
        return super().change_view(request, object_id, form_url, extra_context)
    


from django.contrib import admin
from .models import BlogInteraction

@admin.register(BlogInteraction)
class BlogInteractionAdmin(admin.ModelAdmin):
    list_display = ('blog', 'likes', 'dislikes', 'views')
    search_fields = ('blog__title',)
    list_filter = ('likes', 'dislikes', 'views')
    ordering = ('-likes',)




from django.contrib import admin
from .models import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'blog_interaction', 'user', 'text', 'created_at')  # Fields to display in the admin list view
    list_filter = ('created_at', 'user')  # Filters for the admin sidebar
    search_fields = ('text', 'user__username', 'blog_interaction__blog__title')  # Search fields
    ordering = ('-created_at',)  # Default ordering
    raw_id_fields = ('blog_interaction', 'user')  # Allows for raw ID input for ForeignKey fields



# blog/admin.py
from django.contrib import admin
from .models import TextBlogs

class TextBlogsAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'created_at', 'updated_at','published_date')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}  # Automatically generate the slug from the title

admin.site.register(TextBlogs, TextBlogsAdmin)


from django.contrib import admin
from .models import BlogUpload, BlogImage

class BlogImageInline(admin.TabularInline):  
    """ Allows managing related images directly from the BlogUpload admin. """
    model = BlogUpload.extracted_images.through  # ManyToManyField intermediary table
    extra = 1
    verbose_name = "Extracted Image"
    verbose_name_plural = "Extracted Images"

@admin.register(BlogUpload)
class BlogUploadAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at', 'has_file', 'num_extracted_images')
    search_fields = ('title',)
    list_filter = ('uploaded_at',)
    readonly_fields = ('uploaded_at', 'content',)  # Keep extracted content read-only
    inlines = [BlogImageInline]

    def has_file(self, obj):
        """ Check if a file was uploaded. """
        return bool(obj.uploaded_file)
    has_file.boolean = True
    has_file.short_description = "File Uploaded"

    def num_extracted_images(self, obj):
        """ Count the number of extracted images. """
        return obj.extracted_images.count()
    num_extracted_images.short_description = "Extracted Images"

# Register BlogImage separately if needed
@admin.register(BlogImage)
class BlogImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'image',)







