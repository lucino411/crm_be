from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from administration.userprofile.views import AgentRequiredMixin, AgentContextMixin
from configuration.country.models import Country
from operation.client.models import Client

class HomeClientView(LoginRequiredMixin, TemplateView):
    template_name = 'operation/client/client_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Clients'
        return context

# Query de Clients de la base de datos enviada a JS como JSON para las Datatables JS
class ClientListView(ListView, AgentRequiredMixin, AgentContextMixin):
    model = Client

    def get_queryset(self):
        clients = Client.objects.filter(organization=self.get_organization())
        return clients

    def get(self, request, *args, **kwargs):
        clients = self.get_queryset()
        clients_data = list(clients.values('id', 'first_name', 'last_name', 'primary_email',
                                       'country', 'created_time', 'last_modified_by_id', 'organization'))
        country_names = {
            country.id: country.name for country in Country.objects.all()
        }
        user_names = {
            user.id: f"{user.first_name} {user.last_name}" for user in User.objects.all()
        }
        for client in clients_data:
            client['country'] = country_names.get(client['country'])
            client['last_modified_by'] = user_names.get(client['last_modified_by_id'])
            client['organization'] = self.get_organization().name

        return JsonResponse({'clients': clients_data})
    

class ClientDetailView(DetailView, AgentRequiredMixin, AgentContextMixin):
    model = Client
    template_name = 'operation/client/client_detail.html'
    context_object_name = 'client'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Detail Client'
        context['organization_name'] = self.get_organization()

        # Obtener el objeto Client actual
        client = self.get_object()
        # Obtener los leads relacionados
        client_deals = client.client_deals.all()  # Utiliza el related_name aquí
        # Agregar los leads al contexto
        context['client_deals'] = client_deals

        return context
