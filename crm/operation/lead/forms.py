from django.utils import timezone
from pydantic import ValidationError
from .models import Task, User
from django import forms
from django.contrib.auth.models import User
from .models import Lead, LeadProduct, Task
from configuration.country.models import Country
from configuration.currency.models import Currency
from configuration.product.models import Product

class LeadForm(forms.ModelForm):
    lead_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Lead Name'}))
    first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    primary_email = forms.EmailField(label="", widget=forms.EmailInput(
        attrs={'id': "addLeadUnregisterEmail", 'class': 'form-control', 'placeholder': 'Email'}),
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
        model = Lead
        fields = ['lead_name', 'first_name', 'last_name', 'primary_email', 'country',
                  'assigned_to', 'currency', 'start_date_time', 'end_date_time',
                  'extended_end_date_time']
        

class LeadUpdateForm(forms.ModelForm):
    lead_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Lead Name'}))
    first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    primary_email = forms.EmailField(label="", widget=forms.EmailInput(
        attrs={'id': "addLeadUnregisterEmail", 'class': 'form-control', 'placeholder': 'Email'}),
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
    stage = forms.ChoiceField(choices=Lead.STAGE_CHOICES, widget=forms.Select(
        attrs={'class': 'form-select'}))

    class Meta:
        model = Lead
        fields = ['lead_name', 'first_name', 'last_name', 'primary_email', 'country',
                  'assigned_to', 'currency', 'start_date_time', 'end_date_time',
                  'extended_end_date_time', 'stage']
        

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


class TaskCreateForm(forms.ModelForm):
    name = forms.CharField(label="", max_length=200, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Task Name'}))
    description = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': 'Task Description'}))
    lead = forms.ModelChoiceField(queryset=Lead.objects.all(), required=False, widget=forms.Select(
        attrs={'class': 'form-select'}), label="Lead")
    lead_product = forms.ModelChoiceField(queryset=LeadProduct.objects.all(), required=False, widget=forms.Select(
        attrs={'class': 'form-select'}), label="Lead Product")
    parent_task = forms.ModelChoiceField(queryset=Task.objects.all(), required=False, widget=forms.Select(
        attrs={'class': 'form-select'}), label="Parent Task")
    related_task = forms.ModelChoiceField(queryset=Task.objects.all(), required=False, widget=forms.Select(
        attrs={'class': 'form-select'}), label="Related Task")
    assigned_to = forms.ModelChoiceField(queryset=User.objects.all(), empty_label=None, widget=forms.Select(
        attrs={'class': 'form-select'}), label="Assigned To")

    class Meta:
        model = Task
        fields = ['name', 'description', 'lead', 'lead_product', 'parent_task', 'related_task', 'assigned_to']
        

class TaskUpdateForm(forms.ModelForm):
    name = forms.CharField(label="", max_length=200, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Task Name'}))
    description = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': 'Task Description'}))
    lead = forms.ModelChoiceField(queryset=Lead.objects.all(), required=False, widget=forms.Select(
        attrs={'class': 'form-select'}), label="Lead")
    lead_product = forms.ModelChoiceField(queryset=LeadProduct.objects.all(), required=False, widget=forms.Select(
        attrs={'class': 'form-select'}), label="Lead Product")
    parent_task = forms.ModelChoiceField(queryset=Task.objects.all(), required=False, widget=forms.Select(
        attrs={'class': 'form-select'}), label="Parent Task")
    related_task = forms.ModelChoiceField(queryset=Task.objects.all(), required=False, widget=forms.Select(
        attrs={'class': 'form-select'}), label="Related Task")
    assigned_to = forms.ModelChoiceField(queryset=User.objects.all(), empty_label=None, widget=forms.Select(
        attrs={'class': 'form-select'}), label="Assigned To")
    stage = forms.ChoiceField(choices=Task.STAGE_CHOICES, widget=forms.Select(
        attrs={'class': 'form-select'}))

    class Meta:
        model = Task
        fields = ['name', 'description', 'lead', 'lead_product', 'parent_task', 'related_task', 'assigned_to', 'stage']

