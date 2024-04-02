from django import forms
from .models import Currency

class CurrencyForm(forms.ModelForm):
    code = forms.CharField(
        label="Currency Code", 
        max_length=3, 
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Currency Code'}
        ),
        error_messages={
            # 'unique': 'Este código ya está en uso. Por favor, proporciona un código diferente.',
            'invalid': 'Por favor, introduce un código válido.'
        }
    )
    class Meta:
        model = Currency
        fields = ['code']
