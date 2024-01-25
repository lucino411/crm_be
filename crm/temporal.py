class DealUpdateView(UpdateView, AgentRequiredMixin, AgentContextMixin):
    model = Deal
    template_name = 'operation/deal/deal_update.html'
    form_class = DealUpdateForm
    validation_error_handled = False    


    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        agent = self.request.user.agent
        current_time = timezone.now()
        # Obtener la instancia del deal
        deal = self.get_object()

        if agent:
            # Configuración de queryset para los campos que dependen del agente
            form.fields['country'].queryset = Country.objects.filter(
                Q(organization=agent.organization) & Q(is_selected=True)
            )
            form.fields['assigned_to'].queryset = User.objects.filter(
                agent__organization=agent.organization)          
                
        # Determinar el estado de los campos basado en las fechas de deal
        if deal.is_closed:
            # Deshabilitar todos los campos si el deal está cerrado
            for field in form.fields:
                form.fields[field].disabled = True
        else:
            # Estado predeterminado: habilitar todos los campos
            for field in form.fields:
                form.fields[field].disabled = False

            # Si end_date_time es pasado, deshabilita todos excepto 'extended_end_date_time'
            if deal.end_date_time and deal.end_date_time < current_time:
                for field in form.fields:
                    if field != 'extended_end_date_time':
                        form.fields[field].disabled = True              

            # Si extended_end_date_time es futuro, habilita todos excepto 'end_date_time'
            if deal.extended_end_date_time and deal.extended_end_date_time > current_time:
                for field in form.fields:
                    if field != 'end_date_time':
                        form.fields[field].disabled = False

        return form            

    def form_valid(self, form):
        agent = self.request.user.agent
        form.instance.organization = agent.organization
        form.instance.last_modified_by = agent.user
        current_time = timezone.now()

        try:
            deal = form.save(commit=False)           
            # end_date_time no puede ser menor a start_date_time
            if deal.end_date_time and deal.start_date_time and deal.end_date_time < deal.start_date_time:
                raise ValidationError(
                    "La fecha de finalización no puede ser anterior a la fecha de inicio.")

            # end_date_time no puede ser mayor a extended_end_date_time
            if deal.extended_end_date_time and deal.end_date_time and deal.end_date_time > deal.extended_end_date_time:
                raise ValidationError(
                    "La fecha de finalización extendida no puede ser anterior a la fecha de finalización original.")

             # Logica para establecer el stage is_closed"
            if deal.stage in ['close_win', 'close_lost']:
                deal.is_closed = True 

            with transaction.atomic():
                # Captura el antiguo Contact y la antigua Company asociada al Lead, antes de cualquier cambio
                old_company = deal.company
                old_client = deal.client

                new_email = form.cleaned_data.get('primary_email')
                # Verificar si existe un Contact con el nuevo primary_email
                existing_contact = Contact.objects.filter(primary_email=new_email).first()

                deal_name = form.cleaned_data.get('deal_name')
                deal_source = form.cleaned_data.get('deal_source')
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                title = form.cleaned_data.get('title')
                phone = form.cleaned_data.get('phone')
                mobile_phone = form.cleaned_data.get('mobile_phone')
                company_name = form.cleaned_data.get('company_name')
                new_company_email = form.cleaned_data.get('company_email')
                # Verificar si existe una Company con el nuevo company_email
                existing_company = Company.objects.filter(company_email=new_company_email).first()
                company_phone = form.cleaned_data.get('company_phone')
                website = form.cleaned_data.get('website')
                industry = form.cleaned_data.get('industry')

                country = form.cleaned_data.get('country')
                currency = form.cleaned_data.get('currency')

                description = form.cleaned_data.get('description')
                
                assigned_to = form.cleaned_data.get('assigned_to')
                last_modified_by = agent.user
                modified_time = current_time
                start_date_time = form.cleaned_data.get('start_date_time')
                end_date_time = form.cleaned_data.get('end_date_time')
                extended_end_date_time = form.cleaned_data.get('extended_end_date_time')

                stage = form.cleaned_data.get('stage')


                client = deal.client
                if client:
                    fields_to_update = []
                    for field, value in [
                        ('primary_email', new_email), 
                        ('first_name', first_name), 
                        ('last_name', last_name), 
                        ('title', title), 
                        ('phone', phone), 
                        ('mobile_phone', mobile_phone), 
                        ('company', deal.company), 
                        ('country', country),
                        ('last_modified_by', last_modified_by), 
                        ('modified_time', current_time), 
                    ]:
                        if getattr(client, field) != value:
                            setattr(client, field, value)
                            fields_to_update.append(field)

                    if fields_to_update:
                        client.last_modified_by = agent.user
                        client.save(update_fields=fields_to_update + ['last_modified_by'])                        

                        # Actualizar todos los Deals asociados con este Client
                        for related_deal in client.client_deals.all():
                            related_deal.primary_email = new_email
                            related_deal.first_name = first_name
                            related_deal.last_name = last_name
                            related_deal.title = title
                            related_deal.phone = phone
                            related_deal.mobile_phone = mobile_phone
                            related_deal.company_name = company_name
                            related_deal.website = website
                            related_deal.country = country
                            related_deal.save()

                    # Buscar y actualizar el Contact correspondiente
                    try:
                        contact = Contact.objects.get(primary_email=new_email)
                        for field in fields_to_update:
                            setattr(contact, field, getattr(client, field))
                        contact.save()

                        # Actualizar todos los Leads asociados con este Contact
                        # for lead in contact.contact_leads.all():
                        #     print('heeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeere')
                        #     setattr(lead, field, getattr(contact, field))
                        #     lead.save()
                        # related_leads = contact.contact_leads.all()
                        # for lead in related_leads:
                        #     for field in client_fields_to_update:
                        #         setattr(lead, field, getattr(contact, field))
                        #     lead.save()

                    except Contact.DoesNotExist:
                        # No hay un Client con este primary_email, no se necesita hacer nada más
                        pass

            # Si todo está bien, guarda el deal
            deal.save()

            # Guardar los formularios de DealProduct
            formset = DealProductFormset(
                self.request.POST, self.request.FILES, instance=deal)

            if formset.is_valid():
                formset.save()

            messages.success(self.request, "Deal actualizado")
            url = reverse('deal:update', kwargs={
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
        deal = self.get_object()
        context = self.get_context_data()
        # Actualizar el contexto con datos específicos del formulario inválido
        context.update({
            'form': form,  # Asegurarse de pasar el formulario inválido
            'lead_pk': deal.id,  # ID del lead
            'organization_name': self.get_organization(),
            # Aquí puedes agregar cualquier otro dato específico necesario
        })
        if not self.validation_error_handled:
            messages.error(
                self.request, "Invalid form data. Please check the entries and try again.")
        return render(self.request, self.template_name,  context)    

      
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        deal = self.get_object()
        organization = self.get_organization()
        context['pk'] = deal.pk
        context['titulo'] = 'Update Deal'
        context['organization_name'] = self.get_organization()
        current_time = timezone.now()

        # Determina si deshabilitan los botones update y create task
        context['enable_update'] = True
        context['enable_button'] = True
        if deal.end_date_time and deal.end_date_time < current_time and not deal.extended_end_date_time:
            context['enable_button'] = False            
        if deal.extended_end_date_time and deal.extended_end_date_time < current_time:
            context['enable_button'] = False
        if deal.stage in ['close_win', 'close_lost']:
            context['enable_update'] = False
            context['enable_button'] = False  


        # Determina si debe ocultarse el campo extended_end_date_time
        context['hide_extended_end_date_time'] = False
        if deal.end_date_time and deal.end_date_time > current_time:
            context['hide_extended_end_date_time'] = True 
            
        if self.request.POST:
            context['formset'] = DealProductFormset(
            self.request.POST, instance=deal,
            form_kwargs={'organization': organization})  # Pasar la organización al formulario
        else:
            context['formset'] = DealProductFormset(
            instance=deal,
            form_kwargs={'organization': organization})  # Pasar la organización al formulario

        # Validaciones para formset
        
        # Determinar el estado de los campos basado en las fehas de deal
        if deal.is_closed:
            # Deshabilitar todos los campos si el deal está cerrado
            for form in context['formset']:
                for field in form.fields:
                    form.fields[field].disabled = True
        else:
            # Estado predeterminado: habilitar todos los campos
            for form in context['formset']:
                for field in form.fields:
                    form.fields[field].disabled = False

            # Si end_date_time es pasado, deshabilita todos excepto 'extended_end_date_time'
            if deal.end_date_time and deal.end_date_time < current_time:
                for form in context['formset']:
                    for field in form.fields:
                        form.fields[field].disabled = True           

            # Si extended_end_date_time es futuro, habilita todos excepto 'end_date_time'
            if deal.extended_end_date_time and deal.extended_end_date_time > current_time:
                for form in context['formset']:
                    for field in form.fields:
                        form.fields[field].disabled = False                           

        return context










### TEmporal

            