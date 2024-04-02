from django import forms

from .models import Country

class CountryForm(forms.ModelForm):
    name = forms.CharField(
        label="Country Name", 
        max_length=200, 
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Country Name'}
        )
    )
    code = forms.CharField(
        label="Country Code", 
        max_length=6, 
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Country Code'}
        )
    )
    is_selected = forms.BooleanField(
        label="Selected", 
            widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}
        )
    )

    class Meta:
        model = Country
        fields = ['name', 'code', 'is_selected']