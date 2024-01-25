# from django.utils import timezone
# # from pydantic import ValidationError
# import re  # Importa el módulo re para trabajar con expresiones regulares
# from django.core.validators import RegexValidator

from django import forms
from django.contrib.auth.models import User

from .models import Lead, LeadProduct, LeadTask
from configuration.country.models import Country
from configuration.currency.models import Currency
from configuration.product.models import Product

class LeadForm(forms.ModelForm):
    lead_name = forms.CharField(
        label="Lead Name", 
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lead Name'})
    )
    lead_source = forms.ChoiceField(
        choices=Lead.LEAD_SOURCE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Lead Source",
        required=False
    )
    primary_email = forms.EmailField(
        label="Email", 
        widget=forms.EmailInput(attrs={'id': "addLeadUnregisterEmail", 'class': 'form-control', 'placeholder': 'Email'}),
        error_messages={
            'unique': 'Este email ya está en uso. Por favor, proporciona un email diferente.',
            'invalid': 'Por favor, introduce un email válido.'
    })
    first_name = forms.CharField(
        label="First Name", 
        max_length=100, 
        widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        label="Last Name", 
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    title = forms.ChoiceField(
        choices=Lead.TITLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Title",
        required=False
    )
    phone = forms.CharField(
        label="Phone",
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
        required=False
    )
    mobile_phone = forms.CharField(
        label="Mobile Phone",
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Phone Number'}),
        required=False
    )
    # Nuevos campos agregados
    company_name = forms.CharField(
        label="Company Name",
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
        required=False
    )
    company_email = forms.EmailField(
        label="Company Email", 
        widget=forms.EmailInput(attrs={'id': "addLeadCompanyEmail", 'class': 'form-control', 'placeholder': 'Company Email'}),
        error_messages={
            'unique': 'Este email ya está en uso. Por favor, proporciona un email diferente.',
            'invalid': 'Por favor, introduce un email válido.'
    })
    company_phone = forms.CharField(
        label="Company Phone",
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Phone'}),
        required=False
    )
    website = forms.URLField(
        label="Website",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'example.com'}),
        required=False,
        error_messages={
            'invalid': 'Por favor, introduce una URL válida, ej. pagina.com',
        }
    )
    def clean_website(self):
        website = self.cleaned_data.get('website')
        if website:
            if website.startswith('http://'):
                # Reemplazar http:// por https://
                website = 'https://' + website[len('http://'):]
            elif not website.startswith('https://'):
                # Añadir https:// si no comienza con http:// o https://
                website = 'https://' + website
        return website    
    industry = forms.ChoiceField(
        choices=Lead.INDUSTRY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Industry",
        required=False
    )
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(), 
        widget=forms.Select(
        attrs={'class': 'form-select'})
    )
    currency = forms.ModelChoiceField(
        queryset=Currency.objects.all(), 
        empty_label=None, 
        widget=forms.Select(attrs={'class': 'form-select'})
    )    
    description = forms.CharField(
        label="Description",
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description', 'rows': 3}),
        required=False,
        max_length=280  # Asumiendo que es la misma longitud que Twitter
    )  
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.all(), 
        empty_label=None, 
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
    )
    end_date_time = forms.DateTimeField(
        required=False, 
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
    )   

    class Meta:
        model = Lead        
        fields = [
                    'lead_name', 'lead_source', 'primary_email', 'first_name', 'last_name', 'title', 'phone', 'mobile_phone', 'company_name', 'company_email', 
                    'company_phone', 'website', 'industry', 'country', 'currency', 'description', 'assigned_to', 'start_date_time', 'end_date_time'
                ]
        
         
