from django.views.generic import TemplateView, ListView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import FormView
from django.forms import inlineformset_factory
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.db.models import Count, Q
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.core.exceptions import ValidationError

from administration.userprofile.views import AgentRequiredMixin, AgentContextMixin
from configuration.country.models import Country
from operation.lead.models import Lead
from operation.company.models import Company
from operation.client.models import Client
from operation.contact.models import Contact
from .models import Deal, DealProduct, DealTask
from .forms import DealProductForm, DealTaskCreateForm, DealTaskUpdateForm, DealUpdateForm


DealProductFormset = inlineformset_factory(Deal, DealProduct, form=DealProductForm, extra=0, can_delete=True)


class HomeDealView(LoginRequiredMixin, TemplateView):
    template_name = 'operation/deal/deal_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Gestion de Deals'
        return context

# Query de Deals de la base de datos enviada a JS como JSON para las Datatables JS
class DealListView(ListView, AgentRequiredMixin, AgentContextMixin):
    model = Deal

    def get_queryset(self):
        deals = Deal.objects.filter(organization=self.get_organization())
        return deals

    def get(self, request, *args, **kwargs):
        deals = self.get_queryset()
        deals_data = list(deals.values('id', 'deal_name', 'first_name', 'last_name', 'primary_email',
                                       'country', 'created_time', 'last_modified_by_id', 'assigned_to_id', 'organization'))
        country_names = {
            country.id: country.name for country in Country.objects.all()
        }
        user_names = {
            user.id: f"{user.first_name} {user.last_name}" for user in User.objects.all()
        }
        for deal in deals_data:
            deal['country'] = country_names.get(deal['country'])
            deal['assigned_to'] = user_names.get(deal['assigned_to_id'])
            deal['last_modified_by'] = user_names.get(
                deal['last_modified_by_id'])
            # deal['created_by'] = user_names.get(deal['created_by_id'])
            deal['organization'] = self.get_organization().name

        return JsonResponse({'deals': deals_data})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization_name'] = self.get_organization().name
        return context


