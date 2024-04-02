
from django import forms
from .models import OrganizationMedia
from django.core.exceptions import ValidationError


class OrganizationMediaForm(forms.ModelForm):
    class Meta:
        model = OrganizationMedia
        fields = ['image']

    def clean_image(self):
        image = self.cleaned_data.get('image', False)
        if image:
            if image.size > 1 * 1024 * 1024:  # 1MB limit
                raise ValidationError("El tamaño del archivo es demasiado grande (máximo 1MB).")
            self.instance.image_size = image.size
        return image
    
