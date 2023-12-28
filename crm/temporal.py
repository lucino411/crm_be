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

        # Lógica para deshabilitar el formulario si el lead está en "Close Win" o "Close Lost"
        if lead.stage in ['close_win', 'close_lost']:
            for field in form.fields:
                form.fields[field].disabled = True
            return form

        # Aplica la lógica para habilitar/deshabilitar campos
        if lead.end_date_time and lead.end_date_time < timezone.now():
            form.fields['end_date_time'].disabled = True
            form.fields['extended_end_date_time'].disabled = False
        elif lead.end_date_time and lead.end_date_time > timezone.now():
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

        # Tu lógica de validación aquí...
        try:
            lead = form.save(commit=False)
            # Añade un atributo para rastrear si ya se manejó un ValidationError
            # self.validation_error_handled = False
            # end_date_time no puede ser menor a start_date_time
            if lead.end_date_time and lead.start_date_time and lead.end_date_time < lead.start_date_time:
                raise ValidationError(
                    "La fecha de finalización no puede ser anterior a la fecha de inicio.")

            # end_date_time no puede ser mayor a extended_end_date_time
            if lead.extended_end_date_time and lead.end_date_time and lead.end_date_time > lead.extended_end_date_time:
                raise ValidationError(
                    "La fecha de finalización extendida no puede ser anterior a la fecha de finalización original.")

             # Establecer is_closed en True si el stage es "Close Win" o "Close Lost"
            if lead.stage in ['close_win', 'close_lost']:
                lead.is_closed = True
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

            # Si todo está bien, guarda el lead
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

        except ValidationError as e:
            print(
                'validation errrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrror')
            self.validation_error_handled = True  # Indica que se manejó un error
            # Agrega el error de ValidationError al sistema de mensajes
            error_message = '; '.join(e.messages) if hasattr(
                e, 'messages') else str(e)
            messages.error(self.request, error_message)
            # Agrega los errores del ValidationError al formulario y vuelve a mostrar el formulario
            form.add_error(None, e)
            return self.form_invalid(form)
            # url = reverse('lead:update', kwargs={
            #         'organization_name': self.get_organization(), 'pk': self.object.pk})
            # return redirect(url)

    def form_invalid(self, form):
        lead = self.get_object()  # Obtener el objeto lead actual
        print('invaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaalllllllllllllllllllllllllid')
        print('Lead ID:', lead.pk)  # Para depuración
        # print(self.object.pk)
        print('invaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaalllllllllllllllllllllllllid')
        print(form.errors)
        if not self.validation_error_handled:
            messages.error(
                self.request, "Invalid form data. Please check the entries and try again.")
        return render(self.request, self.template_name, {'form': form, 'organization_name': self.get_organization(), 'pk': lead.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lead = self.get_object()
        context['pk'] = lead.pk
        context['titulo'] = 'Update Lead'
        context['organization_name'] = self.get_organization()
        current_time = timezone.now()

       # Este flag permite habilitar la actualización solo cuando las condiciones sean adecuadas
        context['enable_update'] = False
        context['task_create'] = False
        if lead.extended_end_date_time and lead.extended_end_date_time > current_time and lead.stage not in ['close_win', 'close_lost']:
            context['enable_update'] = True
            context['task_create'] = True
        elif lead.end_date_time and lead.end_date_time < current_time and lead.extended_end_date_time and lead.extended_end_date_time < current_time and lead.stage not in ['close_win', 'close_lost']:
            context['enable_update'] = True
            context['task_create'] = False
        elif lead.end_date_time and lead.end_date_time < current_time and not lead.extended_end_date_time and lead.stage not in ['close_win', 'close_lost']:
            context['enable_update'] = True
            context['task_create'] = False
        elif lead.end_date_time and lead.end_date_time > current_time and not lead.extended_end_date_time and lead.stage not in ['close_win', 'close_lost']:
            context['enable_update'] = True
            context['task_create'] = True
        elif lead.stage in ['close_win', 'close_lost']:
            context['enable_update'] = False
            context['task_create'] = False

        # Determina si debe ocultarse el campo extended_end_date_time
        context['hide_extended_end_date_time'] = False
        if lead.end_date_time and lead.end_date_time > current_time:
            context['hide_extended_end_date_time'] = True

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
