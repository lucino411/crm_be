class DealUpdateView(UpdateView, AgentRequiredMixin, AgentContextMixin):
    model = Deal
    template_name = 'operation/deal/deal_update.html'
    form_class = DealUpdateForm
    validation_error_handled = False    

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        agent = self.request.user.agent
        current_time = timezone.now()
        # Obtener la instancia del Deal
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
            if deal.stage == 'close_lost':
                deal.is_closed = True 

            # Guardar los formularios de DealProduct
            formset = DealProductFormset(
                self.request.POST, self.request.FILES, instance=deal)

            if formset.is_valid():
                formset.save()

            with transaction.atomic():
                # Captura el antiguo Clinet y la antigua Company asociada al Deal, antes de cualquier cambio
                old_company = deal.company
                old_client = deal.client

                new_email = form.cleaned_data.get('primary_email')
                # Verificar si existe un Client con el nuevo primary_email
                existing_client = Client.objects.filter(primary_email=new_email).first()
                
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

                # Actualizar campos en el Deal
                deal_fields_to_update = [
                    'deal_name',
                    'deal_source',
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
                    'modified_time',                                
                    'start_date_time', 
                    'end_date_time',
                    'extended_end_date_time',
                    'stage'
                ]

                # Si existe Company, relacionamos Company con el Deal, sino creamos Company y lo relacionamos con el Deal
                if existing_company:
                    # Si la Company existe, asignar esta Company al Deal actual
                    deal.company = existing_company                  
                else:
                    # Si no existe, crear una nueva Company
                    new_company=Company.objects.create(
                        company_email=new_company_email,
                        company_name=company_name,
                        company_phone=company_phone,
                        website=website,
                        industry=industry,
                        created_by=agent.user,
                        last_modified_by=last_modified_by,
                        created_time=current_time,                        
                        modified_time=current_time,
                        organization=agent.organization,
                    )
                    deal.company = new_company
                
                # Incluir 'company' en la lista de campos a actualizar
                if 'company' not in deal_fields_to_update:
                    deal_fields_to_update.append('company')

                if existing_client:
                    # Si Client existe, asignar este Client al Deal actual
                    deal.client = existing_client
                else:
                    # Si no existe, crear un nuevo Client
                    new_client=Client.objects.create(
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
                    # Asociar la nueva o existente Company con el nuevo Client
                    new_client.company = deal.company
                    new_client.save(update_fields=['company'])

                    deal.client = new_client
                
                # Incluir 'client' en la lista de campos a actualizar del deal
                if 'client' not in deal_fields_to_update:
                    deal_fields_to_update.append('client')

                # Guardamos el deal con todos los campos a actualizar
                deal.save(update_fields=deal_fields_to_update)              

                # Actualizar Companies y Deals relacionados (company_email)
                if existing_company:
                    # Actualizamos los campos de la Company si company_email existe
                    related_companies = Company.objects.filter(company_email=old_company.company_email)    
                    for company in related_companies:
                        company_fields_to_update = []
                        for field, value in [
                            ('company_email', new_company_email),
                            ('company_name', company_name),
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

                            # Actualizar otros Deals relacionados con Company si company_email existe
                            related_company_deals = Deal.objects.filter(company_email=old_company.company_email) 
                            for deal in related_company_deals:
                                deal.company = deal.company
                                deal_fields_to_update = ['company'] # Inicializamos en 'company'
                                for field, value in [                       
                                    ('company_email', new_company_email),
                                    ('company_name', company_name),
                                    ('company_phone', company_phone),
                                    ('website', website),
                                    ('industry', industry),                     
                                ]:
                                    if getattr(deal, field) != value:
                                        setattr(deal, field, value)
                                        if field not in deal_fields_to_update:
                                            deal_fields_to_update.append(field)

                                if deal_fields_to_update:
                                    # Actualizar el company_id del Client asociado con este Deal específico
                                    client = deal.client 
                                    if client:
                                        client.company = deal.company
                                        client.save(update_fields=['company'])     

                                    deal.save(update_fields=deal_fields_to_update)

                            # Actualizar otros Leads relacionados con Company si company_email existe
                            related_company_leads = Lead.objects.filter(company_email=old_company.company_email) 
                            for lead in related_company_leads:
                                lead.company = deal.company
                                lead_fields_to_update = ['company'] # Inicializamos en 'company'
                                for field, value in [                       
                                    ('company_email', new_company_email),
                                    ('company_name', company_name),
                                    ('company_phone', company_phone),
                                    ('website', website),
                                    ('industry', industry),                     
                                ]:
                                    if getattr(lead, field) != value:
                                        setattr(lead, field, value)
                                        if field not in lead_fields_to_update:
                                            lead_fields_to_update.append(field)

                                if lead_fields_to_update:
                                    # Actualizar el company_id del Contact asociado con este Lead específico
                                    contact = lead.contact 
                                    if contact:
                                        contact.company = lead.company
                                        contact.save(update_fields=['company'])     

                                    lead.save(update_fields=lead_fields_to_update)       

                # Actualiza los otros Deals relacionados con la nueva Company si no existing_company
                else: 
                    # Encuentra todos los Deals que tenían el antiguo company_email
                    old_company_email_deals = Deal.objects.filter(company_email=old_company.company_email)

                    for deal in old_company_email_deals:
                        deal.company = new_company
                        for field, value in [
                            ('company_name', company_name),
                            ('company_email', new_company_email),
                            ('company_phone', company_phone),
                            ('website', website),
                            ('industry', industry),
                        ]:
                            if getattr(deal, field) != value:
                                setattr(deal, field, value)
                                if field not in deal_fields_to_update:
                                    deal_fields_to_update.append(field)
                        
                        if deal_fields_to_update:
                            # Actualizar el company_id del Client asociado con este Deal específico
                            client = deal.client 
                            if client:
                                client.company = deal.company
                                client.save(update_fields=['company'])     

                            deal.save(update_fields=deal_fields_to_update)

                    # Actualizar Leads relacionados con la nueva Company
                    old_company_email_leads = Lead.objects.filter(company_email=old_company.company_email)
                    for lead in old_company_email_leads:
                        lead.company = new_company
                        lead_fields_to_update = ['company'] # Inicializamos con 'company'
                        for field, value in [
                            ('company_name', company_name),
                            ('company_email', new_company_email),
                            ('company_phone', company_phone),
                            ('website', website),
                            ('industry', industry),
                        ]:
                            if getattr(lead, field) != value:
                                setattr(lead, field, value)
                                if field not in lead_fields_to_update:
                                    lead_fields_to_update.append(field)
                        
                        if lead_fields_to_update:
                            # Actualizar el company_id del Contact asociado con este Lead específico
                            contact = lead.contact 
                            if contact:
                                contact.company = lead.company
                                contact.save(update_fields=['company'])     

                            lead.save(update_fields=lead_fields_to_update)         

               # EXISTING OR NOT CLIENTS AND CONTACTS (primary_email)
                            
                # Actualizar Contacts, Clients, Deals y Leads relacionados (primary_email)
                if existing_client:
                    # Actualizar Clients relacionados (primary_email)
                    related_clients = Client.objects.filter(primary_email=old_client.primary_email).exclude(pk=deal.pk)
                    for client in related_clients:
                        client_fields_to_update = []
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
                            if getattr(client, field) != value:
                                setattr(client, field, value)
                                client_fields_to_update.append(field)                  

                        if client_fields_to_update:
                            client.save(update_fields=client_fields_to_update)          

                            # Buscar y actualizar los Contact correspondientes
                            try:
                                # related_contacts = Contact.objects.filter(primary_email=old_client.primary_email).exclude(pk=deal.pk)
                                related_contacts = Contact.objects.filter(primary_email=old_client.primary_email)
                                for contact in related_contacts:                                               
                                    for field in client_fields_to_update:
                                        if field != 'company':
                                            setattr(contact, field, getattr(client, field))
                                    if existing_company:
                                        # Si la Company existe, asignar esta Company al Contact actual
                                        contact.company = existing_company
                                        # Incluir 'company' en la lista de campos a actualizar
                                        if 'company' not in client_fields_to_update:
                                            client_fields_to_update.append('company')
                                    # setattr(client, field, getattr(contact, field))
                                    contact.save()

                                    # Actualizar todos los Leads relacionados con este Contact
                                    related_leads = contact.contact_leads.all()
                                    for lead in related_leads:
                                        for field in client_fields_to_update:
                                            setattr(lead, field, getattr(contact, field))
                                        lead.save()

                            except Contact.DoesNotExist:
                                # No hay un Client con este primary_email, no se necesita hacer nada más
                                pass        

                    # Actualizar otros Deals relacionados (primary_email)
                    related_deals = Deal.objects.filter(primary_email=old_client.primary_email)
                    for deal in related_deals:
                        deal_fields_to_update = []
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
                            if getattr(deal, field) != value:
                                setattr(deal, field, value)
                                deal_fields_to_update.append(field)

                        if deal_fields_to_update:
                            deal.save(update_fields=deal_fields_to_update)

                # Actualiza los otros Deals relacionados con el nuevo Client
                else:                      
                    old_primary_email_deals = Deal.objects.filter(primary_email=old_client.primary_email)
                    for deal in old_primary_email_deals:
                        # Actualizar el company_id del Client asociado con este Deal específico  
                        deal.client = new_client
                        # Lista de campos a actualizar
                        deal_fields_to_update = ['client']  # Inicializar con 'client'
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
                            if getattr(deal, field) != value:
                                setattr(deal, field, value)
                                deal_fields_to_update.append(field)

                        if deal_fields_to_update:
                            deal.save(update_fields=deal_fields_to_update)

                    # Comprobar si el nuevo email ya existe en Contact o Lead
                    email_exists_in_contact = Contact.objects.filter(primary_email=new_email).exists()
                    email_exists_in_lead = Lead.objects.filter(primary_email=new_email).exists()
                    
                    if email_exists_in_contact or email_exists_in_lead:
                        # Buscar y actualizar los Contact correspondientes
                        try:
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

                                # Actualizar todos los Leads relacionados con este Contact
                                related_leads = contact.contact_leads.all()
                                for lead in related_leads:
                                    for field in contact_fields_to_update:
                                        setattr(lead, field, getattr(contact, field))
                                    lead.save()

                        except Contact.DoesNotExist:
                            # No hay un Client con este primary_email, no se necesita hacer nada más
                            pass     

                    else: 
                        try:
                            # Filtrar Contacts que tienen el nuevo email o el email antiguo del Client
                            related_contacts = Contact.objects.filter(Q(primary_email=new_email) | Q(primary_email=old_client.primary_email))
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

                                # Actualizar todos los Leads relacionados con este Contact
                                related_leads = contact.contact_leads.all()
                                for lead in related_leads:
                                    for field in contact_fields_to_update:
                                        setattr(lead, field, getattr(contact, field))
                                    lead.save()

                        except Contact.DoesNotExist:
                            # No hay un Client con este primary_email, no se necesita hacer nada más
                            pass                      

                # ELIMINA Company Y Client QUE NO TENGAN DEALS RELACIONADOS

                # Buscar todas las Company que no tienen Leads ni Deals relacionados
                companies_to_check = Company.objects.annotate(
                    num_leads=Count('company_leads'),
                    num_deals=Count('company_deals')
                )
                # Filtra las Company que no tienen ni Leads ni Deals
                companies_without_leads_and_deals = companies_to_check.filter(num_leads=0, num_deals=0)
                # Elimina las Company que cumplen con la condición
                companies_without_leads_and_deals.delete()

                # Buscar todos los Client que no tienen Deals asociados
                clients_without_deals = Client.objects.annotate(num_deals=Count('client_deals')).filter(num_deals=0)
                # Eliminar estos Client
                clients_without_deals.delete()

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
            'deal_pk': deal.id,  # ID del deal
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
        if deal.stage == 'close_lost':
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

        # VALIDACIONES PARA FORMSET        
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