# Generated by Django 4.2.6 on 2024-01-15 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0003_contact_is_client'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='website',
            field=models.URLField(blank=True),
        ),
    ]
