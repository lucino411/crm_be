from django import forms
from .models import Currency


class CurrencyForm(forms.ModelForm):
    class Meta:
        model = Currency
        fields = ['code']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
        }
