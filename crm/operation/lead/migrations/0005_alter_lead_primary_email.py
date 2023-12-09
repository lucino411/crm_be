# Generated by Django 4.2.6 on 2023-12-08 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lead', '0004_alter_lead_assigned_to_alter_lead_created_by_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lead',
            name='primary_email',
            field=models.EmailField(help_text='Please use the following format: <em>YYYY-MM-DD</em>.', max_length=254),
        ),
    ]
