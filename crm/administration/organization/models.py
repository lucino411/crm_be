from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from administration.userprofile.models import User

def get_sentinel_user():
    user, created = User.objects.get_or_create(username="deleted")
    if created:
        user.set_unusable_password()
        user.save()
    return user

class Organization(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False)   
    created_by = models.ForeignKey(
        User, related_name='created_organizations', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('name',)

    #  Para que el nombre de la organización esté en formato de título.
    def clean(self):
        super().clean()
        self.name = self.name.title()

    def __str__(self):
        return self.name

@receiver(pre_delete, sender=Organization)
def delete_related_profiles(sender, instance, **kwargs):
    organizer = getattr(instance, 'organizer', None)
    agents = instance.agent.all()
    if organizer:
        organizer.delete()
    for agent in agents:
        agent.delete()


def organization_directory_path(instance, filename):
    # Archivo se guardará en MEDIA_ROOT/organizations/<id>/<filename>
    return f'organizations/{instance.organization.id}/{filename}'
    # return f'organizations/{instance.organization.}/{filename}'

class OrganizationMedia(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=organization_directory_path, height_field='image_height', width_field='image_width')
    image_height = models.PositiveIntegerField(editable=False, null=True)
    image_width = models.PositiveIntegerField(editable=False, null=True)
    image_size = models.PositiveIntegerField(editable=False, null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='created_media', on_delete=models.SET(get_sentinel_user))

    def __str__(self):
        return f"{self.organization.name} Media"