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
                          'organization', 'modified_time', 'created_by_id', 'is_client'))
        
        user_names = {
            user.id: f"{user.first_name} {user.last_name}" for user in User.objects.all()
        }

        for company in companies_data:
            company['created_by'] = user_names.get(company['created_by_id'])
            company['last_modified_by'] = user_names.get(company['last_modified_by_id'])
            company['organization'] = self.get_organization().name

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


        # context['organization_name'] = self.get_organization()
        # # Obtener el objeto Contact actual
        # contact = self.get_object()
        # # Obtener los leads relacionados
        # contact_leads = contact.contact_leads.all()  # Utiliza el related_name aquí
        # # Agregar los leads al contexto
        # context['contact_leads'] = contact_leads

        return context