from django.utils import timezone
from pydantic import ValidationError
# from .models import Task, User
from .models import User
from django import forms
from django.contrib.auth.models import User
# from .models import Deal, DealProduct, Task
from .models import Deal, DealProduct, DealTask
from configuration.country.models import Country
from configuration.currency.models import Currency
from configuration.product.models import Product

class DealForm(forms.ModelForm):
    deal_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Deal Name'}))
    first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    primary_email = forms.EmailField(label="", widget=forms.EmailInput(
        attrs={'id': "addDealUnregisterEmail", 'class': 'form-control', 'placeholder': 'Email'}),
        error_messages={
            'unique': 'Este email ya está en uso. Por favor, proporciona un email diferente.',
            'invalid': 'Por favor, introduce un email válido.'
    })
    country = forms.ModelChoiceField(queryset=Country.objects.all(), widget=forms.Select(
        attrs={'class': 'form-select'}))
    assigned_to = forms.ModelChoiceField(queryset=User.objects.all(), empty_label=None, widget=forms.Select(
        attrs={'class': 'form-select'}))
    currency = forms.ModelChoiceField(queryset=Currency.objects.all(), empty_label=None, widget=forms.Select(
        attrs={'class': 'form-select'}))

    start_date_time = forms.DateTimeField(widget=forms.DateTimeInput(
        attrs={'class': 'form-control', 'type': 'datetime-local'}))
    end_date_time = forms.DateTimeField(required=False, widget=forms.DateTimeInput(
        attrs={'class': 'form-control', 'type': 'datetime-local'}))
    extended_end_date_time = forms.DateTimeField(required=False, widget=forms.DateTimeInput(
        attrs={'class': 'form-control', 'type': 'datetime-local'}))

    class Meta:
        model = Deal
        fields = ['deal_name', 'first_name', 'last_name', 'primary_email', 'country',
                  'assigned_to', 'currency', 'start_date_time', 'end_date_time',
                  'extended_end_date_time']
        

class DealUpdateForm(forms.ModelForm):
    deal_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Deal Name'}))
    first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    primary_email = forms.EmailField(label="", widget=forms.EmailInput(
        attrs={'id': "addDealUnregisterEmail", 'class': 'form-control', 'placeholder': 'Email'}),
        error_messages={
            'unique': 'Este email ya está en uso. Por favor, proporciona un email diferente.',
            'invalid': 'Por favor, introduce un email válido.'
    })
    country = forms.ModelChoiceField(queryset=Country.objects.all(), widget=forms.Select(
        attrs={'class': 'form-select'}))
    assigned_to = forms.ModelChoiceField(queryset=User.objects.all(), empty_label=None, widget=forms.Select(
        attrs={'class': 'form-select'}))
    currency = forms.ModelChoiceField(queryset=Currency.objects.all(), empty_label=None, widget=forms.Select(
        attrs={'class': 'form-select'}))

    start_date_time = forms.DateTimeField(widget=forms.DateTimeInput(
        attrs={'class': 'form-control', 'type': 'datetime-local'}))
    end_date_time = forms.DateTimeField(required=False, widget=forms.DateTimeInput(
        attrs={'class': 'form-control', 'type': 'datetime-local'}))
    extended_end_date_time = forms.DateTimeField(required=False, widget=forms.DateTimeInput(
        attrs={'class': 'form-control', 'type': 'datetime-local'}))
    stage = forms.ChoiceField(choices=Deal.STAGE_CHOICES, widget=forms.Select(
        attrs={'class': 'form-select'}))

    class Meta:
        model = Deal
        fields = ['deal_name', 'first_name', 'last_name', 'primary_email', 'country',
                  'assigned_to', 'currency', 'start_date_time', 'end_date_time',
                  'extended_end_date_time', 'stage']
        

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

