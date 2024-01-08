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


class Deal(models.Model):
    STAGE_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('dorman', 'Dorman'),
        ('close_win', 'Close Win'),
        ('close_lost', 'Close Lost'),
    ]

    deal_name = models.CharField(max_length=100, unique=True, blank=False, null=True)
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=False)
    primary_email = models.EmailField(
        blank=False, help_text="Please use the following format: <em>YYYY-MM-DD</em>.")
    country = models.ForeignKey(
        Country, on_delete=models.SET_NULL, blank=False, null=True, limit_choices_to={'is_selected': True})
    assigned_to = models.ForeignKey(User, related_name='assigned_deal', on_delete=models.SET(get_sentinel_user))
    created_by = models.ForeignKey(User, related_name='created_deal', on_delete=models.SET(get_sentinel_user))
    last_modified_by = models.ForeignKey(User, related_name='last_modified_deal', on_delete=models.SET(get_sentinel_user))
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    start_date_time = models.DateTimeField(null=True, blank=True)
    end_date_time = models.DateTimeField(null=True, blank=True)
    extended_end_date_time = models.DateTimeField(null=True, blank=True)    
    actual_completion_date = models.DateTimeField(null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    organization = models.ForeignKey(Organization, related_name='deal', on_delete=models.CASCADE)    
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='new')
    is_closed = models.BooleanField(default=False)  

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
    STAGE_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]

    name = models.CharField(max_length=200, blank=False, unique=True)
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
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='pending')    
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return self.name