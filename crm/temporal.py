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


        # Configurar el campo parent_task si se está creando una subtarea
        if 'parent_task_id' in self.kwargs:
            parent_task_id = self.kwargs['parent_task_id']
            # Asegúrate de establecer el valor por defecto de parent_task aquí
            form.fields['parent_task'].initial = parent_task_id
            

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
                if task.stage in ['completed', 'canceled']:
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
        
        # Si se está pasando un ID de tarea parent como parámetro para crear una subtarea
        context['parent_task_id'] = self.request.GET.get('parent_task')

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
