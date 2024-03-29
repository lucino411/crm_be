# Generated by Django 4.2.6 on 2024-01-10 22:35

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lead', '0016_alter_leadtask_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='company_name',
            field=models.CharField(default='Desconocido company', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lead',
            name='description',
            field=models.TextField(default='Desconocido company', validators=[django.core.validators.MaxLengthValidator(280)]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lead',
            name='erased',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='lead',
            name='industry',
            field=models.CharField(choices=[('public', 'Public'), ('private', 'Private'), ('non_profit', 'Non-Profit')], default='Public', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lead',
            name='lead_source',
            field=models.CharField(choices=[('website', 'Website'), ('whatsapp', 'Whatsapp'), ('direct_mail', 'Direct Mail'), ('phone_call', 'Phone Call'), ('in_person', 'In Person'), ('social_media', 'Social Media')], default='website', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lead',
            name='mobile_phone',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='lead',
            name='phone',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='lead',
            name='title',
            field=models.CharField(choices=[('ceo', 'CEO'), ('company_rep', 'Company Representative'), ('independent_professional', 'Independent Professional'), ('entrepreneur', 'Entrepreneur'), ('student', 'Student')], default='ceo', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lead',
            name='website',
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name='lead',
            name='end_date_time',
            field=models.DateTimeField(blank=True, help_text='Please use the following format: <em>YYYY-MM-DD</em>.', null=True),
        ),
        migrations.AlterField(
            model_name='lead',
            name='extended_end_date_time',
            field=models.DateTimeField(blank=True, help_text='Please use the following format: <em>YYYY-MM-DD</em>.', null=True),
        ),
        migrations.AlterField(
            model_name='lead',
            name='primary_email',
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name='lead',
            name='start_date_time',
            field=models.DateTimeField(blank=True, help_text='Please use the following format: <em>YYYY-MM-DD</em>.', null=True),
        ),
    ]
