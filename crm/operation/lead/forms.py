from django import forms
from django.contrib.auth.models import User
from .models import Lead
from administration.userprofile.models import Agent
from configuration.country.models import Country

class LeadForm(forms.ModelForm):
    first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    primary_email = forms.EmailField(label="", widget=forms.EmailInput(attrs={'id': "addLeadUnregisterEmail", 'class': 'form-control', 'placeholder': 'Email'}), error_messages={
        'unique': 'Este email ya está en uso. Por favor, proporciona un email diferente.',
        'invalid': 'Por favor, introduce un email válido.',
    })
    country = forms.ModelChoiceField(queryset=Country.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    assigned_to = forms.ModelChoiceField(queryset=User.objects.all(), empty_label=None, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Lead
        fields = ('first_name', 'last_name', 'primary_email', 'country', 'assigned_to')
        widgets = {
        }
        

