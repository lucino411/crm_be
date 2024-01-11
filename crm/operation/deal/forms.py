# from django.utils import timezone
# from pydantic import ValidationError
# from .models import Task, User
from .models import User
from django import forms
from django.contrib.auth.models import User

from .models import Deal, DealProduct, DealTask
from configuration.country.models import Country
from configuration.currency.models import Currency
from configuration.product.models import Product

# class DealForm(forms.ModelForm):    
#     deal_name = forms.CharField(
#         label="deal Name", 
#         max_length=100, 
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lead Name'})
#     )
#     first_name = forms.CharField(
#         label="First Name", 
#         max_length=100, 
#         widget=forms.TextInput(
#         attrs={'class': 'form-control', 'placeholder': 'First Name'})
#     )
#     last_name = forms.CharField(
#         label="Last Name", 
#         max_length=100, 
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
#     )
#     primary_email = forms.EmailField(
#         label="Email", 
#         widget=forms.EmailInput(attrs={'id': "addLeadUnregisterEmail", 'class': 'form-control', 'placeholder': 'Email'}),
#         error_messages={
#             'unique': 'Este email ya está en uso. Por favor, proporciona un email diferente.',
#             'invalid': 'Por favor, introduce un email válido.'
#     })
#     country = forms.ModelChoiceField(
#         queryset=Country.objects.all(), 
#         widget=forms.Select(
#         attrs={'class': 'form-select'})
#     )
#     assigned_to = forms.ModelChoiceField(
#         queryset=User.objects.all(), 
#         empty_label=None, 
#         widget=forms.Select(attrs={'class': 'form-select'})
#     )
#     currency = forms.ModelChoiceField(
#         queryset=Currency.objects.all(), 
#         empty_label=None, 
#         widget=forms.Select(attrs={'class': 'form-select'})
#     )
#     start_date_time = forms.DateTimeField(
#         widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
#     )
#     end_date_time = forms.DateTimeField(
#         required=False, 
#         widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
#     )
#     extended_end_date_time = forms.DateTimeField(
#         required=False, 
#         widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
#     )

#     # Nuevos campos agregados
#     company_name = forms.CharField(
#         label="Company Name",
#         max_length=255,
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
#         required=False
#     )
#     industry = forms.ChoiceField(
#         choices=Deal.INDUSTRY_CHOICES,
#         widget=forms.Select(attrs={'class': 'form-select'}),
#         label="Industry",
#         required=False
#     )
#     phone = forms.CharField(
#         label="Phone",
#         max_length=20,
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
#         required=False
#     )
#     mobile_phone = forms.CharField(
#         label="Mobile Phone",
#         max_length=20,
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Phone Number'}),
#         required=False
#     )
#     title = forms.ChoiceField(
#         choices=Deal.TITLE_CHOICES,
#         widget=forms.Select(attrs={'class': 'form-select'}),
#         label="Title",
#         required=False
#     )
#     website = forms.URLField(
#         label="Website",
#         widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
#         required=False
#     )
#     lead_source = forms.ChoiceField(
#         choices=Deal.LEAD_SOURCE_CHOICES,
#         widget=forms.Select(attrs={'class': 'form-select'}),
#         label="Lead Source",
#         required=False
#     )
#     description = forms.CharField(
#         label="Description",
#         widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description', 'rows': 3}),
#         required=False,
#         max_length=280  # Asumiendo que es la misma longitud que Twitter
#     )

#     class Meta:
#         model = Deal
#         fields = [
#                     'deal_name', 'first_name', 'last_name', 'primary_email', 'country', 'assigned_to', 'currency', 'start_date_time', 'end_date_time', 
#                     'extended_end_date_time', 'company_name', 'industry', 'phone', 'mobile_phone', 'title', 'website', 'lead_source', 'description'
#                 ]
        