class DealDetailView(DetailView, AgentRequiredMixin, AgentContextMixin):
    model = Deal
    template_name = 'operation/deal/deal_detail.html'
    context_object_name = 'deal'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Detail Deal'
        context['organization_name'] = self.get_organization()
        # Añadir productos asociados al Deal
        deal_products = DealProduct.objects.filter(deal=self.object)
        context['deal_products'] = deal_products
         # Obtener tareas asociadas al Deal
        deal_tasks = DealTask.objects.filter(deal=self.object)
        context['deal_tasks'] = deal_tasks

        return context
    

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
                print('heeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
                print('deal_name =', deal_name)
                print('deal_source =', deal_source)
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

                            deal.save(update_fields=deal_fields_to_update)
                        
                    # Actualizar el company_id del Client asociado con este Deal específico
                    client = deal.client 
                    if client:
                        client.company = deal.company
                        client.save(update_fields=['company'])  

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



  

# class DealDeleteView(DeleteView, AgentRequiredMixin, AgentContextMixin):
#     model = Deal
#     template_name = 'operation/deal/deal_delete.html'
#     context_object_name = 'deal'

#     def get_success_url(self):
#         messages.success(self.request, "Deal Deleted.")
#         return reverse_lazy('deal:list', kwargs={'organization_name': self.get_organization()})

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['titulo'] = 'Delete Deal'
#         context['organization_name'] = self.get_organization()
#         return context

class DealDeleteView(DeleteView, AgentRequiredMixin, AgentContextMixin):
    model = Deal
    template_name = 'operation/deal/deal_delete.html'
    context_object_name = 'deal'

    def form_valid(self, form):
        with transaction.atomic():
            self.object = self.get_object()
            client = self.object.client

            # Verificar si el Contact está asociado con otros Lead
            if client and client.client_leads.count() <= 1:
                # Si solo está asociado con este Lead, eliminar el Contact
                client.delete()

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

            # Buscar todos los Contact que no tienen Leads asociados
            contacts_without_deals = Contact.objects.annotate(num_leads=Count('contact_leads')).filter(num_leads=0)
            # Eliminar estos Contacts
            contacts_without_deals.delete()

        response = super(DealDeleteView, self).form_valid(form)
        messages.success(self.request, "Deal Deleted.")
        return response

    def get_success_url(self):  
        return reverse_lazy('lead:list', kwargs={'organization_name': self.get_organization()})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Delete Lead'
        context['organization_name'] = self.get_organization()
        return context




# # ************
#   # CUR TASK
# # ************


class DealHomeTaskView(LoginRequiredMixin, TemplateView):
    template_name = 'operation/dealtask/task_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Gestion de Tasks Deals'
        return context


# Query de Tasks de la base de datos enviada a JS como JSON para las Datatables JS
class DealTaskListView(ListView, AgentRequiredMixin, AgentContextMixin):
    model = DealTask

    def get_queryset(self):
        return DealTask.objects.filter(
            organization=self.get_organization()
        ).select_related('assigned_to', 'last_modified_by')
    
    def get(self, request, *args, **kwargs):
        tasks = self.get_queryset()
        tasks_data = list(tasks.values('id', 'name', 'last_modified_by_id',
                          'assigned_to_id', 'organization', 'modified_time', 'created_by_id', 'deal_product__product__name', 'deal__deal_name'))
        user_names = {
            user.id: f"{user.first_name} {user.last_name}" for user in User.objects.all()
        }

        for task in tasks_data:
            task['created_by'] = user_names.get(task['created_by_id'])
            task['assigned_to'] = user_names.get(task['assigned_to_id'])
            task['last_modified_by'] = user_names.get(task['last_modified_by_id'])
            task['organization'] = self.get_organization().name
            task['product_name'] = task['deal_product__product__name']  # Asigna el nombre del producto a una nueva clave
            task['deal_name'] = task['deal__deal_name']  # Nombre del deal

        return JsonResponse({'tasks': tasks_data})


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization_name'] = self.get_organization().name
        return context


class DealTaskCreateView(FormView, AgentRequiredMixin, AgentContextMixin):
    model = DealTask
    template_name = 'operation/dealtask/task_create.html'
    form_class = DealTaskCreateForm
    validation_error_handled = False

    def get_form(self, form_class=None):
        form = super().get_form(form_class)       
        agent = self.request.user.agent
        deal_id = self.kwargs.get('deal_pk')
        deal = get_object_or_404(Deal, pk=deal_id)
       
        if agent:
            # Configuración de queryset para los campos que dependen del agente
            form.fields['assigned_to'].queryset = User.objects.filter(
                agent__organization=agent.organization)        
            
        if deal:
            # Filtra los productos del deal
            form.fields['deal_product'].queryset = DealProduct.objects.filter(deal=deal)       

            # Preparando el queryset de tareas relacionadas al deal y excluyendo parent tasks y sub-tareas
            # Excluir las tareas que son subtask
            tasks_to_exclude = DealTask.objects.filter(parent_task__isnull=False).values_list('id', flat=True)

            # Filtrar tareas elegibles para ser parent_task
            eligible_tasks = DealTask.objects.filter(
                deal=deal
            ).exclude(
                id__in=tasks_to_exclude
            )

            # Si no hay tareas elegibles, ocultar el campo parent_task
            if not eligible_tasks.exists():
                del form.fields['parent_task']
            else:
                form.fields['parent_task'].queryset = eligible_tasks
          
            # Muestra el parent_task si se está creando una subtarea desde otra tarea
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

            # Capturar el ID del Deal desde la URL
            deal_id = self.kwargs.get('deal_pk')
            # Obtener el objeto Deal
            deal = get_object_or_404(Deal, pk=deal_id)
            # Asegura que el Deal con este ID existe para evitar errores
            if deal:
                task.deal = get_object_or_404(Deal, pk=deal_id)
                 # Obtiene el ID de parent_task desde la URL (si existe)
                parent_task_id = form.cleaned_data.get('parent_task_id')             
                if parent_task_id:
                    try:
                        parent_task_id = int(parent_task_id)  # Convierte a entero
                        # Asigna el objeto parent_task al task actual
                        task.parent_task = DealTask.objects.get(id=parent_task_id)
                        # task.parent_task = parent_task_id
                    except (ValueError, DealTask.DoesNotExist):
                        # Manejar el caso en que parent_task_id no sea un entero o no exista
                        messages.error(self.request, "Parent Task inválido.")
                        return self.form_invalid(form)

                messages.success(self.request, "Task creada correctamente")
                # Guarda el objeto Task
                task.save()                   
                
            else:
                # Cuando no tenga un deal asociado
                messages.error(
                    self.request, "El Task no tiene un Deal asociado.")
                return self.form_invalid(form)

            # Redirige a una URL específica después de la creación, como la página update del deal asociado
            url = reverse('deal:task-list', kwargs={
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
        task = get_object_or_404(DealTask, pk=current_task_id)
        deal = task.deal

        if not self.validation_error_handled:
            messages.error(
                self.request, "Invalid form data. Please check the entries and try again.")
        return render(self.request, self.template_name, {
            'form': form,
            'organization_name': self.get_organization(),
            'deal_pk': deal.id,
        })   


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        # Obtener el ID del Deal de los argumentos de la URL
        deal_id = self.kwargs.get('deal_pk')
        deal = get_object_or_404(Deal, pk=deal_id)  # Obtener el objeto Deal

        # Componer el título y añadirlo al contexto
        if deal.deal_name:
            context['titulo'] = f"Crear Task for {deal.deal_name}"
        else:
            context['titulo'] = "Crear Task"
        context['deal'] = deal
        context['deal_name'] = deal.deal_name if deal else None
        context['deal_pk'] = deal_id
        context['organization_name'] = self.get_organization()

        return context
    

class DealTaskDetailView(DetailView, AgentRequiredMixin, AgentContextMixin):
    model = DealTask
    template_name = 'operation/dealtask/task_detail.html'
    context_object_name = 'task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Deal Detail Task'
        context['organization_name'] = self.get_organization()
       # Obtener el producto asociado a la tarea
        task = context['task']  # Esta es la instancia de Task que DetailView está mostrando
        task_product = None  # Inicializa como None por si no hay producto asociado        
        # Verifica si la tarea tiene un deal_product y, por lo tanto, un producto
        if task.deal_product:
            task_product = task.deal_product.product.name  # Sigue la relación hasta llegar al nombre del producto
        context['task_product'] = task_product  # Agrega el producto al contexto

         # Obtener todas las subtareas asociadas a esta tarea
        subtasks = task.parent_dealtask.all()  # Usa la relación inversa definida por 'related_name'
        # Agrega las subtareas al contexto
        context['subtasks'] = subtasks

        # Verifica si la tarea actual es una subtarea y tiene una tarea padre
        if task.parent_task:
            context['parent_task'] = task.parent_task
        else:
            context['parent_task'] = None  # O asignar un valor por defecto si no hay tarea padre
            
  
        return context
    

class DealTaskDeleteView(DeleteView, AgentRequiredMixin, AgentContextMixin):
    model = DealTask
    template_name = 'operation/dealtask/task_delete.html'
    context_object_name = 'task'

    def get_success_url(self):
        messages.success(self.request, "Task Deleted.")
        return reverse_lazy('deal:task-list', kwargs={'organization_name': self.get_organization()})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Delete Task'
        context['organization_name'] = self.get_organization()
        return context


class DealTaskUpdateView(UpdateView, AgentRequiredMixin, AgentContextMixin):
    model = DealTask
    template_name = 'operation/dealtask/task_update.html'
    form_class = DealTaskUpdateForm
    validation_error_handled = False

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        agent = self.request.user.agent
        current_task_id = self.kwargs.get('pk')  # ID de la tarea actual
        task = get_object_or_404(DealTask, pk=current_task_id)
        deal = task.deal  # Obteniendo el deal asociado a la tarea

        if agent:
            # Configuración de queryset para los campos que dependen del agente
            form.fields['assigned_to'].queryset = User.objects.filter(
                agent__organization=agent.organization)            
        
        if deal:
            # Filtra los productos del deal
            form.fields['deal_product'].queryset = DealProduct.objects.filter(deal=deal)

            # Preparando el queryset de tareas relacionadas al deal y excluyendo la tarea actual, parent tasks y sub-tareas
            # Seleccionamos la tarea actual
            current_task_id = self.kwargs.get('pk')
            current_task = get_object_or_404(DealTask, pk=current_task_id)

            # Excluir la tarea actual y las tareas que son subtask
            tasks_to_exclude = DealTask.objects.filter(parent_task__isnull=False).values_list('id', flat=True)
            tasks_to_exclude = list(tasks_to_exclude) + [current_task_id]

            # Ajustar el queryset del campo parent_task
            form.fields['parent_task'].queryset = DealTask.objects.filter(
                deal=current_task.deal
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
            if DealTask.objects.filter(parent_task=current_task).exists():
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
            task = get_object_or_404(DealTask, pk=current_task_id)
            task.organization = agent.organization
            task.created_by = agent.user
            task.last_modified_by = agent.user
            deal = task.deal  # Obteniendo el deal asociado a la tarea
            current_time = timezone.now()
            
            # Asegura que el Deal con este ID existe para evitar errores
            if deal:
                task = form.save(commit=False)
                task.deal = get_object_or_404(Deal, pk=deal.id) 

                if deal.is_closed:
                    messages.error(self.request, "El Deal esta cerrado.")
                    return self.form_invalid(form)            
                
                # Validaciones basadas en el estado de la tarea
                if task.is_closed:
                    messages.error(self.request, "La tarea esta cerrada.")
                    return self.form_invalid(form)
                # Validaciones basadas en las fechas de cierre del Deal
                if deal.extended_end_date_time and deal.extended_end_date_time < current_time:
                    # Implementa la lógica adecuada si el deal ha pasado su fecha extendida de cierre
                    messages.error(self.request, "El Deal esta cerrado.")
                    return self.form_invalid(form) 
                elif deal.end_date_time and deal.end_date_time < current_time and not deal.extended_end_date_time:
                    messages.error(self.request, "El Deal esta cerrado.")
                    return self.form_invalid(form)    

                # Logica para establecer el stage is_closed"
                if task.stage in ['completed', 'canceled']:
                    task.is_closed = True
                    # También marcar como cerrada las subtareas si la tarea principal está cerrada
                    for subtask in task.parent_dealtask.all():
                        subtask.is_closed = True 
                        subtask.save()
             
                # Guarda el objeto Task                
                messages.success(self.request, "Task editada correctamente")
                task.save()

            else:
                # Cuando no tenga un deal asociado
                messages.error(
                    self.request, "El Task no tiene un Deal asociado.")
                return self.form_invalid(form)

            # Redirige a una URL específica después de editar la tarea, como la página update del deal asociado
            url = reverse('deal:task-update', kwargs={
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
        task = get_object_or_404(DealTask, pk=current_task_id)
        deal = task.deal
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
        # Si se está pasando un ID de tarea parent como parámetro para crear una subtarea
        context['parent_task_id'] = self.request.GET.get('parent_task')
        current_time = timezone.now()
        # Obtener el ID del Deal de los argumentos de la URL
        current_task_id = self.kwargs.get('pk')  # ID de la tarea actual
        task = get_object_or_404(DealTask, pk=current_task_id)
        deal = task.deal  # Obteniendo el deal asociado a la tarea
        # Componer el título y añadirlo al contexto
        if deal.deal_name:
            context['titulo'] = f"Crear Task for {deal.deal_name}"
        else:
            context['titulo'] = "Crear Task"
        context['task'] = task
        context['deal'] = deal
        context['deal_pk'] = deal.id
        context['pk'] = current_task_id
        context['deal_name'] = deal.deal_name if deal else None
        context['organization_name'] = self.get_organization()

        # Determina si deshabilia los botones del formulario
        context['enable_button'] = True

        # Verificar si la tarea actual no es una subtask (no tiene parent_task)
        if not task.parent_task:
            # Habilitar el botón si también se cumple la condición de la fecha del deal
            context['enable_button'] = True
        else:
            context['enable_button'] = False

        if deal.extended_end_date_time and deal.extended_end_date_time < current_time:
            context['enable_button'] = False

        if deal.end_date_time and not deal.extended_end_date_time and deal.end_date_time < current_time:
            context['enable_button'] = False

        # datos para validar habilitar o deshabilitar los campos del formulario con JS de acuerdo al estado del deal y la tarea
        context['is_deal_closed'] = deal.is_closed
        context['is_task_closed'] = task.is_closed
        context['extended_end_date_time'] = deal.extended_end_date_time
        context['end_date_time'] = deal.end_date_time


        return context