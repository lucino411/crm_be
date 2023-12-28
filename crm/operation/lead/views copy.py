from django.views.generic import TemplateView, ListView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import FormView
from django.forms import inlineformset_factory
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django import forms
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta


from configuration.country.models import Country
from .models import Lead, LeadProduct, Task
from .forms import LeadForm, LeadProductForm, LeadUpdateForm, TaskCreateForm
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

        try:
            lead = form.save(commit=False)
            validation_error_handled = False
            # end_date_time no puede ser menor a start_date_time
            if lead.end_date_time and lead.start_date_time and lead.end_date_time < lead.start_date_time:
                raise ValidationError(
                    "La fecha de finalización no puede ser anterior a la fecha de inicio.")

            lead.save()

            messages.success(self.request, "Lead Creado correctamente")
            url = reverse('lead:list', kwargs={
                'organization_name': agent.organization})
            return redirect(url)

        except ValidationError as e:
            self.validation_error_handled = True  # Indica que se manejó un error
            # Agrega el error de ValidationError al sistema de mensajes
            error_message = '; '.join(e.messages) if hasattr(
                e, 'messages') else str(e)
            messages.error(self.request, error_message)
            # Agrega los errores del ValidationError al formulario y vuelve a mostrar el formulario
            form.add_error(None, e)
            # return self.form_invalid(form)
            return render(self.request, self.template_name, {'form': form, 'organization_name': agent.organization})

    def form_invalid(self, form):
        # print(form.errors)
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


class LeadUpdateView(UpdateView, AgentContextMixin):
    model = Lead
    template_name = 'operation/lead/lead_update.html'
    form_class = LeadUpdateForm

    def form_valid(self, form):
        agent = self.request.user.agent
        form.instance.organization = agent.organization
        form.instance.last_modified_by = agent.user

        lead = form.save(commit=False)

        if lead.start_date_time > lead.end_date_time:
            raise ValidationError("La fecha de finalización no puede ser anterior a la fecha de inicio.")          

        lead.save()        

        messages.success(self.request, "Lead actualizado")
        return redirect(reverse('lead:detail', kwargs={'organization_name': self.get_organization(), 'pk': self.object.pk}))
       

    def form_invalid(self, form):
        print('Lead ID:', self.object.pk)
        print(form.errors)
        messages.error(self.request, "Invalid form data. Please check the entries and try again.")
        return render(self.request, self.template_name, {'form': form, 'organization_name': self.get_organization(), 'pk': self.object.pk})


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lead = self.get_object()
        context['pk'] = lead.pk
        context['organization_name'] = self.get_organization()

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


# ************
  # CUR TASK
# ************

LeadProductFormset = inlineformset_factory(
    Lead, LeadProduct, form=LeadProductForm, extra=0, can_delete=True)


class HomeLeadView(LoginRequiredMixin, TemplateView):
    template_name = 'operation/lead/lead_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Gestion de Leads'
        return context


# Query de Tasks de la base de datos enviada a JS como JSON para las Datatables JS
class TaskListView(ListView, AgentRequiredMixin, AgentContextMixin):
    model = Task

    def get_queryset(self):
        return Task.objects.filter(
            organization=self.get_organization()
        ).select_related('lead_product', 'assigned_to', 'last_modified_by')

    def get(self, request, *args, **kwargs):
        tasks = self.get_queryset()
        tasks_data = [
            {
                'id': task.id,
                'name': task.name,
                'task_lead_product': task.lead_product.name if task.lead_product else None,
                'assigned_to': task.assigned_to.get_full_name() if task.assigned_to else None,
                'start_date_time': task.start_date_time.strftime('%Y-%m-%d %H:%M:%S') if task.start_date_time else None,
            }
            for task in tasks
        ]
        return JsonResponse({'tasks': tasks_data})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization_name'] = self.get_organization().name
        return context