class DealUpdateForm(forms.ModelForm):
    deal_name = forms.CharField(
        label="deal Name", 
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lead Name'})
    )
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
    primary_email = forms.EmailField(
        label="Email", 
        widget=forms.EmailInput(attrs={'id': "addLeadUnregisterEmail", 'class': 'form-control', 'placeholder': 'Email'}),
        error_messages={
            'unique': 'Este email ya está en uso. Por favor, proporciona un email diferente.',
            'invalid': 'Por favor, introduce un email válido.'
    })
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(), 
        widget=forms.Select(
        attrs={'class': 'form-select'})
    )
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.all(), 
        empty_label=None, 
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    currency = forms.ModelChoiceField(
        queryset=Currency.objects.all(), 
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
    # Nuevos campos agregados
    company_name = forms.CharField(
        label="Company Name",
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
        required=False
    )
    industry = forms.ChoiceField(
        choices=Deal.INDUSTRY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Industry",
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
    title = forms.ChoiceField(
        choices=Deal.TITLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Title",
        required=False
    )
    website = forms.URLField(
        label="Website",
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'example.com'}),
        required=False
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

    lead_source = forms.ChoiceField(
        choices=Deal.LEAD_SOURCE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Lead Source",
        required=False
    )
    description = forms.CharField(
        label="Description",
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description', 'rows': 3}),
        required=False,
        max_length=280  # Asumiendo que es la misma longitud que Twitter
    )
    stage = forms.ChoiceField(
        choices=Deal.STAGE_CHOICES, 
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Deal
        fields = [
                    'deal_name', 'first_name', 'last_name', 'primary_email', 'country', 'assigned_to', 'currency', 'start_date_time', 'end_date_time', 'extended_end_date_time',
                     'company_name', 'industry', 'phone', 'mobile_phone', 'title', 'website', 'lead_source', 'description', 'stage'
                ]
        

class DealProductForm(forms.ModelForm):
    # Este campo es para seleccionar un producto existente en la organizacion
    product = forms.ModelChoiceField(queryset=Product.objects.all(
    ), widget=forms.Select(attrs={'class': 'form-select'}), label="Product")
    # Campo para la URL de cotización específica del DealProduct
    cotizacion_url = forms.URLField(required=False, widget=forms.URLInput(
        attrs={'class': 'form-control', 'placeholder': 'Cotización URL'}), label="Cotización URL")
    
    def __init__(self, *args, **kwargs):
        organization = kwargs.pop('organization', None)  # Extraer la organización del arumento
        super(DealProductForm, self).__init__(*args, **kwargs)
        if organization:
            # Filtrar el queryset del campo 'product' por la organización
            self.fields['product'].queryset = Product.objects.filter(organization=organization)

    class Meta:
        model = DealProduct
        fields = ['product', 'cotizacion_url']


class DealTaskCreateForm(forms.ModelForm):
    name = forms.CharField(label="", max_length=200, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Task Name'}))
    description = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': 'Task Description'}))
    deal = forms.ModelChoiceField(queryset=Deal.objects.all(), required=False, widget=forms.Select(
        attrs={'class': 'form-select'}), label="Deal")
    deal_product = forms.ModelChoiceField(queryset=DealProduct.objects.all(), required=False, widget=forms.Select(
        attrs={'class': 'form-select'}), label="Deal Product")
    parent_task = forms.ModelChoiceField(queryset=DealTask.objects.all(), required=False, widget=forms.Select(
        attrs={'class': 'form-select'}), label="Parent Task")
    parent_task_id = forms.IntegerField(widget=forms.HiddenInput(), required=False) # Captura el id del parent_task que se envia por la url desde DealTaskUpdateView
    assigned_to = forms.ModelChoiceField(queryset=User.objects.all(), empty_label=None, widget=forms.Select(
        attrs={'class': 'form-select'}), label="Assigned To")
        
    
    # def __init__(self, *args, **kwargs):
        # super(DealTaskCreateForm, self).__init__(*args, **kwargs)
        # Añadir un placeholder al principio de las opciones existentes
        # if 'parent_task' in self.fields:
            # existing_choices = list(self.fields['parent_task'].choices)
            # print('holllllllllllll')
            # print(existing_choices[0])
            # if existing_choices and existing_choices[0][0] != '':
            # self.fields['parent_task'].choices = [('', 'Parent Task')] + existing_choices
            # self.fields['parent_task'].choices = [('', 'Seleccione una opción')] + list(self.fields['parent_task'].choices)[1:]
            # self.fields['parent_task'].empty_label = None
        # if 'parent_task' in self.fields:
        #     existing_choices = list(self.fields['parent_task'].choices)
        #     if existing_choices and existing_choices[0][0] != '':
    class Meta:
        model = DealTask
        fields = ['name', 'description', 'deal', 'deal_product', 'parent_task', 'assigned_to']
        

class DealTaskUpdateForm(forms.ModelForm):
    name = forms.CharField(label="", max_length=200, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Task Name'}))
    description = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': 'Task Description'}))
    deal = forms.ModelChoiceField(queryset=Deal.objects.all(), required=False, widget=forms.Select(
        attrs={'class': 'form-select'}), label="Deal")
    deal_product = forms.ModelChoiceField(queryset=DealProduct.objects.all(), required=False, widget=forms.Select(
        attrs={'class': 'form-select'}), label="Deal Product")
    parent_task = forms.ModelChoiceField(queryset=DealTask.objects.all(), required=False, widget=forms.Select(
        attrs={'class': 'form-select'}), label="Parent Task")
    assigned_to = forms.ModelChoiceField(queryset=User.objects.all(), empty_label=None, widget=forms.Select(
        attrs={'class': 'form-select'}), label="Assigned To")
    stage = forms.ChoiceField(choices=DealTask.STAGE_CHOICES, widget=forms.Select(
        attrs={'class': 'form-select'}))  


    class Meta:
        model = DealTask
        fields = ['name', 'description', 'deal', 'deal_product', 'parent_task', 'assigned_to', 'stage']

