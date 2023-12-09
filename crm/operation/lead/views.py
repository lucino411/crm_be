from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import FormView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Q


from configuration.country.models import Country
from administration.userprofile.models import Agent
from administration.organization.models import Organization
from .models import Lead
from .forms import LeadForm

''' 
/************
 LEAD LIST
/************
'''

class HomeLeadView(LoginRequiredMixin, TemplateView):
    template_name = 'operation/lead/lead_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Gestion de Leads'    
        organization_name = self.request.user.agent.organization.name
        context['organization_name'] = organization_name
        return context

# Query de Leads de la base de datos enviada a JS como JSON para las Datatables JS
class LeadListView(ListView):
    model = Lead

    def get_queryset(self):
        # Obten la organización del agente actualmente autenticado
        agent = Agent.objects.get(user=self.request.user)
        user_organization = agent.organization

        # Filtra los leads basados en la organización del agente
        return Lead.objects.filter(organization=user_organization)

    def get(self, request, *args, **kwargs):
        agent = Agent.objects.get(user=self.request.user)
        user_organization = agent.organization
        leads = self.get_queryset()
        leads_data = list(leads.values('id', 'first_name', 'last_name', 'primary_email',
                                       'country', 'created_time', 'last_modified_by_id', 'assigned_to_id', 'created_by_id', 'organization'))
        country_names = {
            country.id: country.name for country in Country.objects.all()
        }
        user_names = {
            user.id: f"{user.first_name} {user.last_name}" for user in User.objects.all()
        }
        for lead in leads_data:
            lead['country'] = country_names.get(lead['country'])
            lead['assigned_to'] = user_names.get(lead['assigned_to_id'])
            lead['last_modified_by'] = user_names.get(lead['last_modified_by_id'])
            lead['created_by'] = user_names.get(lead['created_by_id'])
            lead['organization'] = user_organization.name

        return JsonResponse({'leads': leads_data})
    
''' 
/************
CREATE LEAD
/************
'''
class LeadCreateView(LoginRequiredMixin, FormView):
    template_name = 'operation/lead/lead_create.html'
    form_class = LeadForm

    def test_func(self):
        return self.request.user.is_active

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        agent = self.request.user.agent

        if agent:
            # Filtrar las opciones del campo 'country' según la organización y la condición 'is_selected'
            form.fields['country'].queryset = Country.objects.filter(
                Q(organization=agent.organization) & Q(is_selected=True)
            )           
            form.fields['assigned_to'].queryset = User.objects.filter(
                agent__organization=agent.organization)  
        return form

    def form_valid(self, form):

        # Se verifica que el el email no este repetido, se va a usar en Company y Contact . No se usa en Leads ni Deals
        # agent = self.request.user.agent    
        # email = form.cleaned_data['primary_email']        
        # Verificar si existe un lead con el mismo email en la misma organización
        # if Lead.objects.filter(
        #     primary_email=email,
        #     organization=agent.organization
        # ).exists():
        #     messages.error(
        #         self.request, "A lead with this email already exists in your organization.")
        #     return render(self.request, self.template_name, {'form': form, 'organization_name': agent.organization})    
        # else:
        #     # Obtener la organización del agente que está creando el lead
        #     agent = self.request.user.agent    
        #     # Asignar la organización al lead
        #     form.instance.organization = agent.organization
        #     form.instance.created_by = agent.user
        #     form.instance.last_modified_by = agent.user
        #     # form.instance.assigned_to = agent.user
        #     form.save()

        #     messages.success(self.request, "Lead was created")
        #     return redirect('operation:lead-list', organization_name=agent.organization)

        # Asignar la organización al lead
        agent = self.request.user.agent    
        form.instance.organization = agent.organization
        form.instance.created_by = agent.user
        form.instance.last_modified_by = agent.user
        form.save()

        messages.success(self.request, "Lead was created")
        url = reverse('operation:lead-list', kwargs={'organization_name': agent.organization})
        return redirect(url)

    def form_invalid(self, form):
        messages.error(
            self.request, "Invalid form data. Please check the entries and try again.")
        return render(self.request, self.template_name, {'form': form})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)   
        agent = self.request.user.agent
        context['organization_name'] = agent.organization
        return context
    

''' 
/************
LEAD DETAIL
/************
'''
class LeadDetailView(LoginRequiredMixin, DetailView):
    model = Lead
    template_name = 'operation/lead/lead_detail.html'
    context_object_name = 'lead'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)   
        agent = self.request.user.agent
        context['organization_name'] = agent.organization
        return context
    
    ''' 
/************
LEAD UPDATE
/************
'''
class LeadUpdateView(LoginRequiredMixin, UpdateView):
    model = Lead
    template_name = 'operation/lead/lead_update.html'
    form_class = LeadForm

    def test_func(self):
        return self.request.user.is_active

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        agent = self.request.user.agent

        if agent:
            # Filtrar las opciones del campo 'country' según la organización y la condición 'is_selected'
            form.fields['country'].queryset = Country.objects.filter(
                Q(organization=agent.organization) & Q(is_selected=True)
            )           
            form.fields['assigned_to'].queryset = User.objects.filter(
                agent__organization=agent.organization)  
        return form

    def get_success_url(self):
        messages.success(self.request, "Lead updated.")
        agent = self.request.user.agent
        return reverse_lazy('operation:lead-list', kwargs={'organization_name': agent.organization})   

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)   
        agent = self.request.user.agent
        context['organization_name'] = agent.organization
        return context


class LeadDeleteView(LoginRequiredMixin, DeleteView):
    model = Lead
    template_name = 'operation/lead/lead_delete.html'
    context_object_name = 'lead'

    def get_success_url(self):
        messages.success(self.request, "Lead deleted.")
        agent = self.request.user.agent
        return reverse_lazy('operation:lead-list', kwargs={'organization_name': agent.organization})   

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agent = self.request.user.agent
        context['organization_name'] = agent.organization
        return context
