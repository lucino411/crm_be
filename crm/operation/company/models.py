from django.db import models
from django.contrib.auth.models import User

from configuration.country.models import Country
from administration.organization.models import Organization


def get_sentinel_user():
    user, created = User.objects.get_or_create(username="deleted")
    if created:
        user.set_unusable_password()
        user.save()
    return user


class Company(models.Model):    
    company_name = models.CharField(max_length=255)
    company_email = models.EmailField(blank=False)
    company_phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    INDUSTRY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('non_profit', 'Non-Profit'),
    ]
    industry = models.CharField(max_length=20, choices=INDUSTRY_CHOICES)    
    created_by = models.ForeignKey(User, related_name='created_company', on_delete=models.SET(get_sentinel_user))
    last_modified_by = models.ForeignKey(User, related_name='last_modified_company', on_delete=models.SET(get_sentinel_user))
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)    
    organization = models.ForeignKey(Organization, related_name='organization_company', on_delete=models.CASCADE)      
    erased = models.BooleanField(default=False)

    def __str__(self):       
        return self.company_name  
    
    def save(self, *args, **kwargs):
        if self.website:
            if self.website.startswith('http://'):
                # Reemplazar http:// por https://
                self.website = 'https://' + self.website[len('http://'):]
            elif not self.website.startswith('https://'):
                # Añadir https:// si no comienza con http:// o https://
                self.website = 'https://' + self.website

        if self.website and not self.website.startswith('https://'):
            self.website = 'https://' + self.website
        super().save(*args, **kwargs)