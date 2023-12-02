from django.contrib import admin
from django.contrib.auth.models import User
from django import forms
from .models import Profile, Agent, Organizer


class AgentForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = ['user', 'organization', 'created_by']

    def __init__(self, *args, **kwargs):
        super(AgentForm, self).__init__(*args, **kwargs)
        # Filtra los usuarios excluyendo a los superusuarios
        self.fields['user'].queryset = User.objects.exclude(is_superuser=True)


class OrganizerForm(forms.ModelForm):
    class Meta:
        model = Organizer
        fields = ['user', 'organization', 'created_by']

    def __init__(self, *args, **kwargs):
        super(OrganizerForm, self).__init__(*args, **kwargs)
        # Filtra los usuarios excluyendo a los superusuarios
        self.fields['user'].queryset = User.objects.exclude(is_superuser=True)


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    form = AgentForm
    list_display = ('user', 'organization', 'created_by', 
                    'created_at')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Establecer el 'created_by' en el usuario actual al crear una nueva organización
        if db_field.name == 'created_by' and not kwargs.get('obj'):
            kwargs['initial'] = {'created_by': request.user.id}
            kwargs['queryset'] = User.objects.filter(
                id=request.user.id)  # Limitar opciones al usuario actual
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Organizer)
class OrganizerAdmin(admin.ModelAdmin):
    form = OrganizerForm
    list_display = ('user', 'organization', 'created_by', 'created_at')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Establecer el 'created_by' en el usuario actual al crear una nueva organización
        if db_field.name == 'created_by' and not kwargs.get('obj'):
            kwargs['initial'] = {'created_by': request.user.id}
            kwargs['queryset'] = User.objects.filter(
                id=request.user.id)  # Limitar opciones al usuario actual
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Profile)

