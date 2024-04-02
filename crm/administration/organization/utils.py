from django.utils.html import format_html
from django.urls import reverse
from django.template.defaulttags import register

def get_media_url(media):
    return reverse('organization:media-file', kwargs={'organization_slug': media.organization.slug, 'media_id': media.id})

@register.simple_tag
def media_url(media):
    return format_html('<img class="mb-4" src="{}" alt="{{ media.image.name }}" width="72" height="57">', get_media_url(media))
