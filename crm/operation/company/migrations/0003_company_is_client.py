# Generated by Django 4.2.6 on 2024-01-30 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0002_remove_company_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='is_client',
            field=models.BooleanField(default=False),
        ),
    ]
