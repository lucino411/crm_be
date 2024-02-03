# Pasar Organization slug y Organization id a todas las plantillas
def organization_details(request):
    context = {}
    user = request.user

    if user.is_authenticated:
        if hasattr(user, 'organizer') and user.organizer:
            organization = user.organizer.organization
        elif hasattr(user, 'agent') and user.agent:
            organization = user.agent.organization
        else:
            organization = None

        if organization:
            context['organization_slug'] = organization.slug
            context['organization_id'] = organization.id
            context['organization_name'] = organization.name  # Agregar el nombre de la organización al contexto
            
    return context
