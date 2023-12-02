from django.contrib import admin
from .models import Profile, Organization
from django import forms
from django.contrib.auth.models import User


# admin.site.register(Organization, OrganizationAdmin)
class OrganizationAdminForm(forms.ModelForm):
    class Meta:
        model = Organization
        exclude = []

    def __init__(self, *args, **kwargs):
        super(OrganizationAdminForm, self).__init__(*args, **kwargs)
        # Filtrar usuarios que sean is_organizer=True
        self.fields['owner'].queryset = User.objects.filter(
            profile__is_organizer=True)

        # Filtrar usuarios que sean is_agent=True para el campo 'members'
        self.fields['members'].queryset = self.fields['members'].queryset.filter(
            profile__is_agent=True)
        # members = forms.ModelMultipleChoiceField(
        # queryset=None,
        # widget=admin.widgets.FilteredSelectMultiple('Members', is_stacked=False)
    # )


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'owner')
    form = OrganizationAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Establecer el 'created_by' en el usuario actual al crear una nueva organización
        if db_field.name == 'created_by' and not kwargs.get('obj'):
            kwargs['initial'] = {'created_by': request.user.id}
            kwargs['queryset'] = User.objects.filter(
                id=request.user.id)  # Limitar opciones al usuario actual
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # def formfield_for_manytomany(self, db_field, request, **kwargs):
    #     # Deshabilitar la edición del campo 'members' en el formulario
    #     if db_field.name == 'members' and kwargs.get('obj'):
    #         kwargs['queryset'] = kwargs['obj'].members.all()
    #     return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        # Guardar el 'created_by' con el usuario actual al crear una nueva organización
        if not change and not obj.created_by:
            obj.created_by = request.user

        # Guardar la organización
        obj.save()

        # Guardar el 'owner' en la tabla intermedia 'organization_members'
        obj.members.add(obj.owner)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_organizer', 'is_agent')
