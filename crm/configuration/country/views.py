from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from django.urls import reverse_lazy
from .models import Country
from .forms import CountryForm
from administration.userprofile.views import OrganizerRequiredMixin, OrganizerContextMixin


class CountryListView(OrganizerRequiredMixin, OrganizerContextMixin, ListView):
    model = Country
    template_name = 'configuration/country/country_list.html'
    context_object_name = 'countries'

    def get_queryset(self):
        return Country.objects.filter(organization=self.get_organization())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)              
        context['title'] = "Countries"
        context['crud'] = "Country Settings"
        return context


class CountryDetailView(OrganizerRequiredMixin, OrganizerContextMixin, DetailView):
    model = Country
    template_name = 'configuration/country/country_detail.html'
    context_object_name = 'country'


class CountryCreateView(OrganizerRequiredMixin, OrganizerContextMixin, SuccessMessageMixin, CreateView):
    model = Country
    template_name = 'configuration/country/country_create.html'
    form_class = CountryForm
    # success_message = "Country created successfully."

    def form_valid(self, form):
        form.instance.organization = self.get_organization()
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Currency Created.")
        return reverse_lazy('country:list', kwargs={'organization_slug': self.get_organization().slug})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)              
        context['title'] = "Countries"
        context['crud'] = "Country Create"
        return context


class CountryUpdateView(OrganizerRequiredMixin, OrganizerContextMixin, SuccessMessageMixin, UpdateView):
    model = Country
    template_name = 'configuration/country/country_update.html'
    fields = ['name', 'code', 'is_selected']
    success_message = 'Country updated successfully'

    def get_success_url(self):
        # messages.success(self.request, "Country updated.")
        return reverse_lazy('country:list', kwargs={'organization_slug': self.get_organization().slug})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)              
        context['title'] = "Countries"
        context['crud'] = "Country Update"
        return context



class CountryDeleteView(OrganizerRequiredMixin, OrganizerContextMixin, SuccessMessageMixin, DeleteView):
    model = Country
    template_name = 'configuration/country/country_delete.html'
    success_message = "Country deleted."

    def get_success_url(self):
        # messages.success(self.request, "Country deleted.")
        return reverse_lazy('country:list', kwargs={'organization_slug': self.get_organization().slug})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)              
        context['title'] = "Countries"
        context['crud'] = "Country Delete"
        return context