class LeadUpdateForm(forms.ModelForm):
    lead_name = forms.CharField(
        label="Lead Name", 
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lead Name'})
    )
    lead_source = forms.ChoiceField(
        choices=Lead.LEAD_SOURCE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Lead Source",
        required=False
    )
    primary_email = forms.EmailField(
        label="Email", 
        widget=forms.EmailInput(attrs={'id': "addLeadUnregisterEmail", 'class': 'form-control', 'placeholder': 'Email'}),
        error_messages={
            'unique': 'Este email ya está en uso. Por favor, proporciona un email diferente.',
            'invalid': 'Por favor, introduce un email válido.'
    })
    first_name = forms.CharField(
        label="First Name", 
        max_length=100, 
        widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        label="Last Name", 
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    title = forms.ChoiceField(
        choices=Lead.TITLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Title",
        required=False
    )
    phone = forms.CharField(
        label="Phone",
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
        required=False
    )
    mobile_phone = forms.CharField(
        label="Mobile Phone",
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Phone Number'}),
        required=False
    )
    company_name = forms.CharField(
        label="Company Name",
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
        required=False
    )
    company_email = forms.EmailField(
        label="Company Email", 
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Company Email'}),
        error_messages={
            'unique': 'Este email ya está en uso. Por favor, proporciona un email diferente.',
            'invalid': 'Por favor, introduce un email válido.'
    })
    company_phone = forms.CharField(
        label="Company Phone",
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Phone'}),
        required=False
    )
    website = forms.URLField(
        label="Website",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'example.com'}),
        required=False,
        error_messages={
            'invalid': 'Por favor, introduce una URL válida, ej. pagina.com',
        }
    )
    def clean_website(self):
        website = self.cleaned_data.get('website')
        if website:
            if website.startswith('http://'):
                # Reemplazar http:// por https://
                website = 'https://' + website[len('http://'):]
            elif not website.startswith('https://'):
                # Añadir https:// si no comienza con http:// o https://
                website = 'https://' + website
        return website    
    industry = forms.ChoiceField(
        choices=Lead.INDUSTRY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Industry",
        required=False
    )
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(), 
        widget=forms.Select(
        attrs={'class': 'form-select'})
    )
    currency = forms.ModelChoiceField(
        queryset=Currency.objects.all(), 
        empty_label=None, 
        widget=forms.Select(attrs={'class': 'form-select'})
    )    
    description = forms.CharField(
        label="Description",
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description', 'rows': 3}),
        required=False,
        max_length=280  # Asumiendo que es la misma longitud que Twitter
    )  
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.all(), 
        empty_label=None, 
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
    )
    end_date_time = forms.DateTimeField(
        required=False, 
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
    )  
    extended_end_date_time = forms.DateTimeField(
        required=False, 
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
    )
    stage = forms.ChoiceField(
        choices=Lead.STAGE_CHOICES, 
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Lead
        fields = [
                    'lead_name', 'lead_source', 'primary_email', 'first_name', 'last_name', 'title', 'phone', 'mobile_phone', 'company_name', 'company_email', 
                    'company_phone', 'website', 'industry', 'country', 'currency', 'description', 'assigned_to', 'start_date_time', 'end_date_time', 'extended_end_date_time', 'stage'
                ]
        

class LeadProductForm(forms.ModelForm):
    # Este campo es para seleccionar un producto existente en la organizacion
    product = forms.ModelChoiceField(queryset=Product.objects.all(
    ), widget=forms.Select(attrs={'class': 'form-select'}), label="Product")
    # Campo para la URL de cotización específica del LeadProduct
    cotizacion_url = forms.URLField(required=False, widget=forms.URLInput(
        attrs={'class': 'form-control', 'placeholder': 'Cotización URL'}), label="Cotización URL")
    
    def __init__(self, *args, **kwargs):
        organization = kwargs.pop('organization', None)  # Extraer la organización del arumento
        super(LeadProductForm, self).__init__(*args, **kwargs)
        if organization:
            # Filtrar el queryset del campo 'product' por la organización
            self.fields['product'].queryset = Product.objects.filter(organization=organization)

    class Meta:
        model = LeadProduct
        fields = ['product', 'cotizacion_url']


class LeadTaskCreateForm(forms.ModelForm):
    name = forms.CharField(
        label="Lead Name", 
        max_length=200, 
        widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Task Name'})
    )
    description = forms.CharField(
        widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': 'Task Description'})
    )
    lead = forms.ModelChoiceField(
        queryset=Lead.objects.all(), 
        required=False, 
        widget=forms.Select(
        attrs={'class': 'form-select'}), 
        label="Lead"
    )
    lead_product = forms.ModelChoiceField(
        queryset=LeadProduct.objects.all(), 
        required=False, 
        widget=forms.Select(
        attrs={'class': 'form-select'}), 
        label="Lead Product"
    )
    parent_task = forms.ModelChoiceField(
        queryset=LeadTask.objects.all(), 
        required=False, 
        widget=forms.Select(
        attrs={'class': 'form-select'}), 
        label="Parent Task"
    )
    parent_task_id = forms.IntegerField(
        widget=forms.HiddenInput(), 
        required=False
    ) # Captura el id del parent_task que se envia por la url desde LeadTaskUpdateView
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.all(), 
        empty_label=None, 
        widget=forms.Select(attrs={'class': 'form-select'}), 
        label="Assigned To"
    )         
    
    # def __init__(self, *args, **kwargs):
    #     super(LeadTaskCreateForm, self).__init__(*args, **kwargs)
    #     self.fields['parent_task'].choices = [('', 'Seleccione una opción')] + list(self.fields['parent_task'].choices)[1:]
    #     self.fields['parent_task'].empty_label = None

    class Meta:
        model = LeadTask
        fields = ['name', 'description', 'lead', 'lead_product', 'parent_task', 'assigned_to']
        

class LeadTaskUpdateForm(forms.ModelForm):
    name = forms.CharField(label="", max_length=200, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Task Name'}))
    description = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': 'Task Description'}))
    lead = forms.ModelChoiceField(queryset=Lead.objects.all(), required=False, widget=forms.Select(
        attrs={'class': 'form-select'}), label="Lead")
    lead_product = forms.ModelChoiceField(queryset=LeadProduct.objects.all(), required=False, widget=forms.Select(
        attrs={'class': 'form-select'}), label="Lead Product")
    parent_task = forms.ModelChoiceField(queryset=LeadTask.objects.all(), required=False, widget=forms.Select(
        attrs={'class': 'form-select'}), label="Parent Task")
    assigned_to = forms.ModelChoiceField(queryset=User.objects.all(), empty_label=None, widget=forms.Select(
        attrs={'class': 'form-select'}), label="Assigned To")
    stage = forms.ChoiceField(choices=LeadTask.STAGE_CHOICES, widget=forms.Select(
        attrs={'class': 'form-select'}))      

    class Meta:
        model = LeadTask
        fields = ['name', 'description', 'lead', 'lead_product', 'parent_task', 'assigned_to', 'stage']