class TaskCreateView(FormView, AgentRequiredMixin, AgentContextMixin):
    model = Task
    template_name = 'operation/task/task_create.html'
    form_class = TaskCreateForm


    validation_error_handled = False

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        agent = self.request.user.agent
        lead_id = self.kwargs.get('pk')
        lead = get_object_or_404(Lead, pk=lead_id)

        if agent:
            # Configuración de queryset para los campos que dependen del agente
            form.fields['assigned_to'].queryset = User.objects.filter(
                agent__organization=agent.organization)

        if lead:
            form.fields['lead_product'].queryset = LeadProduct.objects.filter(
                lead=lead)
            # Verificar si hay tareas existentes para el Lead
            lead_tasks = Task.objects.filter(lead=lead)
            if lead_tasks.exists():  # Si hay tareas, ajustar el queryset de 'related_task'
                form.fields['related_task'].queryset = lead_tasks
                form.fields['parent_task'].queryset = lead_tasks
            else:  # Si no hay tareas, eliminar el campo 'related_task' del formulario
                del form.fields['related_task']
                del form.fields['parent_task']

        return form

    def form_valid(self, form):
        try:
            # self.validation_error_handled = False
            agent = self.request.user.agent
            task = form.save(commit=False)
            task.organization = agent.organization
            task.created_by = agent.user
            task.last_modified_by = agent.user

            # Capturar el ID del Lead desde la URL
            lead_id = self.kwargs.get('lead_id')
            # Obtener el objeto Lead
            lead = get_object_or_404(Lead, pk=lead_id)

            # Asegura que el Lead con este ID existe para evitar errores
            if lead_id:
                # task.lead = Lead.objects.get(pk=lead_id)
                task.lead = get_object_or_404(Lead, pk=lead_id)
                lead_pk = task.lead.pk

                # end_date_time no puede ser menor a lead.end_date_time
                if lead.extended_end_date_time and task.end_date_time and task.end_date_time > lead.extended_end_date_time:
                    raise ValidationError("La fecha de finalización de la tarea no puede ser posterior a la fecha de finalización extendida del lead (%s)." %
                                          lead.extended_end_date_time.strftime("%Y-%m-%d"))

                elif lead.end_date_time and not lead.extended_end_date_time and task.end_date_time > lead.end_date_time:

                    raise ValidationError("La fecha de finalización de la tarea no puede ser posterior a la fecha de finalización del lead (%s)." %
                                          lead.end_date_time.strftime("%Y-%m-%d"))
                elif lead.start_date_time and task.end_date_time < lead.start_date_time:

                    raise ValidationError("La fecha de finalización de la tarea no puede ser menor a la fecha de inicio del lead (%s)." %
                                          lead.start_date_time.strftime("%Y-%m-%d"))
                # end_date_time no puede ser menor a start_date_time
                if task.end_date_time and task.start_date_time and task.end_date_time < task.start_date_time:
                    raise ValidationError(
                        "La fecha de finalización no puede ser anterior a la fecha de inicio.")

                messages.success(self.request, "Task creada correctamente")

                # Guarda el objeto Task
                task.save()

            else:
                # Cuando no tenga un lead asociado
                messages.error(
                    self.request, "El Task no tiene un Lead asociado.")
                return self.form_invalid(form)

            # Redirige a una URL específica después de la creación, como la página update del lead asociado
            url = reverse('lead:update', kwargs={
                'organization_name': agent.organization, 'pk': lead_pk})
            return redirect(url)

        except ValidationError as e:
            self.validation_error_handled = True  # Indica que se manejó un error
            # Agrega el error de ValidationError al sistema de mensajes
            error_message = '; '.join(e.messages) if hasattr(
                e, 'messages') else str(e)
            messages.error(self.request, error_message)
            # Agrega los errores del ValidationError al formulario y vuelve a mostrar el formulario
            form.add_error(None, e)

            return self.form_invalid(form)

    def form_invalid(self, form):
        # print(form.errors)
        lead_id = self.kwargs.get('lead_id')
        if not self.validation_error_handled:
            messages.error(
                self.request, "Invalid form data. Please check the entries and try again.")
        return render(self.request, self.template_name, {
            'form': form,
            'organization_name': self.get_organization(),
            'pk': lead_id
        })

























    def get_context_data(self, **kwargs):
        # Asegúrate de que el contexto contenga todos los datos necesarios para la plantilla
        context = super().get_context_data(**kwargs)

        # Obtener el ID del Lead de los argumentos de la URL
        lead_id = self.kwargs.get('pk')
        lead = get_object_or_404(Lead, pk=lead_id)  # Obtener el objeto Lead
        # Componer el título y añadirlo al contexto
        if lead.lead_name:
            context['titulo'] = f"Crear Task for {lead.lead_name}"
        else:
            context['titulo'] = "Crear Task"
        context['lead'] = lead
        context['pk'] = lead_id

        context['lead_name'] = lead.lead_name if lead else None
        context['organization_name'] = self.get_organization()

        return context





