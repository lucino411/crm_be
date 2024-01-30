from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.core.validators import RegexValidator
from django.utils.text import slugify


from administration.userprofile.models import User

def get_sentinel_user():
    user, created = User.objects.get_or_create(username="deleted")
    if created:
        user.set_unusable_password()
        user.save()
    return user

class Organization(models.Model):
    name = models.CharField(max_length=100, unique=True, validators=[
        RegexValidator(
            regex='^[a-zA-Z0-9 ]*$',  # Permite letras, números y espacios
            message='El nombre solo puede contener letras, números y espacios.'
        )
    ])
    slug = models.SlugField(unique=True, blank=True)  # Campo slug añadido
    created_by = models.ForeignKey(
        User, related_name='created_organizations', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    # Convierte el nombre a slug antes de guardar
    def save(self, *args, **kwargs):
        # Genera el slug a partir del nombre si no existe
        if not self.slug:
            self.slug = slugify(self.name)
        super(Organization, self).save(*args, **kwargs)

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


# Archivo se guardará en MEDIA_ROOT/organizations/<id>/<filename>
def organization_directory_path(instance, filename):
    return f'organizations/{instance.organization.id}/{filename}'

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