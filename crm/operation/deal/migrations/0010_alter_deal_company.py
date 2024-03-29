# Generated by Django 4.2.6 on 2024-01-23 16:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0002_remove_company_country'),
        ('deal', '0009_rename_lead_source_deal_deal_source_deal_company_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deal',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='company_deals', to='company.company'),
        ),
    ]
