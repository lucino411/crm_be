# Generated by Django 4.2.6 on 2023-12-18 16:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0001_initial'),
        ('currency', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='currency',
            name='organization',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='organization.organization'),
            preserve_default=False,
        ),
    ]
