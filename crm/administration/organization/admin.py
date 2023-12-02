from django.contrib import admin
from django.contrib.auth.models import User
from django import forms
from .models import Organization

# admin.site.register(Organization)


# admin.site.register(Organization, OrganizationAdmin)
class OrganizationAdminForm(forms.ModelForm):
    class Meta:
        model = Organization
        exclude = []

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at')
    form = OrganizationAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Establecer el 'created_by' en el usuario actual al crear una nueva organización
        if db_field.name == 'created_by' and not kwargs.get('obj'):
            kwargs['initial'] = {'created_by': request.user.id}
            kwargs['queryset'] = User.objects.filter(
                id=request.user.id)  # Limitar opciones al usuario actual
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


