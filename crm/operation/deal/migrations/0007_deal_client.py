# Generated by Django 4.2.6 on 2024-01-12 19:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0001_initial'),
        ('deal', '0006_deal_company_name_deal_description_deal_erased_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='deal',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='client_leads', to='client.client'),
        ),
    ]
