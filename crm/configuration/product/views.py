from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages

from operation.lead.models import LeadProduct

from .models import Product, ProductCategory
from administration.userprofile.views import OrganizerRequiredMixin, OrganizerContextMixin
from .forms import ProductForm, ProductCategoryForm



class ProductListView(OrganizerRequiredMixin, OrganizerContextMixin, ListView):
    model = Product
    template_name = 'configuration/product/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(organization=self.get_organization())


class ProductCreateView(OrganizerRequiredMixin, OrganizerContextMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'configuration/product/product_create.html'    

    def form_valid(self, form):
        form.instance.organization = self.get_organization()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(ProductCreateView, self).get_form_kwargs()
        kwargs['organization'] = self.get_organization()
        return kwargs

    def get_success_url(self):
        organization_name = self.get_organization()
        messages.success(self.request, "Product created.")
        return reverse_lazy('product:list', kwargs={'organization_name': organization_name})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organization = self.get_organization()
        categories = ProductCategory.objects.filter(organization=organization)  # Usa filter en lugar de get
        context['categories'] = categories
        return context       
    

class ProductDetailView(OrganizerRequiredMixin, OrganizerContextMixin, DetailView):
    model = Product
    template_name = 'configuration/product/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Detail Product'
        context['organization_name'] = self.get_organization()
        return context


class ProductUpdateView(OrganizerRequiredMixin, OrganizerContextMixin, UpdateView):
    model = Product
    template_name = 'configuration/product/product_update.html'
    form_class = ProductForm

    def get_success_url(self):
        pk = self.object.pk
        messages.success(self.request, "Product updated.")
        return reverse_lazy('product:detail', kwargs={'organization_name': self.get_organization(), 'pk': pk})


class ProductDeleteView(OrganizerRequiredMixin, OrganizerContextMixin, DeleteView):
    model = Product
    context_object_name = 'product'
    template_name = 'configuration/product/product_delete.html'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if LeadProduct.objects.filter(product=self.object).exists():
            # Si el producto está en uso, muestra un mensaje de error y redirige
            messages.error(self.request, "Cannot delete product because it is in use.")
            return HttpResponseRedirect(self.get_success_url())
        else:
            # Si el producto no está en uso, procede con la eliminación
            response = super().delete(request, *args, **kwargs)
            messages.success(self.request, "Product deleted.")
            return response

    def get_success_url(self):
        organization_name = self.get_organization()
        return reverse_lazy('product:list', kwargs={'organization_name': organization_name})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Product Delete'
        context['organization_name'] = self.get_organization()
        return context
    

    









class ProductCategoryListView(OrganizerRequiredMixin, OrganizerContextMixin, ListView):
    model = ProductCategory
    context_object_name = 'categories'
    template_name = 'configuration/product_category/category_list.html'

    def get_queryset(self):
        return ProductCategory.objects.filter(organization=self.get_organization())


class ProductCategoryCreateView(OrganizerRequiredMixin, OrganizerContextMixin, CreateView):
    model = ProductCategory
    form_class = ProductCategoryForm
    template_name = 'configuration/product_category/category_create.html'

    def form_valid(self, form):
        form.instance.organization = self.get_organization()
        return super().form_valid(form)

    def get_success_url(self):
        organization_name = self.get_organization()
        messages.success(self.request, "Category created.")
        return reverse_lazy('product:category-list', kwargs={'organization_name': organization_name})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Product Category Create'
        context['organization_name'] = self.get_organization()
        return context
   

class ProductCategoryDetailView(OrganizerRequiredMixin, OrganizerContextMixin, DetailView):
    model = ProductCategory
    template_name = 'configuration/product_category/category_detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Detail Lead'
        context['organization_name'] = self.get_organization()
        return context


class ProductCategoryUpdateView(OrganizerRequiredMixin, OrganizerContextMixin, UpdateView):
    model = ProductCategory
    form_class = ProductCategoryForm
    template_name = 'configuration/product_category/category_update.html'

    def get_success_url(self):
        pk = self.object.pk
        messages.success(self.request, "Category updated.")
        return reverse_lazy('product:category-detail', kwargs={'organization_name': self.get_organization(), 'pk': pk})


class ProductCategoryDeleteView(OrganizerRequiredMixin, OrganizerContextMixin, DeleteView):
    model = ProductCategory
    context_object_name = 'category'
    template_name = 'configuration/product_category/category_delete.html'

    def post(self, request, *args, **kwargs):
        # Obtén la instancia de la categoría a eliminar
        self.object = self.get_object()

        # Verificar si hay productos de esta categoría en LeadProduct
        if Product.objects.filter(category=self.object, lead_product__isnull=False).exists():
            # Si encuentra productos asociados, mostrar mensaje de error y redirigir
            messages.error(request, "No se puede eliminar la categoría porque tiene productos asociados en LeadProduct.")
            return HttpResponseRedirect(self.get_success_url())
        
        # Si no hay productos asociados, permite la eliminación
        response = super().post(request, *args, **kwargs)
        messages.success(request, "Categoría eliminada con éxito.")
        return response

    def get_success_url(self):
        organization_name = self.get_organization()
        return reverse_lazy('product:category-list', kwargs={'organization_name': organization_name})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Category Delete'
        context['organization_name'] = self.get_organization()
        return context