from django import forms
from .models import Product, ProductCategory


class ProductForm(forms.ModelForm):
    name = forms.CharField(max_length=200, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Product Name'}))
    category = forms.ModelChoiceField(queryset=ProductCategory.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    product_url = forms.CharField(max_length=200, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Product URL'}))

    class Meta:
        model = Product
        fields = ('name', 'category', 'product_url')


class ProductCategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=200, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Product Name'}))
    url = forms.CharField(max_length=200, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Product URL'}))

    class Meta:
        model = ProductCategory
        fields = ('name', 'url')
