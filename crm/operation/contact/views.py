from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from administration.userprofile.views import AgentRequiredMixin, AgentContextMixin
from configuration.country.models import Country
from operation.lead.models import Lead
from operation.contact.models import Contact

class HomeContactView(LoginRequiredMixin, TemplateView):
    template_name = 'operation/contact/contact_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Contacts'
        return context

# Query de Contacts de la base de datos enviada a JS como JSON para las Datatables JS
class ContactListView(ListView, AgentRequiredMixin, AgentContextMixin):
    model = Contact

    def get_queryset(self):
        contacts = Contact.objects.filter(organization=self.get_organization())
        return contacts

    def get(self, request, *args, **kwargs):
        contacts = self.get_queryset()
        contacts_data = list(contacts.values('id', 'first_name', 'last_name', 'title', 'primary_email', 'phone',   'mobile_phone', 'country',
                                     'created_time', 'created_by', 'modified_time', 'last_modified_by_id', 'company__company_name', 'organization__slug'))
        country_names = {
            country.id: country.name for country in Country.objects.all()
        }
        user_names = {
            user.id: f"{user.first_name} {user.last_name}" for user in User.objects.all()
        }

        # Diccionario para convertir valores de title a su representación legible
        title_choices = dict(Contact.TITLE_CHOICES)
        for contact in contacts_data:
            contact['country'] = country_names.get(contact['country'])
            contact['last_modified_by'] = user_names.get(contact['last_modified_by_id'])
            contact['created_by'] = user_names.get(contact['created_by'])
            # Convertir stage de código a representación legible
            contact['title'] = title_choices.get(contact['title'], 'Unknown') # Ver más detalles en la nota de Obsidian: [[Notas en el Codigo]]
            # Obtener Leads relacionados
            leads = Lead.objects.filter(contact_id=contact['id']).values('id', 'lead_name')                
            contact['leads'] = list(leads)  # Cambia 'deal' a 'deals' para reflejar que puede hab

        return JsonResponse({'contacts': contacts_data})
    

class ContactDetailView(DetailView, AgentRequiredMixin, AgentContextMixin):
    model = Contact
    template_name = 'operation/contact/contact_detail.html'
    context_object_name = 'contact'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Detail Contact'

        # Obtener el objeto Contact actual
        contact = self.get_object()
        # Obtener los leads relacionados
        contact_leads = contact.contact_leads.all()  # Utiliza el related_name aquí
        # Agregar los leads al contexto
        context['contact_leads'] = contact_leads

        return context
