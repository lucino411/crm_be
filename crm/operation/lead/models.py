from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from configuration.country.models import Country
from administration.organization.models import Organization
from configuration.currency.models import Currency
from configuration.product.models import Product


def get_sentinel_user():
    user, created = User.objects.get_or_create(username="deleted")
    if created:
        user.set_unusable_password()
        user.save()
    return user


class Lead(models.Model):
    STAGE_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('dorman', 'Dorman'),
        ('close_win', 'Close Win'),
        ('close_lost', 'Close Lost'),
    ]

    lead_name = models.CharField(max_length=100, unique=True, blank=False, null=True)
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=False)
    primary_email = models.EmailField(blank=False)
    country = models.ForeignKey(
        Country, on_delete=models.SET_NULL, blank=False, null=True, limit_choices_to={'is_selected': True})
    assigned_to = models.ForeignKey(User, related_name='assigned_lead', on_delete=models.SET(get_sentinel_user))
    created_by = models.ForeignKey(User, related_name='created_lead', on_delete=models.SET(get_sentinel_user))
    last_modified_by = models.ForeignKey(User, related_name='last_modified_lead', on_delete=models.SET(get_sentinel_user))
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    start_date_time = models.DateTimeField(null=True, blank=True, help_text="Please use the following format: <em>YYYY-MM-DD</em>.")
    end_date_time = models.DateTimeField(null=True, blank=True, help_text="Please use the following format: <em>YYYY-MM-DD</em>.")
    extended_end_date_time = models.DateTimeField(null=True, blank=True, help_text="Please use the following format: <em>YYYY-MM-DD</em>.")    
    actual_completion_date = models.DateTimeField(null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    organization = models.ForeignKey(Organization, related_name='lead', on_delete=models.CASCADE)    
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='new')
    is_closed = models.BooleanField(default=False)  

    def __str__(self):
        return self.lead_name


class LeadProduct(models.Model):
    lead = models.ForeignKey(
        Lead, related_name='lead_product', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='lead_product', on_delete=models.CASCADE)
    cotizacion_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.product.name


class LeadTask(models.Model):
    STAGE_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]

    name = models.CharField(max_length=200, blank=False)
    lead = models.ForeignKey('Lead', related_name='lead_leadtask', on_delete=models.CASCADE, null=True, blank=True)
    lead_product = models.ForeignKey('LeadProduct', related_name='product_leadtask', on_delete=models.CASCADE, null=True, blank=True)
    parent_task = models.ForeignKey('self', null=True, blank=True, related_name='parent_leadtask', on_delete=models.CASCADE)
    description = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_leadtask', on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='assigned_leadtask', on_delete=models.CASCADE)
    last_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='modified_leadtask', on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, related_name='organization_leadtask', on_delete=models.CASCADE)    
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='pending')    
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return self.name