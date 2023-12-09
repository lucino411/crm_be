# Generated by Django 4.2.6 on 2023-12-07 22:58

from django.db import migrations, models
import operation.lead.models


class Migration(migrations.Migration):

    dependencies = [
        ('country', '0001_initial'),
        ('lead', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='country',
            field=models.ForeignKey(default=1, limit_choices_to={'is_selected': True}, on_delete=models.SET(operation.lead.models.get_sentinel_user), to='country.country'),
            preserve_default=False,
        ),
    ]
