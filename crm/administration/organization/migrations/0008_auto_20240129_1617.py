# Generated by Django 4.2.6 on 2024-01-29 16:17

from django.db import migrations
from django.utils.text import slugify

def generate_unique_slugs(apps, schema_editor):
    Organization = apps.get_model('organization', 'Organization')
    for organization in Organization.objects.all():
        base_slug = slugify(organization.name)
        slug = base_slug
        counter = 1
        while Organization.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        organization.slug = slug
        organization.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0007_organization_slug'),
    ]

    operations = [
        migrations.RunPython(generate_unique_slugs),
    ]
