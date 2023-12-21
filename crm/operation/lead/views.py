from django.views.generic import TemplateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.views.generic.edit import FormView
from django import forms
from django.db.models import Q
from django.utils import timezone
from django.forms import inlineformset_factory


from configuration.country.models import Country
from .models import Lead, LeadProduct
from .forms import LeadForm, LeadProductForm
from administration.userprofile.views import AgentRequiredMixin, AgentContextMixin


LeadProductFormset = inlineformset_factory(
    Lead, LeadProduct, form=LeadProductForm, extra=0, can_delete=True)


class HomeLeadView(LoginRequiredMixin, TemplateView):
    template_name = 'operation/lead/lead_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Gestion de Leads'    
        return context 


# Query de Leads de la base de datos enviada a JS como JSON para las Datatables JS
class LeadListView(ListView, AgentRequiredMixin, AgentContextMixin):
    model = Lead

    def get_queryset(self):
        leads = Lead.objects.filter(organization=self.get_organization())
        return leads

    def get(self, request, *args, **kwargs):
        leads = self.get_queryset()
        leads_data = list(leads.values('id', 'lead_name', 'first_name', 'last_name', 'primary_email',
                                       'country', 'created_time', 'last_modified_by_id', 'assigned_to_id', 'organization'))
        country_names = {
            country.id: country.name for country in Country.objects.all()
        }
        user_names = {
            user.id: f"{user.first_name} {user.last_name}" for user in User.objects.all()
        }
        for lead in leads_data:
            lead['country'] = country_names.get(lead['country'])
            lead['assigned_to'] = user_names.get(lead['assigned_to_id'])
            lead['last_modified_by'] = user_names.get(
                lead['last_modified_by_id'])
            # lead['created_by'] = user_names.get(lead['created_by_id'])
            lead['organization'] = self.get_organization().name

        return JsonResponse({'leads': leads_data})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization_name'] = self.get_organization().name
        return context
    

class LeadDetailView(DetailView, AgentRequiredMixin, AgentContextMixin):
    model = Lead
    template_name = 'operation/lead/lead_detail.html'
    context_object_name = 'lead'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Detail Lead'
        context['organization_name'] = self.get_organization()
        # Añadir productos asociados al Lead
        lead_products = LeadProduct.objects.filter(lead=self.object)
        context['lead_products'] = lead_products

        return context


class LeadCreateView(LoginRequiredMixin, FormView, AgentRequiredMixin, AgentContextMixin):
    template_name = 'operation/lead/lead_create.html'
    form_class = LeadForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        agent = self.request.user.agent

        if agent:             
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

        agent = self.request.user.agent
        form.instance.organization = agent.organization
        form.instance.created_by = agent.user
        form.instance.last_modified_by = agent.user

        self.object = form.save()

        formset = LeadProductFormset(
            self.request.POST, self.request.FILES, instance=self.object)
        if formset.is_valid():
            formset.save()
        else:
            return self.render_to_response(self.get_context_data(form=form))

        messages.success(self.request, "Lead was created")
        url = reverse('lead:list', kwargs={
                      'organization_name': agent.organization})
        return redirect(url)

    def form_invalid(self, form):
        print(form.errors)
        messages.error(
            self.request, "Invalid form data. Please check the entries and try again.")
        return render(self.request, self.template_name, {'form': form})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Create Lead'    
        context['organization_name'] = self.get_organization()
        if self.request.POST:
            context['formset'] = LeadProductFormset(self.request.POST)
        else:
            context['formset'] = LeadProductFormset()

        return context

    
class LeadUpdateView(UpdateView, AgentRequiredMixin, AgentContextMixin):
    model = Lead
    template_name = 'operation/lead/lead_update.html'
    form_class = LeadForm
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        agent = self.request.user.agent      

        if agent:
            # Configuración de queryset para los campos que dependen del agente
            form.fields['country'].queryset = Country.objects.filter(
                Q(organization=agent.organization) & Q(is_selected=True)
            )
            form.fields['assigned_to'].queryset = User.objects.filter(
                agent__organization=agent.organization)            
       
        # Obtener la instancia del lead
        lead = self.get_object()

        # Lógica para deshabilitar el formulario si el lead está en "Close Win" o "Close Lost"
        if lead.stage in ['close_win', 'close_lost']:
            for field in form.fields:
                form.fields[field].disabled = True
            return form

        current_time = timezone.now()
        # Lógica para habilitar/deshabilitar campos en función de las fechas y el estado del lead
        if lead.end_date_time and lead.end_date_time < current_time:
            form.fields['end_date_time'].disabled = True
            form.fields['extended_end_date_time'].disabled = False
        elif lead.end_date_time and lead.end_date_time > current_time:
            form.fields['end_date_time'].disabled = False
            form.fields['extended_end_date_time'].disabled = True

        # Deshabilitar todos los campos si el lead está cerrado, excepto extended_end_date_time
        if lead.is_closed:
            for field in form.fields:
                if field != 'extended_end_date_time':
                    form.fields[field].disabled = True

        return form

    def form_valid(self, form):
        agent = self.request.user.agent
        form.instance.organization = agent.organization
        form.instance.last_modified_by = agent.user

        lead = form.save(commit=False)

        # Establecer is_closed en True si el stage es "Close Win" o "Close Lost"
        if lead.stage in ['close_win', 'close_lost']:
            lead.is_closed = True
            print(lead.stage)
            print(lead.is_closed)
        else:
            # Actualizar is_closed basado en end_date_time y extended_end_date_time
            current_time = timezone.now()
            if lead.end_date_time and lead.end_date_time > current_time:
                lead.is_closed = False
                # Si end_date_time es futuro, ocultar extended_end_date_time
                form.fields['extended_end_date_time'].widget = forms.HiddenInput()
            elif lead.extended_end_date_time and lead.extended_end_date_time > current_time:
                lead.is_closed = False
            else:
                lead.is_closed = True

        lead.save()

        # Guardar los formularios de LeadProduct
        formset = LeadProductFormset(
            self.request.POST, self.request.FILES, instance=lead)
        
        if formset.is_valid():
            formset.save()

        messages.success(self.request, "Lead actualizado")
        url = reverse('lead:detail', kwargs={
                      'organization_name': self.get_organization(), 'pk': self.object.pk})
        return redirect(url)      

    def form_invalid(self, form):    
        print(form.errors)
        messages.error(
            self.request, "Invalid form data. Please check the entries and try again.")
        return render(self.request, self.template_name, {
            'form': form,
            'organization_name': self.get_organization(),
            'pk': self.object.pk
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Update Lead'
        context['organization_name'] = self.get_organization()

        # Obtener la instancia del lead
        lead = self.get_object()

        # Configurar el formset
        if self.request.POST:
            context['formset'] = LeadProductFormset(
                self.request.POST, instance=lead)
        else:
            context['formset'] = LeadProductFormset(instance=lead)

        # Deshabilitar los campos del formset si el lead está cerrado
        if lead.is_closed:
            for form in context['formset']:
                for field in form.fields:
                    form.fields[field].disabled = True

        return context




class LeadDeleteView(DeleteView, AgentRequiredMixin, AgentContextMixin):
    model = Lead
    template_name = 'operation/lead/lead_delete.html'
    context_object_name = 'lead'

    def get_success_url(self):
        messages.success(self.request, "Lead Deleted.")
        return reverse_lazy('lead:list', kwargs={'organization_name': self.get_organization()})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Delete Lead'    
        context['organization_name'] = self.get_organization()
        return context