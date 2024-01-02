from django.views.generic import TemplateView, ListView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import FormView
from django.forms import inlineformset_factory
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
# from django import forms
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.core.exceptions import ValidationError
# from datetime import timedelta


from configuration.country.models import Country
# from configuration.product.models import Product
from .models import Lead, LeadProduct, Task
from .forms import LeadForm, LeadProductForm, LeadUpdateForm, TaskCreateForm, TaskUpdateForm
from administration.userprofile.views import AgentRequiredMixin, AgentContextMixin


LeadProductFormset = inlineformset_factory(Lead, LeadProduct, form=LeadProductForm, extra=0, can_delete=True)


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
         # Obtener tareas asociadas al Lead
        lead_tasks = Task.objects.filter(lead=self.object)
        context['lead_tasks'] = lead_tasks


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
        # if self.request.POST:
        #     context['formset'] = LeadProductFormset(self.request.POST)
        # else:
        #     context['formset'] = LeadProductFormset()

        return context

class LeadUpdateView(UpdateView, AgentRequiredMixin, AgentContextMixin):
    model = Lead
    template_name = 'operation/lead/lead_update.html'
    form_class = LeadUpdateForm
    validation_error_handled = False    


    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        agent = self.request.user.agent
        current_time = timezone.now()
        # Obtener la instancia del lead
        lead = self.get_object()

        if agent:
            # Configuración de queryset para los campos que dependen del agente
            form.fields['country'].queryset = Country.objects.filter(
                Q(organization=agent.organization) & Q(is_selected=True)
            )
            form.fields['assigned_to'].queryset = User.objects.filter(
                agent__organization=agent.organization)          
                
        # Determinar el estado de los campos basado en las fechas de lead
        if lead.is_closed:
            # Deshabilitar todos los campos si el lead está cerrado
            for field in form.fields:
                form.fields[field].disabled = True
        else:
            # Estado predeterminado: habilitar todos los campos
            for field in form.fields:
                form.fields[field].disabled = False

            # Si end_date_time es pasado, deshabilita todos excepto 'extended_end_date_time'
            if lead.end_date_time and lead.end_date_time < current_time:
                for field in form.fields:
                    if field != 'extended_end_date_time':
                        form.fields[field].disabled = True              

            # Si extended_end_date_time es futuro, habilita todos excepto 'end_date_time'
            if lead.extended_end_date_time and lead.extended_end_date_time > current_time:
                for field in form.fields:
                    if field != 'end_date_time':
                        form.fields[field].disabled = False

        return form            

    def form_valid(self, form):
        agent = self.request.user.agent
        form.instance.organization = agent.organization
        form.instance.last_modified_by = agent.user

        try:
            lead = form.save(commit=False)           
            # end_date_time no puede ser menor a start_date_time
            if lead.end_date_time and lead.start_date_time and lead.end_date_time < lead.start_date_time:
                raise ValidationError(
                    "La fecha de finalización no puede ser anterior a la fecha de inicio.")

            # end_date_time no puede ser mayor a extended_end_date_time
            if lead.extended_end_date_time and lead.end_date_time and lead.end_date_time > lead.extended_end_date_time:
                raise ValidationError(
                    "La fecha de finalización extendida no puede ser anterior a la fecha de finalización original.")

             # Logica para establecer el stage is_closed"
            if lead.stage in ['close_win', 'close_lost']:
                lead.is_closed = True 

            # Si todo está bien, guarda el lead
            lead.save()

            # Guardar los formularios de LeadProduct
            formset = LeadProductFormset(
                self.request.POST, self.request.FILES, instance=lead)

            if formset.is_valid():
                formset.save()

            messages.success(self.request, "Lead actualizado")
            url = reverse('lead:update', kwargs={
                'organization_name': self.get_organization(), 'pk': self.object.pk})
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
        if not self.validation_error_handled:
            messages.error(self.request, "Invalid form data. Please check the entries and try again.")
        return render(self.request, self.template_name, {'form': form, 'organization_name': self.get_organization(), 'pk': self.object.pk})

      
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lead = self.get_object()
        organization = self.get_organization()
        context['pk'] = lead.pk
        context['titulo'] = 'Update Lead'
        context['organization_name'] = self.get_organization()
        current_time = timezone.now()

        # Determina si deshabilitan los botones update y create task
        context['enable_update'] = True
        context['enable_button'] = True
        if lead.end_date_time and lead.end_date_time < current_time and not lead.extended_end_date_time:
            context['enable_button'] = False            
        if lead.extended_end_date_time and lead.extended_end_date_time < current_time:
            context['enable_button'] = False
        if lead.stage in ['close_win', 'close_lost']:
            context['enable_update'] = False
            context['enable_button'] = False  


        # Determina si debe ocultarse el campo extended_end_date_time
        context['hide_extended_end_date_time'] = False
        if lead.end_date_time and lead.end_date_time > current_time:
            context['hide_extended_end_date_time'] = True 
            
        if self.request.POST:
            context['formset'] = LeadProductFormset(
            self.request.POST, instance=lead,
            form_kwargs={'organization': organization})  # Pasar la organización al formulario
        else:
            context['formset'] = LeadProductFormset(
            instance=lead,
            form_kwargs={'organization': organization})  # Pasar la organización al formulario

        # Validaciones para formset
        
        # Determinar el estado de los campos basado en las fehas de lead
        if lead.is_closed:
            # Deshabilitar todos los campos si el lead está cerrado
            for form in context['formset']:
                for field in form.fields:
                    form.fields[field].disabled = True
        else:
            # Estado predeterminado: habilitar todos los campos
            for form in context['formset']:
                for field in form.fields:
                    form.fields[field].disabled = False

            # Si end_date_time es pasado, deshabilita todos excepto 'extended_end_date_time'
            if lead.end_date_time and lead.end_date_time < current_time:
                for form in context['formset']:
                    for field in form.fields:
                        form.fields[field].disabled = True           

            # Si extended_end_date_time es futuro, habilita todos excepto 'end_date_time'
            if lead.extended_end_date_time and lead.extended_end_date_time > current_time:
                for form in context['formset']:
                    for field in form.fields:
                        form.fields[field].disabled = False       
                    

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

