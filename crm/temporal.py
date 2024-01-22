            with transaction.atomic():
                new_email = form.cleaned_data.get('primary_email')
                lead_name = form.cleaned_data.get('lead_name')
                lead_source = form.cleaned_data.get('lead_source')
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                title = form.cleaned_data.get('title')
                phone = form.cleaned_data.get('phone')
                mobile_phone = form.cleaned_data.get('mobile_phone')
                company_name = form.cleaned_data.get('company_name')
                new_company_email = form.cleaned_data.get('company_email')
                company_phone = form.cleaned_data.get('company_phone')
                website = form.cleaned_data.get('website')
                industry = form.cleaned_data.get('industry')
                country = form.cleaned_data.get('country')
                currency = form.cleaned_data.get('currency')
                description = form.cleaned_data.get('description')
                assigned_to = form.cleaned_data.get('assigned_to')
                last_modified_by = agent.user
                start_date_time = form.cleaned_data.get('start_date_time')
                end_date_time = form.cleaned_data.get('end_date_time')   

                # Actualizar campos en el Lead
                lead_fields_to_update = [
                    'lead_name',
                    'lead_source',
                    'primary_email', 
                    'first_name',
                    'last_name',
                    'title',
                    'phone',
                    'mobile_phone', 
                    'company_name',
                    'company_email',
                    'company_phone', 
                    'website', 
                    'industry',          
                    'country', 
                    'currency', 
                    'description', 
                    'assigned_to', 
                    'last_modified_by',                                    
                    'start_date_time', 
                    'end_date_time',
                    'extended_end_date_time',
                    'stage'
                ]
                lead.save(update_fields=lead_fields_to_update)         

                # Actualizar otros Leads relacionados (primary_email)
                related_leads = Lead.objects.filter(primary_email=new_email)
                for lead in related_leads:
                    lead_fields_to_update = []
                    for field, value in [
                        ('primary_email', new_email),
                        ('first_name', first_name),
                        ('last_name', last_name),
                        ('title', title),
                        ('phone', phone),
                        ('mobile_phone', mobile_phone),                      
                        ('country', country),
                        ('currency', currency),
                        ('last_modified_by', last_modified_by),
                        ('modified_time', current_time),
                    ]:
                        if getattr(lead, field) != value:
                            setattr(lead, field, value)
                            lead_fields_to_update.append(field)

                    if lead_fields_to_update:
                        lead.save(update_fields=lead_fields_to_update)        

                # Actualizar Compañías relacionadas (company_email)
                related_companies = Company.objects.filter(company_email=new_company_email).exclude(pk=lead.pk)            
                for company in related_companies:
                    company_fields_to_update = []
                    for field, value in [
                        ('company_name', company_name),
                        ('company_email', new_company_email),
                        ('company_phone', company_phone),
                        ('website', website),
                        ('industry', industry),
                        ('last_modified_by', last_modified_by),
                        ('modified_time', current_time),
                    ]:
                        if getattr(company, field) != value:
                            setattr(company, field, value)
                            company_fields_to_update.append(field)

                    if company_fields_to_update:
                        company.save(update_fields=company_fields_to_update)   

                        # Actualizar otros Leads relacionados con Company (companyp_email)
                        related_company_leads = Lead.objects.filter(company_email=new_company_email).exclude(pk=lead.pk) 
                        for lead in related_company_leads:
                            lead_fields_to_update = []
                            for field, value in [                       
                                ('company_name', company_name),
                                ('company_email', new_company_email),
                                ('company_phone', company_phone),
                                ('website', website),
                                ('industry', industry),                     
                            ]:
                                if getattr(lead, field) != value:
                                    setattr(lead, field, value)
                                    lead_fields_to_update.append(field)

                            if lead_fields_to_update:
                                lead.save(update_fields=lead_fields_to_update)                           

                # Actualizar Contacts relacionados (primary_email)
                related_contacts = Contact.objects.filter(primary_email=new_email)
                for contact in related_contacts:
                    contact_fields_to_update = []
                    for field, value in [
                        ('primary_email', new_email), 
                        ('first_name', first_name), 
                        ('last_name', last_name), 
                        ('title', title), 
                        ('phone', phone), 
                        ('mobile_phone', mobile_phone), 
                        ('country', country),
                        ('last_modified_by', last_modified_by),
                        ('modified_time', current_time),
                    ]:
                        if getattr(contact, field) != value:
                            setattr(contact, field, value)
                            contact_fields_to_update.append(field)

                    if contact_fields_to_update:
                        contact.save(update_fields=contact_fields_to_update)          

                        # Buscar y actualizar el Client correspondiente
                        try:
                            client = Client.objects.get(primary_email=new_email)
                            for field in contact_fields_to_update:
                                setattr(client, field, getattr(contact, field))
                            client.save()

                            # Actualizar todos los Deals asociados con este Client
                            for deal in client.client_deals.all():
                                for field in contact_fields_to_update:
                                    setattr(deal, field, getattr(client, field))
                                deal.save()

                        except Client.DoesNotExist:
                            # No hay un Client con este primary_email, no se necesita hacer nada más
                            pass              


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










