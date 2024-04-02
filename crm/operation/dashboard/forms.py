from django import forms

from administration.organization.models import OrganizationMedia

class ImageSelectionForm(forms.Form):
    image = forms.ModelChoiceField(queryset=OrganizationMedia.objects.all(), empty_label=None)
