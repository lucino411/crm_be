from django.db import models
from django.contrib.auth.models import User

from configuration.country.models import Country
from administration.organization.models import Organization
from operation.company.models import Company


def get_sentinel_user():
    user, created = User.objects.get_or_create(username="deleted")
    if created:
        user.set_unusable_password()
        user.save()
    return user

class Contact(models.Model):
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
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, related_name='contacts_company')
    country = models.ForeignKey(
            Country, on_delete=models.SET_NULL, blank=False, null=True, limit_choices_to={'is_selected': True})
    created_by = models.ForeignKey(User, related_name='created_contact', on_delete=models.SET(get_sentinel_user))
    last_modified_by = models.ForeignKey(User, related_name='last_modified_contact', on_delete=models.SET(get_sentinel_user))
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    organization = models.ForeignKey(Organization, related_name='contact_organization', on_delete=models.CASCADE)  
    erased = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)

    def clean(self):
        super().clean()
        self.first_name = self.first_name.title()
        self.last_name = self.last_name.title()

    def __str__(self):
        return self.first_name + " " + self.last_name
