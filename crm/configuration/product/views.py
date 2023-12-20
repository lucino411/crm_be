from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
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
    success_url = reverse_lazy('product-list')


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
    form_class = ProductForm
    template_name = 'configuration/product/product_update.html'
    success_url = reverse_lazy('product-list')


class ProductDeleteView(OrganizerRequiredMixin, OrganizerContextMixin, DeleteView):
    model = Product
    context_object_name = 'product'
    template_name = 'configuration/product/product_delete.html'
    success_url = reverse_lazy('product-list')


class ProductCategoryListView(OrganizerRequiredMixin, OrganizerContextMixin, ListView):
    model = ProductCategory
    context_object_name = 'productCategories'
    template_name = 'configuration/product_category/category_list.html'


class ProductCategoryCreateView(OrganizerRequiredMixin, OrganizerContextMixin, CreateView):
    model = ProductCategory
    form_class = ProductCategoryForm
    template_name = 'configuration/product_category/category_create.html'
    success_url = reverse_lazy('product-category-list')


class ProductCategoryDetailView(OrganizerRequiredMixin, OrganizerContextMixin, DetailView):
    model = ProductCategory
    template_name = 'configuration/product_category/category_detail.html'
    context_object_name = 'productCategory'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Detail Lead'
        context['organization_name'] = self.get_organization()
        return context


class ProductCategoryUpdateView(OrganizerRequiredMixin, OrganizerContextMixin, UpdateView):
    model = ProductCategory
    form_class = ProductCategoryForm
    template_name = 'configuration/product_category/category_update.html'
    success_url = reverse_lazy('product-category-list')


class ProductCategoryDeleteView(OrganizerRequiredMixin, OrganizerContextMixin, DeleteView):
    model = ProductCategory
    context_object_name = 'productCategory'
    template_name = 'configuration/product_category/category_delete.html'
    success_url = reverse_lazy('product-category-list')
