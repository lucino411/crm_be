# Generated by Django 4.2.6 on 2023-12-24 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lead', '0008_rename_last_modified_time_task_modified_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lead',
            name='start_date_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='start_date_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
