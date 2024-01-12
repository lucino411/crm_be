from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from administration.userprofile.views import AgentRequiredMixin, AgentContextMixin
from configuration.country.models import Country
from operation.contact.models import Contact

class HomeContactView(LoginRequiredMixin, TemplateView):
    template_name = 'operation/contact/contact_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Gestion de Contacts'
        return context

# Query de Contacts de la base de datos enviada a JS como JSON para las Datatables JS
class ContactListView(ListView, AgentRequiredMixin, AgentContextMixin):
    model = Contact

    def get_queryset(self):
        contacts = Contact.objects.filter(organization=self.get_organization())
        return contacts

    def get(self, request, *args, **kwargs):
        contacts = self.get_queryset()
        contacts_data = list(contacts.values('id', 'first_name', 'last_name', 'primary_email',
                                       'country', 'created_time', 'last_modified_by_id', 'organization', 'is_client'))
        country_names = {
            country.id: country.name for country in Country.objects.all()
        }
        user_names = {
            user.id: f"{user.first_name} {user.last_name}" for user in User.objects.all()
        }
        for contact in contacts_data:
            contact['country'] = country_names.get(contact['country'])
            contact['last_modified_by'] = user_names.get(contact['last_modified_by_id'])
            contact['organization'] = self.get_organization().name

        return JsonResponse({'contacts': contacts_data})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization_name'] = self.get_organization().name
        return context
    

class ContactDetailView(DetailView, AgentRequiredMixin, AgentContextMixin):
    model = Contact
    template_name = 'operation/contact/contact_detail.html'
    context_object_name = 'contact'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Detail Contact'
        context['organization_name'] = self.get_organization()

        # Obtener el objeto Contact actual
        contact = self.get_object()
        # Obtener los leads relacionados
        contact_leads = contact.contact_leads.all()  # Utiliza el related_name aquí
        # Agregar los leads al contexto
        context['contact_leads'] = contact_leads

        return context
