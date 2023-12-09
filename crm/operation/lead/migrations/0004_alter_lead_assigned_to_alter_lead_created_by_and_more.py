# Generated by Django 4.2.6 on 2023-12-08 16:17

from django.conf import settings
from django.db import migrations, models
import operation.lead.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lead', '0003_lead_first_name_lead_last_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lead',
            name='assigned_to',
            field=models.ForeignKey(on_delete=models.SET(operation.lead.models.get_sentinel_user), related_name='assigned_lead', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='lead',
            name='created_by',
            field=models.ForeignKey(on_delete=models.SET(operation.lead.models.get_sentinel_user), related_name='created_lead', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='lead',
            name='last_modified_by',
            field=models.ForeignKey(on_delete=models.SET(operation.lead.models.get_sentinel_user), related_name='last_modified_lead', to=settings.AUTH_USER_MODEL),
        ),
    ]
