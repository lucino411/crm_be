from django.views.generic import TemplateView, ListView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import FormView
from django.forms import inlineformset_factory
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.db.models import Q
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.core.exceptions import ValidationError


from administration.userprofile.views import AgentRequiredMixin, AgentContextMixin
from configuration.country.models import Country
from .models import Lead, LeadProduct, LeadTask
from .forms import LeadForm, LeadProductForm, LeadUpdateForm, LeadTaskCreateForm, LeadTaskUpdateForm

# from deal.models import Deal, DealProduct, DealTask  


LeadProductFormset = inlineformset_factory(Lead, LeadProduct, form=LeadProductForm, extra=0, can_delete=True)

# def convert_lead_to_deal(request, lead_id):
#     lead = get_object_or_404(Lead, id=lead_id)

#     with transaction.atomic():
#         # Crear una instancia de Deal con los datos de Lead
#         deal = Deal(
#             deal_name=lead.lead_name,
#             # ... copiar todos los campos relevantes
#         )
#         deal.save()

#         # Copiar relaciones, como productos y tareas
#         for lead_product in lead.lead_product.all():
#             DealProduct.objects.create(
#                 deal=deal,
#                 product=lead_product.product,
#                 # ... otros campos
#             )

#         for task in lead.tasks.all():
#             DealTask.objects.create(
#                 deal=deal,
#                 # ... otros campos
#             )

#         # Eliminar el Lead original
#         lead.delete()

#         # Opcional: agregar un mensaje para confirmar la conversión
#         messages.success(request, "Lead converted to Deal successfully.")

#     # Redireccionar a la página adecuada después de la conversión
#     return redirect('some-view-name')





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
        lead_tasks = LeadTask.objects.filter(lead=self.object)
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


class LeadHomeTaskView(LoginRequiredMixin, TemplateView):
    template_name = 'operation/leadtask/task_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Gestion de Tasks'
        return context


# Query de Tasks de la base de datos enviada a JS como JSON para las Datatables JS
class LeadTaskListView(ListView, AgentRequiredMixin, AgentContextMixin):
    model = LeadTask

    def get_queryset(self):
        return LeadTask.objects.filter(
            organization=self.get_organization()
        ).select_related('assigned_to', 'last_modified_by')
    
    def get(self, request, *args, **kwargs):
        tasks = self.get_queryset()
        tasks_data = list(tasks.values('id', 'name', 'last_modified_by_id',
                          'assigned_to_id', 'organization', 'modified_time', 'created_by_id', 'lead_product__product__name', 'lead__lead_name'))
        user_names = {
            user.id: f"{user.first_name} {user.last_name}" for user in User.objects.all()
        }

        for task in tasks_data:
            task['created_by'] = user_names.get(task['created_by_id'])
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


