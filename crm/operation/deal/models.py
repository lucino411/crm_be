from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import MaxLengthValidator

from configuration.country.models import Country
from administration.organization.models import Organization
from configuration.currency.models import Currency
from configuration.product.models import Product
from operation.client.models import Client



def get_sentinel_user():
    user, created = User.objects.get_or_create(username="deleted")
    if created:
        user.set_unusable_password()
        user.save()
    return user


class Deal(models.Model):
    deal_name = models.CharField(max_length=100, unique=True, blank=False, null=True)
     # Campo para relacionar el Client con el Deal
    client = models.ForeignKey(
        Client, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='client_deals'  # Permite acceder a los deals dede Client
    )

    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=False)

    TITLE_CHOICES = [
        ('ceo', 'CEO'),
        ('company_rep', 'Company Representative'),
        ('independent_professional', 'Independent Professional'),
        ('entrepreneur', 'Entrepreneur'),
        ('student', 'Student'),
    ]
    title = models.CharField(max_length=50, choices=TITLE_CHOICES)
    primary_email = models.EmailField(blank=False)
    phone = models.CharField(max_length=20, blank=True)
    mobile_phone = models.CharField(max_length=20, blank=True)
    company_name = models.CharField(max_length=255)
    INDUSTRY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('non_profit', 'Non-Profit'),
    ]
    industry = models.CharField(max_length=20, choices=INDUSTRY_CHOICES)
    website = models.URLField(blank=True)
    country = models.ForeignKey(
        Country, on_delete=models.SET_NULL, blank=False, null=True, limit_choices_to={'is_selected': True})
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    
    LEAD_SOURCE_CHOICES = [
        ('website', 'Website'),
        ('whatsapp', 'Whatsapp'),
        ('direct_mail', 'Direct Mail'),
        ('phone_call', 'Phone Call'),
        ('in_person', 'In Person'),
        ('social_media', 'Social Media'),
    ]
    lead_source = models.CharField(max_length=50, choices=LEAD_SOURCE_CHOICES)
    assigned_to = models.ForeignKey(User, related_name='assigned_deal', on_delete=models.SET(get_sentinel_user))
    created_by = models.ForeignKey(User, related_name='created_deal', on_delete=models.SET(get_sentinel_user))
    last_modified_by = models.ForeignKey(User, related_name='last_modified_deal', on_delete=models.SET(get_sentinel_user))
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    start_date_time = models.DateTimeField(null=True, blank=True, help_text="Please use the following format: <em>YYYY-MM-DD</em>.")
    end_date_time = models.DateTimeField(null=True, blank=True, help_text="Please use the following format: <em>YYYY-MM-DD</em>.")
    extended_end_date_time = models.DateTimeField(null=True, blank=True, help_text="Please use the following format: <em>YYYY-MM-DD</em>.")    
    actual_completion_date = models.DateTimeField(null=True, blank=True)
    description = models.TextField(validators=[MaxLengthValidator(280)])
    organization = models.ForeignKey(Organization, related_name='deal', on_delete=models.CASCADE)    
    
    STAGE_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('dorman', 'Dorman'),
        ('close_win', 'Close Win'),
        ('close_lost', 'Close Lost'),
    ]
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='new')
    is_closed = models.BooleanField(default=False)  
    erased = models.BooleanField(default=False)

    def __str__(self):
        return self.deal_name


class DealProduct(models.Model):
    deal = models.ForeignKey(
        Deal, related_name='deal_product', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='deal_product', on_delete=models.CASCADE)
    cotizacion_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.product.name


class DealTask(models.Model):
    name = models.CharField(max_length=200, blank=False)
    deal = models.ForeignKey('Deal', related_name='deal_dealtask', on_delete=models.CASCADE, null=True, blank=True)
    deal_product = models.ForeignKey('DealProduct', related_name='product_dealtask', on_delete=models.CASCADE, null=True, blank=True)
    parent_task = models.ForeignKey('self', null=True, blank=True, related_name='parent_dealtask', on_delete=models.CASCADE)
    description = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_dealtask', on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='assigned_dealtask', on_delete=models.CASCADE)
    last_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='modified_dealtask', on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, related_name='organization_dealtask', on_delete=models.CASCADE)
    STAGE_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]   
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='pending')    
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return self.name