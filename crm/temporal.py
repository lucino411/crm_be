class LeadUpdateView(UpdateView, AgentRequiredMixin, AgentContextMixin):
    model = Lead
    template_name = 'operation/lead/lead_update.html'
    form_class = LeadForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        agent = self.request.user.agent

        if agent:
            form.fields['country'].queryset = Country.objects.filter(
                Q(organization=agent.organization) & Q(is_selected=True)
            )
            form.fields['assigned_to'].queryset = User.objects.filter(
                agent__organization=agent.organization)

            # Lógica para ocultar/mostrar extended_end_date_time
            if form.instance.end_date_time and form.instance.end_date_time > timezone.now():
                form.fields['extended_end_date_time'].widget = forms.DateTimeInput(
                    attrs={'class': 'form-control', 'type': 'datetime-local'})
            else:
                form.fields['extended_end_date_time'].widget = forms.HiddenInput()

             # Deshabilitar end_date_time si la fecha actual es mayor
            if form.instance.end_date_time and timezone.now() > form.instance.end_date_time:
                form.fields['end_date_time'].disabled = True

        return form

    def form_valid(self, form):
        agent = self.request.user.agent
        form.instance.organization = agent.organization
        form.instance.last_modified_by = agent.user
        self.object = form.save(commit=False)
        formset = LeadProductFormset(
            self.request.POST, self.request.FILES, instance=self.object)

        if formset.is_valid():
            self.object.save()
            formset.save()
        else:
            return self.render_to_response(self.get_context_data(form=form))

        messages.success(self.request, "Lead was updated")
        url = reverse('lead:detail', kwargs={
                      'organization_name': agent.organization, 'pk': self.object.pk})
        return redirect(url)

    def form_invalid(self, form):
        print(form.errors)
        messages.error(
            self.request, "Invalid form data. Please check the entries and try again.")
        return render(self.request, self.template_name, {'form': form})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Update Lead'
        context['organization_name'] = self.get_organization()

        if self.request.POST:
            context['formset'] = LeadProductFormset(
                self.request.POST, instance=self.object)
        else:
            context['formset'] = LeadProductFormset(instance=self.object)

        return context