# LeadProductFormset = inlineformset_factory(
#     Lead, LeadProduct, form=LeadProductForm, extra=0, can_delete=True)


class HomeTaskView(LoginRequiredMixin, TemplateView):
    template_name = 'operation/task/task_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Gestion de Tasks'
        return context


# Query de Tasks de la base de datos enviada a JS como JSON para las Datatables JS
class TaskListView(ListView, AgentRequiredMixin, AgentContextMixin):
    model = Task

    def get_queryset(self):
        return Task.objects.filter(
            organization=self.get_organization()
        ).select_related('assigned_to', 'last_modified_by')
    
    def get(self, request, *args, **kwargs):
        tasks = self.get_queryset()
        tasks_data = list(tasks.values('id', 'name', 'last_modified_by_id',
                          'assigned_to_id', 'organization', 'modified_time', 'end_date_time', 'extended_end_date_time', 'lead_product__product__name', 'lead__lead_name'))
        user_names = {
            user.id: f"{user.first_name} {user.last_name}" for user in User.objects.all()
        }

        for task in tasks_data:
            task['assigned_to'] = user_names.get(task['assigned_to_id'])
            task['last_modified_by'] = user_names.get(task['last_modified_by_id'])
            task['organization'] = self.get_organization().name
            task['product_name'] = task['lead_product__product__name']  # Asigna el nombre del producto a una nueva clave
            task['lead_name'] = task['lead__lead_name']  # Nombre del lead

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
            lead_id = self.kwargs.get('pk')
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
    

class TaskDetailView(DetailView, AgentRequiredMixin, AgentContextMixin):
    model = Task
    template_name = 'operation/task/task_detail.html'
    context_object_name = 'task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['titulo'] = 'Detail Task'
        context['organization_name'] = self.get_organization()
       # Obtener el producto asociado a la tarea
        task = context['task']  # Esta es la instancia de Task que DetailView está mostrando
        task_product = None  # Inicializa como None por si no hay producto asociado        
        # Verifica si la tarea tiene un lead_product y, por lo tanto, un producto
        if task.lead_product:
            task_product = task.lead_product.product.name  # Sigue la relación hasta llegar al nombre del producto

        context['task_product'] = task_product  # Agrega el producto al contexto
  
        return context
    

