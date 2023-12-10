from django import forms
from .models import Stage


class StageForm(forms.ModelForm):
    class Meta:
        model = Stage
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }
