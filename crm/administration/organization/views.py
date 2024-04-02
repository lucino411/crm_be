from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404


from administration.userprofile.views import OrganizerContextMixin, OrganizerRequiredMixin
from administration.organization.models import Organization, OrganizationMedia
from .forms import OrganizationMediaForm
  

class ImageUploadView(LoginRequiredMixin, OrganizerRequiredMixin, OrganizerContextMixin, FormView):
    template_name = 'administration/organization/upload_media.html'
    form_class = OrganizationMediaForm
    validation_error_handled = False
    # success_url = reverse_lazy('some-success-url')  # Cambia esto a tu URL de éxito

    def form_valid(self, form):
        organizer = self.request.user.organizer
        organization_media = form.save(commit=False)
        organization_media.organization = self.get_organization()
        organization_media.created_by = organizer.user
        organization_media.save()
        messages.success(self.request, "Imagen subida correctamente")
        return super().form_valid(form)

    def form_invalid(self, form):
        # Manejar lo que sucede cuando el formulario no es válido
        return super().form_invalid(form)
    
    def get_success_url(self):  
        return reverse_lazy('lead:list', kwargs={'organization_slug': self.get_organization().slug})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context.update({'organization_slug': self.get_organization()})
        context['titulo'] = 'Subir Imagen'
        return context


class MediaLibraryView(LoginRequiredMixin, OrganizerRequiredMixin, OrganizerContextMixin, ListView):
    model = OrganizationMedia
    template_name = 'administration/organization/media_library.html'
    context_object_name = 'media_list'

    def get_queryset(self):
        # organization_id = self.kwargs['organization_id']
        # print('organization_id  ', organization_id)
        organization_slug = self.kwargs['organization_slug']
        # organization = get_object_or_404(Organization, name=organization_slug)
        organization = get_object_or_404(Organization, slug=organization_slug)
        return OrganizationMedia.objects.filter(organization=organization)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context.update({'organization_slug': self.get_organization()})
        context['titulo'] = 'Media Library'
        return context
    











