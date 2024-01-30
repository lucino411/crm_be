from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Currency
from .forms import CurrencyForm
from administration.userprofile.views import OrganizerRequiredMixin, OrganizerContextMixin


class CurrencyListView(OrganizerRequiredMixin, OrganizerContextMixin, ListView):
    model = Currency
    template_name = 'configuration/currency/currency_list.html'
    context_object_name = 'currencies'

    def get_queryset(self):
        return Currency.objects.filter(organization=self.get_organization())

class CurrencyDetailView(OrganizerRequiredMixin, OrganizerContextMixin, DetailView):
    model = Currency
    template_name = 'configuration/currency/currency_detail.html'
    context_object_name = 'currency'

class CurrencyCreateView(OrganizerRequiredMixin, OrganizerContextMixin, CreateView):
    model = Currency
    template_name = 'configuration/currency/currency_create.html'
    form_class = CurrencyForm

    def form_valid(self, form):
        form.instance.organization = self.get_organization()
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Currency Created.")
        return reverse_lazy('currency:list', kwargs={'organization_slug': self.get_organization().slug})
    







class CurrencyUpdateView(OrganizerRequiredMixin, OrganizerContextMixin, UpdateView):
    model = Currency
    template_name = 'configuration/currency/currency_update.html'
    form_class = CurrencyForm

    def get_success_url(self):
        pk = self.object.pk
        messages.success(self.request, "Currency Updated.")
        return reverse_lazy('currency:detail', kwargs={'organization_slug': self.get_organization().slug, 'pk': pk})

class CurrencyDeleteView(OrganizerRequiredMixin, OrganizerContextMixin, DeleteView):
    model = Currency
    template_name = 'configuration/currency/currency_delete.html'

    def get_success_url(self):
        messages.success(self.request, "Currency Deleted.")
        return reverse_lazy('currency:list', kwargs={'organization_slug': self.get_organization().slug})