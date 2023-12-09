from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from administration.organization.models import Organization

class Organizer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.OneToOneField(
        Organization, null=True, on_delete=models.SET_NULL,  related_name='organizer', error_messages={
            'unique_together': "Este usuario ya es organizer de otra organización.",
        })
    created_by = models.ForeignKey(
        User, related_name='created_organizer', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ('user',)

    def __str__(self):
        return self.user.username


class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(
        Organization,
        null=True,
        on_delete=models.SET_NULL,
        related_name='agent',
        error_messages={
            'unique_together': "Este usuario ya es agente de otra organización.",
        }
    )
    created_by = models.ForeignKey(
        User, related_name='created_agent', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ('user',)

    def __str__(self):
        return self.user.username

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, null=True)

# Guarda en Profile al User creado
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    Profile.objects.get_or_create(user=instance)