 email = form.cleaned_data['primary_email']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        title = form.cleaned_data['title']
        phone = form.cleaned_data['phone']
        mobile_phone = form.cleaned_data['mobile_phone']
        company_name = form.cleaned_data['company_name']
        country = form.cleaned_data['country']

        try:
            lead = form.save(commit=False)
            validation_error_handled = False
            # end_date_time no puede ser menor a start_date_time
            if lead.end_date_time and lead.start_date_time and lead.end_date_time < lead.start_date_time:
                raise ValidationError(
                    "La fecha de finalización no puede ser anterior a la fecha de inicio.")
            
            # Crea o Actualiza el contact si ya existe:
            contact, created = Contact.objects.get_or_create(
            primary_email=email, 
            organization=agent.organization,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'title': title,
                'phone': phone,
                'mobile_phone': mobile_phone,
                'company_name': company_name,
                'country': country,
                'created_by': agent.user,
                'last_modified_by': agent.user,
                }
            )

            if not created:
                # Actualiza los campos si el Contact ya existía
                fields_to_update = []
                for field in ['first_name', 'last_name', 'title', 'phone', 'mobile_phone', 'company_name', 'country']:
                    if getattr(contact, field) != locals()[field]:
                        setattr(contact, field, locals()[field])
                        fields_to_update.append(field)
                if fields_to_update:
                    contact.last_modified_by = agent.user
                    contact.save(update_fields=fields_to_update + ['last_modified_by'])  

            # Verificar si el Contacto existe en Client
            if Client.objects.filter(primary_email=email).exists():
                contact.is_client = True
                contact.save(update_fields=['is_client'])
            
            lead.contact = contact  # Asocia el Contact con el Lead





   def form_valid(self, form):    
        agent = self.request.user.agent
        form.instance.organization = agent.organization
        form.instance.created_by = agent.user
        form.instance.last_modified_by = agent.user

        try:
            lead = form.save(commit=False)
            validation_error_handled = False         
            new_email = form.cleaned_data.get('primary_email')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            title = form.cleaned_data.get('title')
            phone = form.cleaned_data.get('phone')
            mobile_phone = form.cleaned_data.get('mobile_phone')
            company_name = form.cleaned_data.get('company_name')
            country = form.cleaned_data.get('country')
            
            with transaction.atomic():
                # Verificar si ya existe un Contact con el mismo primary_email
                contact, created = Contact.objects.get_or_create(
                    primary_email=new_email,
                    defaults={'first_name': first_name, 'last_name': last_name, 'title': title, 'phone': phone, 'mobile_phone': mobile_phone, 'company_name': company_name, 'country': country}
                )

                if not created:
                    # Si el Contact ya existe, actualizarlo
                    contact.first_name = first_name
                    contact.last_name = last_name
                    contact.title = title
                    contact.phone = phone
                    contact.mobile_phone = mobile_phone
                    contact.company_name = company_name
                    contact.country = country
                    contact.save()

                    # Actualizar el Client asociado, si existe
                    try:
                        client = Client.objects.get(primary_email=new_email)
                        client.first_name = first_name
                        client.last_name = last_name
                        client.title = title
                        client.phone = phone
                        client.mobile_phone = mobile_phone
                        client.company_name = company_name
                        client.country = country
                        client.save()

                        # Actualizar todos los Deals asociados
                        for deal in client.client_deals.all():
                            deal.first_name = first_name
                            deal.last_name = last_name
                            deal.title = title
                            deal.phone = phone
                            deal.mobile_phone = mobile_phone
                            deal.company_name = company_name
                            deal.country = country
                            deal.save()

                    except Client.DoesNotExist:
                        # No hay un Client con este primary_email, no se hace nada
                        pass

                # Crear el nuevo Lead
                lead = Lead.objects.create(
                    contact=contact,
                    primary_email=new_email,
                    first_name=first_name,
                    last_name=last_name,
                    title = title,
                    phone = phone,
                    mobile_phone = mobile_phone,
                    company_name = company_name,
                    country = country
                )

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