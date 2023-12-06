from django import forms
from .models import Country


class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ['name', 'code', 'is_selected']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'is_selected': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