class TaskDeleteView(DeleteView, AgentRequiredMixin, AgentContextMixin):
    model = Task
    template_name = 'operation/task/task_delete.html'
    context_object_name = 'task'

    def get_success_url(self):
        messages.success(self.request, "Task Deleted.")
        return reverse_lazy('lead:task-list', kwargs={'organization_name': self.get_organization()})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Delete Task'
        context['organization_name'] = self.get_organization()
        return context


class TaskUpdateView(UpdateView, AgentRequiredMixin, AgentContextMixin):
    model = Task
    template_name = 'operation/task/task_update.html'
    form_class = TaskUpdateForm
    validation_error_handled = False

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        agent = self.request.user.agent
        lead_id = self.kwargs.get('pk')
        lead = get_object_or_404(Lead, pk=lead_id)
        current_task_id = self.kwargs.get('pk')  # ID de la tarea actual
        task = self.get_object()
        current_time = timezone.now()    

        if agent:
            # Configuración de queryset para los campos que dependen del agente
            form.fields['assigned_to'].queryset = User.objects.filter(
                agent__organization=agent.organization)

        if lead:
           # Verificar si hay tareas existentes para el Lead
            lead_tasks = Task.objects.filter(lead=lead).exclude(pk=current_task_id)

            if lead_tasks.exists():  # Si hay tareas, ajustar el queryset de 'related_task'
                form.fields['related_task'].queryset = lead_tasks
                form.fields['parent_task'].queryset = lead_tasks
            else:  # Si no hay tareas, eliminar el campo 'related_task' del formulario
                del form.fields['related_task']
                del form.fields['parent_task']   

                
        # Validaciones basadas en el estado del Lead
        if lead.is_closed:
            # Deshabilitar todos los campos si el lead está cerrado
            for field in form.fields:
                form.fields[field].disabled = True
        # Validaciones basadas en el estado de la tarea
        elif task.is_closed:
            # Deshabilitar todos los campos si task está cerrado
            for field in form.fields:
                form.fields[field].disabled = True

        # Validaciones basadas en el estado del Lead       
        if lead.extended_end_date_time and lead.extended_end_date_time < current_time:
            for field in form.fields:
                form.fields[field].disabled = True 

        elif lead.end_date_time and lead.end_date_time < current_time and not lead.extended_end_date_time:
            for field in form.fields:
                form.fields[field].disabled = True           

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
            lead_id = self.kwargs.get('pk')
            # Obtener el objeto Lead
            lead = get_object_or_404(Lead, pk=lead_id)

            # Asegura que el Lead con este ID existe para evitar errores
            if lead:
                task.lead = get_object_or_404(Lead, pk=lead_id)
                lead_pk = task.lead.pk

                # Logica para establecer el stage is_closed"
                if task.stage in ['completed', 'canceled', 'skipped']:
                    task.is_closed = True 
                    
                messages.success(self.request, "Task editada correctamente")
                # Guarda el objeto Task
                task.save()

            else:
                # Cuando no tenga un lead asociado
                messages.error(
                    self.request, "El Task no tiene un Lead asociado.")
                return self.form_invalid(form)

            # Redirige a una URL específica después de editar la tarea, como la página update del lead asociado
            url = reverse('lead:task-update', kwargs={
                'organization_name': agent.organization, 'pk': lead_pk})
            return redirect(url)

        except ValidationError as e:
            self.validation_error_handled = True  # Indica que se manejó un error
            # Agrega el error de ValidationError al sistema de mensajes
            error_message = '; '.join(e.messages) if hasattr(e, 'messages') else str(e) 
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
        context = super().get_context_data(**kwargs)
        task = self.get_object()
        current_time = timezone.now()
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

        # Determina si deshabilia el boton update
        context['enable_update'] = True

        if lead.extended_end_date_time and lead.extended_end_date_time < current_time:
            context['enable_update'] = False

        if lead.end_date_time and not lead.extended_end_date_time and lead.end_date_time < current_time:
            context['enable_update'] = False


        return context