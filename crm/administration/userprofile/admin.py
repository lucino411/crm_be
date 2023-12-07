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

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        organization = cleaned_data.get('organization')
         # Verifica si el usuario ya es organizer en alguna organización
        organizer = Organizer.objects.filter(user=user).first()
        if organizer:
            # Obtén la organización del organizer
            organizer_organization = organizer.organization
            if organizer:
                # Obtén la organización del organizer
                organizer_organization = organizer.organization
                # Verifica si la organización es diferente a la proporcionada
                if organizer_organization and organizer_organization != organization:
                    raise forms.ValidationError(
                        'Este usuario ya es un Organizer en otra organización y no puede ser un Agente en esta.')                     

        # Verifica si el usuario ya es un agente en otra organización
        if Agent.objects.filter(user=user).exclude(organization=organization).exists():
            raise forms.ValidationError('Este usuario ya es un Agente en otra organización.')

        return cleaned_data


class OrganizerForm(forms.ModelForm):
    class Meta:
        model = Organizer
        fields = ['user', 'organization', 'created_by']

    def __init__(self, *args, **kwargs):
        super(OrganizerForm, self).__init__(*args, **kwargs)
        # Filtra los usuarios excluyendo a los superusuarios
        self.fields['user'].queryset = User.objects.exclude(is_superuser=True)

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        organization = cleaned_data.get('organization')
        # Verifica si el usuario ya es organizer en alguna organización
        agent = Agent.objects.filter(user=user).first()
        if agent:
            # Obtén la organización del organizer
            agent_organization = agent.organization
            if agent:
                # Obtén la organización del organizer
                agent_organization = agent.organization
                # Verifica si la organización es diferente a la proporcionada
                if agent_organization and agent_organization != organization:
                    raise forms.ValidationError(
                        'Este usuario ya es un Agent en otra organización y no puede ser un Organizer en esta.')

        # Verifica si el usuario ya es un agente en otra organización
        if Organizer.objects.filter(user=user).exclude(organization=organization).exists():
            raise forms.ValidationError(
                'Este usuario ya es un Organizer en otra organización.')

        return cleaned_data

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
