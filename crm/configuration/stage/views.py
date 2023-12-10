from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Stage
from .forms import StageForm
from administration.userprofile.views import OrganizerRequiredMixin, OrganizerContextMixin


class StageListView(OrganizerRequiredMixin, OrganizerContextMixin, ListView):
    model = Stage
    template_name = 'configuration/stage/stage_list.html'
    context_object_name = 'stages'

class StageDetailView(OrganizerRequiredMixin, OrganizerContextMixin, DetailView):
    model = Stage
    template_name = 'configuration/stage/stage_detail.html'
    context_object_name = 'stage'

class StageCreateView(OrganizerRequiredMixin, OrganizerContextMixin, CreateView):
    model = Stage
    template_name = 'configuration/stage/stage_create.html'
    form_class = StageForm

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Stage Created.")
        return reverse_lazy('stage:list', kwargs={'organization_name': self.get_organization()})

class StageUpdateView(OrganizerRequiredMixin, OrganizerContextMixin, UpdateView):
    model = Stage
    template_name = 'configuration/stage/stage_update.html'
    form_class = StageForm

    def get_success_url(self):
        pk = self.object.pk
        messages.success(self.request, "Stage Updated.")
        return reverse_lazy('stage:detail', kwargs={'organization_name': self.get_organization(), 'pk': pk})

class StageDeleteView(OrganizerRequiredMixin, OrganizerContextMixin, DeleteView):
    model = Stage
    template_name = 'configuration/stage/stage_delete.html'

    def get_success_url(self):
        messages.success(self.request, "Stage Deleted.")
        return reverse_lazy('stage:list', kwargs={'organization_name': self.get_organization()})