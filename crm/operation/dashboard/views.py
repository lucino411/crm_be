from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from administration.organization.models import Organization, OrganizationMedia

@login_required
def dashboard(request, organization_slug=None):
    context = {'title': 'Dashboard'}
        # Obtén todas las imágenes de la biblioteca de medios
    media_list = OrganizationMedia.objects.all()
    # Pasa las URLs de las imágenes al contexto
    context = {'media_urls': [media.image.url for media in media_list]}
    return render(request, 'operation/dashboard/dashboard_home.html', context)


from django.shortcuts import render
from .forms import ImageSelectionForm

def select_image_view(request):
    if request.method == 'POST':
        form = ImageSelectionForm(request.POST)
        if form.is_valid():
            selected_image = form.cleaned_data['image']
            # Realiza cualquier acción necesaria con la imagen seleccionada
            # Por ejemplo, puedes mostrarla en otra parte de la aplicación o guardar su URL en la base de datos
            return render(request, 'otra_plantilla.html', {'selected_image': selected_image})
    else:
        form = ImageSelectionForm()
    
    return render(request, 'tu_plantilla.html', {'form': form})