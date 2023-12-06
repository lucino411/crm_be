from typing import Any
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.http import HttpResponse


from administration.userprofile.models import Organizer
from .models import Country
from .forms import CountryForm


class OrganizerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user_is_organizer = Organizer.objects.filter(
            user=self.request.user).exists()
        return user_is_organizer


# class CountryListView(OrganizerRequiredMixin, ListView):
#     model = Country
#     template_name = 'configuration/option/country_list.html'
#     context_object_name = 'countries'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         organizer = Organizer.objects.get(user=self.request.user)
#         context['organization_name'] = organizer.organization
#         return context
    


class CountryListView(OrganizerRequiredMixin, ListView):
    model = Country
    template_name = 'configuration/option/country_list.html'
    context_object_name = 'countries'

    def get_queryset(self):
        # Asegurarse de que el usuario actual es un organizador
        if self.request.user.is_authenticated:
            organizer = Organizer.objects.get(user=self.request.user)
            # Filtrar los países por la organización del organizador actual
            return Country.objects.filter(organization=organizer.organization)
        else:
            # Usuario no autenticado, retornar queryset vacío o manejar según tu lógica
            return Country.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener la organización asociada al organizador actual
        organizer = Organizer.objects.get(user=self.request.user)
        context['organization_name'] = organizer.organization
        return context

class CountryDetailView(OrganizerRequiredMixin, DetailView):
    model = Country
    template_name = 'configuration/option/country_detail.html'
    context_object_name = 'country'

class CountryCreateView(OrganizerRequiredMixin, CreateView):
    model = Country
    template_name = 'configuration/option/country_create.html'
    form_class = CountryForm
    success_url = reverse_lazy('configuration:country-list')

    def form_valid(self, form):
        # Obtén la organización asociada al organizador
        organization = self.request.user.organizer.organization
        # Establece la organización en el objeto Country antes de guardarlo
        form.instance.organization = organization
        return super().form_valid(form)


class CountryUpdateView(OrganizerRequiredMixin, UpdateView):
    model = Country
    template_name = 'configuration/option/country_update.html'
    fields = ['name', 'code', 'is_selected']

    def get_success_url(self):
        return reverse_lazy('configuration:country-detail', kwargs={'pk': self.object.pk})


# class CountryDeleteView(OrganizerRequiredMixin, DeleteView):
#     model = Country
#     template_name = 'country_confirm_delete.html'
#     success_url = reverse_lazy('country_list')
