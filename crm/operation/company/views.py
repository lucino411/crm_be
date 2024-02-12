from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib.auth.models import User


from administration.userprofile.views import AgentRequiredMixin, AgentContextMixin
from operation.deal.models import Deal
from operation.company.models import Company
from operation.client.models import Client


class CompanyHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'operation/company/company_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Gestion de Companies'
        return context


# Query de Companies de la BD enviada a JS como JSON para Datatables JS
class CompanyListView(ListView, AgentRequiredMixin, AgentContextMixin):
    model = Company

    def get_queryset(self):
        return Company.objects.filter(is_client=True, organization=self.get_organization())
    
    def get(self, request, *args, **kwargs):
        companies = self.get_queryset()
        companies_data = list(companies.values('id', 'company_name', 'company_email', 'company_phone', 'website', 'industry', 'last_modified_by_id',
                          'organization', 'created_time', 'created_by', 'modified_time', 'created_by_id', 'is_client', 'organization__slug'))
        
        user_names = {
            user.id: f"{user.first_name} {user.last_name}" for user in User.objects.all()
        }

        # Diccionario para convertir valores de industry a su representación legible
        industry_choices = dict(Company.INDUSTRY_CHOICES)

        for company in companies_data:
            company['created_by'] = user_names.get(company['created_by_id'])
            company['last_modified_by'] = user_names.get(company['last_modified_by_id'])
            company['organization'] = self.get_organization().name
            # Convertir industry de código a representación legible
            company['industry'] = industry_choices.get(company['industry'], 'Unknown') # Ver más detalles en la nota de Obsidian: [[Notas en el Codigo]]
            # Obtener Deals relacionados correctamente
            deals = Deal.objects.filter(company_id=company['id']).values('id', 'deal_name')                
            company['deals'] = list(deals)  # Cambia 'deal' a 'deals' para reflejar que puede haber múltiples
            # Obtener Clients relacionados correctamente
            clients = Client.objects.filter(company_id=company['id']).values('id', 'primary_email', 'first_name', 'last_name')                
            company['clients'] = list(clients)  # Cambia 'deal' a 'deals' para reflejar que puede haber múltiples

        return JsonResponse({'companies': companies_data})
    

class CompanyDetailView(DetailView, AgentRequiredMixin, AgentContextMixin):
    model = Company
    template_name = 'operation/company/company_detail.html'
    context_object_name = 'company'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.get_object()
        client = self.get_object()
        context['titulo'] = 'Detail Company'
        # Obtener los Deals asociados con esta Company
        context['deals'] = Deal.objects.filter(company=company)
        # Obtener los Clients asociados con esta Company
        context['clients'] = Client.objects.filter(company=company)

        return context