from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from administration.userprofile.models import User

class Organization(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False)   
    created_by = models.ForeignKey(
        User, related_name='created_organizations', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('name',)

    def clean(self):
        super().clean()
        self.name = self.name.title()
        
    def __str__(self):
        return self.name

@receiver(pre_delete, sender=Organization)
def delete_related_profiles(sender, instance, **kwargs):
    organizer = instance.organizer
    agents = instance.agent.all()
    if organizer:
        organizer.delete()
    for agent in agents:
        agent.delete()