class LeadTaskCreateView(FormView, AgentRequiredMixin, AgentContextMixin):
    model = LeadTask
    template_name = 'operation/leadtask/task_create.html'
    form_class = LeadTaskCreateForm
    validation_error_handled = False

    def get_form(self, form_class=None):
        form = super().get_form(form_class)       
        agent = self.request.user.agent
        lead_id = self.kwargs.get('lead_pk')
        lead = get_object_or_404(Lead, pk=lead_id)
       
        if agent:
            # Configuración de queryset para los campos que dependen del agente
            form.fields['assigned_to'].queryset = User.objects.filter(
                agent__organization=agent.organization)        
            
        if lead:
            # Filtra los productos del lead
            form.fields['lead_product'].queryset = LeadProduct.objects.filter(lead=lead)       

            # Preparando el queryset de tareas relacionadas al lead y excluyendo parent tasks y sub-tareas
            # Excluir las tareas que son subtask
            tasks_to_exclude = LeadTask.objects.filter(parent_task__isnull=False).values_list('id', flat=True)

            # Filtrar tareas elegibles para ser parent_task
            eligible_tasks = LeadTask.objects.filter(
                lead=lead
            ).exclude(
                id__in=tasks_to_exclude
            )

            # Si no hay tareas elegibles, ocultar el campo parent_task
            if not eligible_tasks.exists():
                del form.fields['parent_task']
            else:
                form.fields['parent_task'].queryset = eligible_tasks
          
            # Configurar el campo parent_task si se está creando una subtarea
            parent_task_id = self.request.GET.get('parent_task')
            if parent_task_id:
                try:
                    parent_task_id = int(parent_task_id)  # Asegúrate de que es un entero
                    form.fields['parent_task'].initial = parent_task_id
                    form.fields['parent_task'].disabled = True  # Hacer el campo no editable
                except ValueError:
                    # Manejar el caso en que parent_task_id no sea un entero
                    pass   

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
            lead_id = self.kwargs.get('lead_pk')
            # Obtener el objeto Lead
            lead = get_object_or_404(Lead, pk=lead_id)
            # Asegura que el Lead con este ID existe para evitar errores
            if lead:
                task.lead = get_object_or_404(Lead, pk=lead_id)

                messages.success(self.request, "Task creada correctamente")
                # Guarda el objeto Task
                task.save()                   
                
            else:
                # Cuando no tenga un lead asociado
                messages.error(
                    self.request, "El Task no tiene un Lead asociado.")
                return self.form_invalid(form)

            # Redirige a una URL específica después de la creación, como la página update del lead asociado
            url = reverse('lead:task-list', kwargs={
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

            return self.form_invalid(form)

    def form_invalid(self, form):
        # print(form.errors)
        current_task_id = self.kwargs.get('pk')  # ID de la tarea actual
        task = get_object_or_404(LeadTask, pk=current_task_id)
        lead = task.lead

        if not self.validation_error_handled:
            messages.error(
                self.request, "Invalid form data. Please check the entries and try again.")
        return render(self.request, self.template_name, {
            'form': form,
            'organization_name': self.get_organization(),
            'lead_pk': lead.id,
        })   


    def get_context_data(self, **kwargs):
        # Asegúrate de que el contexto contenga todos los datos necesarios para la plantilla
        context = super().get_context_data(**kwargs)        
        # Obtener el ID del Lead de los argumentos de la URL
        lead_id = self.kwargs.get('lead_pk')
        lead = get_object_or_404(Lead, pk=lead_id)  # Obtener el objeto Lead

        # Componer el título y añadirlo al contexto
        if lead.lead_name:
            context['titulo'] = f"Crear Task for {lead.lead_name}"
        else:
            context['titulo'] = "Crear Task"
        context['lead'] = lead
        context['lead_name'] = lead.lead_name if lead else None
        context['lead_pk'] = lead_id
        context['organization_name'] = self.get_organization()

        return context
    

class LeadTaskDetailView(DetailView, AgentRequiredMixin, AgentContextMixin):
    model = LeadTask
    template_name = 'operation/leadtask/task_detail.html'
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

         # Obtener todas las subtareas asociadas a esta tarea
        subtasks = task.parent_leadtask.all()  # Usa la relación inversa definida por 'related_name'

        # Agrega las subtareas al contexto
        context['subtasks'] = subtasks
  
        return context
    

class LeadTaskDeleteView(DeleteView, AgentRequiredMixin, AgentContextMixin):
    model = LeadTask
    template_name = 'operation/leadtask/task_delete.html'
    context_object_name = 'task'

    def get_success_url(self):
        messages.success(self.request, "Task Deleted.")
        return reverse_lazy('lead:task-list', kwargs={'organization_name': self.get_organization()})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Delete Task'
        context['organization_name'] = self.get_organization()
        return context


class LeadTaskUpdateView(UpdateView, AgentRequiredMixin, AgentContextMixin):
    model = LeadTask
    template_name = 'operation/leadtask/task_update.html'
    form_class = LeadTaskUpdateForm
    validation_error_handled = False

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        agent = self.request.user.agent
        current_task_id = self.kwargs.get('pk')  # ID de la tarea actual
        task = get_object_or_404(LeadTask, pk=current_task_id)
        lead = task.lead  # Obteniendo el lead asociado a la tarea

        if agent:
            # Configuración de queryset para los campos que dependen del agente
            form.fields['assigned_to'].queryset = User.objects.filter(
                agent__organization=agent.organization)            
        
        if lead:
            # Filtra los productos del lead
            form.fields['lead_product'].queryset = LeadProduct.objects.filter(lead=lead)

            # Preparando el queryset de tareas relacionadas al lead y excluyendo la tarea actual, parent tasks y sub-tareas
            # Seleccionamos la tarea actual
            current_task_id = self.kwargs.get('pk')
            current_task = get_object_or_404(LeadTask, pk=current_task_id)

            # Excluir la tarea actual y las tareas que son subtask
            tasks_to_exclude = LeadTask.objects.filter(parent_task__isnull=False).values_list('id', flat=True)
            tasks_to_exclude = list(tasks_to_exclude) + [current_task_id]

            # Ajustar el queryset del campo parent_task
            form.fields['parent_task'].queryset = LeadTask.objects.filter(
                lead=current_task.lead
            ).exclude(
                id__in=tasks_to_exclude
            )         

            # Configurar el campo parent_task si se está creando una subtarea
            if 'parent_task_id' in self.kwargs:
                parent_task_id = self.kwargs['parent_task_id']
                # Establecer el valor por defecto de parent_task aquí
                form.fields['parent_task'].initial = parent_task_id   

            # Deshabilitar el formulario de la current task y subtasks, si la tarea está cerrada
            if current_task.is_closed:
                for field in form.fields.values():
                    field.disabled = True

           # Comprobar si la tarea tiene padres o hijos
           # Condición 1: Si una tarea es padre, no puede ser hija
            if LeadTask.objects.filter(parent_task=current_task).exists():
                form.fields['parent_task'].disabled = True

            # Condición 2 y 3: Si una tarea es hija, no puede ser padre ni cambiar de padre
            if current_task.parent_task:
                form.fields['parent_task'].disabled = True
                  
            return form
                

    def form_valid(self, form):
        try:
            # self.validation_error_handled = False
            agent = self.request.user.agent
            current_task_id = self.kwargs.get('pk')  # ID de la tarea actual
            task = get_object_or_404(LeadTask, pk=current_task_id)
            task.organization = agent.organization
            task.created_by = agent.user
            task.last_modified_by = agent.user
            lead = task.lead  # Obteniendo el lead asociado a la tarea
            current_time = timezone.now()
            
            # Asegura que el Lead con este ID existe para evitar errores
            if lead:
                task = form.save(commit=False)
                task.lead = get_object_or_404(Lead, pk=lead.id) 

                if lead.is_closed:
                    messages.error(self.request, "El Lead esta cerrado.")
                    return self.form_invalid(form)            
                
                # Validaciones basadas en el estado de la tarea
                if task.is_closed:
                    messages.error(self.request, "La tarea esta cerrada.")
                    return self.form_invalid(form)
                # Validaciones basadas en las fechas de cierre del Lead
                if lead.extended_end_date_time and lead.extended_end_date_time < current_time:
                    # Implementa la lógica adecuada si el lead ha pasado su fecha extendida de cierre
                    messages.error(self.request, "El Lead esta cerrado.")
                    return self.form_invalid(form) 
                elif lead.end_date_time and lead.end_date_time < current_time and not lead.extended_end_date_time:
                    messages.error(self.request, "El Lead esta cerrado.")
                    return self.form_invalid(form)    

                # Logica para establecer el stage is_closed"
                if task.stage in ['completed', 'canceled']:
                    task.is_closed = True
                    # También marcar como cerrada las subtareas si la tarea principal está cerrada
                    for subtask in task.parent_leadtask.all():
                        subtask.is_closed = True 
                        subtask.save()
             
                # Guarda el objeto Task                
                messages.success(self.request, "Task editada correctamente")
                task.save()

            else:
                # Cuando no tenga un lead asociado
                messages.error(
                    self.request, "El Task no tiene un Lead asociado.")
                return self.form_invalid(form)

            # Redirige a una URL específica después de editar la tarea, como la página update del lead asociado
            url = reverse('lead:task-update', kwargs={
                'organization_name': agent.organization, 'pk': current_task_id})
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
        current_task_id = self.kwargs.get('pk')  # ID de la tarea actual
        task = get_object_or_404(LeadTask, pk=current_task_id)
        lead = task.lead
        context = self.get_context_data()
            # Actualizar el contexto con datos específicos del formulario inválido
        context.update({
            'form': form,  # Asegurarse de pasar el formulario inválido
            'lead_pk': lead.id,  # ID del lead
            'organization_name': self.get_organization(),
            # Aquí puedes agregar cualquier otro dato específico necesario
        })
        if not self.validation_error_handled:
            messages.error(
                self.request, "Invalid form data. Please check the entries and try again.")
        return render(self.request, self.template_name,  context)    
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        # Si se está pasando un ID de tarea parent como parámetro para crear una subtarea
        context['parent_task_id'] = self.request.GET.get('parent_task')
        current_time = timezone.now()
        # Obtener el ID del Lead de los argumentos de la URL
        current_task_id = self.kwargs.get('pk')  # ID de la tarea actual
        task = get_object_or_404(LeadTask, pk=current_task_id)
        lead = task.lead  # Obteniendo el lead asociado a la tarea
        # Componer el título y añadirlo al contexto
        if lead.lead_name:
            context['titulo'] = f"Crear Task for {lead.lead_name}"
        else:
            context['titulo'] = "Crear Task"
        context['task'] = task
        context['lead'] = lead
        context['lead_pk'] = lead.id
        context['pk'] = current_task_id
        context['lead_name'] = lead.lead_name if lead else None
        context['organization_name'] = self.get_organization()

        # Determina si deshabilia los botones del formulario
        context['enable_button'] = True

        # Verificar si la tarea actual no es una subtask (no tiene parent_task)
        if not task.parent_task:
            # Habilitar el botón si también se cumple la condición de la fecha del lead
            context['enable_button'] = True
        else:
            context['enable_button'] = False

        if lead.extended_end_date_time and lead.extended_end_date_time < current_time:
            context['enable_button'] = False

        if lead.end_date_time and not lead.extended_end_date_time and lead.end_date_time < current_time:
            context['enable_button'] = False

        # datos para validar habilitar o deshabilitar los campos del formulario con JS de acuerdo al estado del lead y la tarea
        context['is_lead_closed'] = lead.is_closed
        context['is_task_closed'] = task.is_closed
        context['extended_end_date_time'] = lead.extended_end_date_time
        context['end_date_time'] = lead.end_date_time


        return context