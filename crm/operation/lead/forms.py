from django import forms
from django.contrib.auth.models import User
from .models import Lead, LeadProduct
from administration.userprofile.models import Agent
from configuration.country.models import Country
from configuration.currency.models import Currency
from configuration.product.models import Product, ProductCategory


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
    stage = forms.ChoiceField(choices=Lead.STAGE_CHOICES, widget=forms.Select(
        attrs={'class': 'form-select'}))

    class Meta:
        model = Lead
        fields = ['lead_name', 'first_name', 'last_name', 'primary_email', 'country',
                  'assigned_to', 'currency', 'start_date_time', 'end_date_time',
                  'extended_end_date_time', 'stage']




class LeadProductForm(forms.ModelForm):
    # Este campo es para seleccionar un producto existente
    product = forms.ModelChoiceField(queryset=Product.objects.all(
    ), widget=forms.Select(attrs={'class': 'form-select'}), label="Product")

    # Campo para la URL de cotización específica del LeadProduct
    cotizacion_url = forms.URLField(required=False, widget=forms.URLInput(
        attrs={'class': 'form-control', 'placeholder': 'Cotización URL'}), label="Cotización URL")

    class Meta:
        model = LeadProduct
        fields = ['product', 'cotizacion_url']
