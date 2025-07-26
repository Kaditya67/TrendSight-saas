from django import template

register = template.Library()

@register.filter
def get_item(image_list, index):
    """Retrieve an image URL from a list using the sequence index."""
    try:
        img_index = int(index.split('_')[1])  # Extract number from "image_0"
        return image_list[img_index].image.url
    except (IndexError, ValueError):
        return ''