### TEmporal

            with transaction.atomic():
                new_email = form.cleaned_data.get('primary_email')
                # Verificar si existe un Contact con el nuevo primary_email
                existing_contact = Contact.objects.filter(primary_email=new_email).first()


                # Captura la antigua Company asociada al Lead, antes de cualquier cambio
                old_contact = lead.contact

                # Si existe Contact, relacionamos Contact con el Lead, sino creamos Contact y lo relacionamos con el Lead
                if existing_contact:
                    # Si Contact existe, asignar este Contact al Lead actual
                    lead.contact = existing_contact
                else:
                    # Si no existe, crear un nuev Contact
                    new_contact=Contact.objects.create(
                        primary_email=new_email,
                        first_name=first_name,
                        last_name=last_name,
                        title=title,
                        phone=phone,
                        mobile_phone=mobile_phone,
                        country=country,                       
                        created_by=agent.user,
                        last_modified_by=last_modified_by,
                        created_time=current_time,                        
                        modified_time=current_time,
                        organization=agent.organization,
                    )
                    # Asociar la nueva o existente Company con el nuevo Contact
                    new_contact.company = lead.company
                    new_contact.save(update_fields=['company'])

                    lead.contact = new_contact
                
                # Asegurarse de incluir 'contact' en la lista de campos a actualizar del lead
                if 'contact' not in lead_fields_to_update:
                    lead_fields_to_update.append('contact')

                lead.save(update_fields=lead_fields_to_update)   
              
                if existing_contact:
                    # Actualizar Contacts relacionados (primary_email)
                    related_contacts = Contact.objects.filter(primary_email=new_email).exclude(pk=lead.pk)
                    for contact in related_contacts:
                        contact_fields_to_update = []
                        for field, value in [
                            ('primary_email', new_email), 
                            ('first_name', first_name), 
                            ('last_name', last_name), 
                            ('title', title), 
                            ('phone', phone), 
                            ('mobile_phone', mobile_phone), 
                            ('country', country),
                            ('last_modified_by', last_modified_by),
                            ('modified_time', current_time),
                        ]:                
                            if getattr(contact, field) != value:
                                setattr(contact, field, value)
                                contact_fields_to_update.append(field)                  

                        if contact_fields_to_update:
                            contact.save(update_fields=contact_fields_to_update)          

                            # Buscar y actualizar el Client correspondiente
                            try:
                                client = Client.objects.get(primary_email=new_email)
                                for field in contact_fields_to_update:
                                    if existing_company:
                                        # Si la Company existe, asignar esta Company al Lead actual
                                        field.company = existing_company
                                        # Asegurarse de incluir 'company' en la lista de campos a actualizar
                                        if 'company' not in contact_fields_to_update:
                                            contact_fields_to_update.append('company')
                                    setattr(client, field, getattr(contact, field))
                                client.save()

                                # Actualizar todos los Deals asociados con este Client
                                for deal in client.client_deals.all():
                                    for field in contact_fields_to_update:
                                        setattr(deal, field, getattr(client, field))
                                    deal.save()

                            except Client.DoesNotExist:
                                # No hay un Client con este primary_email, no se necesita hacer nada más
                                pass        

                            # Actualizar otros Leads relacionados (primary_email)
                            related_leads = Lead.objects.filter(primary_email=new_email).exclude(pk=lead.pk) 
                            for lead in related_leads:
                                lead_fields_to_update = []
                                for field, value in [
                                    ('primary_email', new_email),
                                    ('first_name', first_name),
                                    ('last_name', last_name),
                                    ('title', title),
                                    ('phone', phone),
                                    ('mobile_phone', mobile_phone),                      
                                    ('country', country),
                                    ('currency', currency),
                                    ('last_modified_by', last_modified_by),
                                    ('modified_time', current_time),
                                ]:
                                    if getattr(lead, field) != value:
                                        setattr(lead, field, value)
                                        lead_fields_to_update.append(field)

                                if lead_fields_to_update:
                                    lead.save(update_fields=lead_fields_to_update)

                else: 
                    # old_primary_email_leads = Lead.objects.filter(contact=old_contact).exclude(pk=lead.pk)   
                    old_primary_email_leads = Lead.objects.filter(contact=old_contact)
                    for lead in old_primary_email_leads:
                        # Actualizar el company_id del Contact asociado con este Lead específico  
                        lead_fields_to_update = []
                        for field, value in [
                            ('primary_email', new_email),
                            ('first_name', first_name),
                            ('last_name', last_name),
                            ('title', title),
                            ('phone', phone),
                            ('mobile_phone', mobile_phone),                      
                            ('country', country),
                            ('currency', currency),
                            ('last_modified_by', last_modified_by),
                            ('modified_time', current_time),
                        ]:
                            if getattr(lead, field) != value:
                                setattr(lead, field, value)
                                lead_fields_to_update.append(field)

                        if lead_fields_to_update:
                            contact = lead.contact 
                            if contact:
                                contact.company = lead.company
                                contact.save(update_fields=['company'])   
                                
                            lead.save(update_fields=lead_fields_to_update)