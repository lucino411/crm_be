from django.db import models
from django.contrib.auth.models import User

from configuration.country.models import Country
from administration.organization.models import Organization
from lead.models import Lead


def get_sentinel_user():
    user, created = User.objects.get_or_create(username="deleted")
    if created:
        user.set_unusable_password()
        user.save()
    return user

class Contact(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    TITLE_CHOICES = [
        ('ceo', 'CEO'),
        ('company_rep', 'Company Representative'),
        ('independent_professional', 'Independent Professional'),
        ('entrepreneur', 'Entrepreneur'),
        ('student', 'Student'),
    ]
    title = models.CharField(max_length=50, choices=TITLE_CHOICES)
    primary_email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    mobile_phone = models.CharField(max_length=20, blank=True)
    company_name = models.CharField(max_length=255)
    country = models.ForeignKey(
            Country, on_delete=models.SET_NULL, blank=False, null=True, limit_choices_to={'is_selected': True})
    created_by = models.ForeignKey(User, related_name='created_lead', on_delete=models.SET(get_sentinel_user))
    last_modified_by = models.ForeignKey(User, related_name='last_modified_lead', on_delete=models.SET(get_sentinel_user))
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    organization = models.ForeignKey(Organization, related_name='lead', on_delete=models.CASCADE)  
    erased = models.BooleanField(default=False)

    def __str__(self):
        return self.first_name + " " + self.last_name
