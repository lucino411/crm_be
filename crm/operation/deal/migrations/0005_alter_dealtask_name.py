# Generated by Django 4.2.6 on 2024-01-08 23:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deal', '0004_alter_dealtask_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dealtask',
            name='name',
            field=models.CharField(max_length=200),
        ),
    ]
