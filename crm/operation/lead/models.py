from django.db import models
from django.contrib.auth.models import User
from configuration.country.models import Country
from administration.organization.models import Organization
from configuration.stage.models import Stage

def get_sentinel_user():
    user, created = User.objects.get_or_create(username="deleted")
    if created:
        user.set_unusable_password()
        user.save()
    return user

class Lead(models.Model):
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=False)
    primary_email = models.EmailField(
        blank=False, help_text="Please use the following format: <em>YYYY-MM-DD</em>.")
    country = models.ForeignKey(
        Country, on_delete=models.SET_NULL, blank=False, null=True, limit_choices_to={'is_selected': True})
    assigned_to = models.ForeignKey(User, related_name='assigned_lead', on_delete=models.SET(get_sentinel_user))
    created_by = models.ForeignKey(User, related_name='created_lead', on_delete=models.SET(get_sentinel_user))
    last_modified_by = models.ForeignKey(User, related_name='last_modified_lead', on_delete=models.SET(get_sentinel_user))
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    organization = models.ForeignKey(
        Organization, related_name='lead', on_delete=models.CASCADE)
    stage = models.ForeignKey(Stage, related_name="lead", null=True, on_delete=models.SET_NULL)
    # is_closed = models.BooleanField(default=False)