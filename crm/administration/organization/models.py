from django.db import models
from administration.userprofile.models import User

class Organization(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False)
    created_by = models.ForeignKey(
        User, related_name='created_organizations', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name
