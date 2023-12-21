# class LeadUpdateView(UpdateView, AgentRequiredMixin, AgentContextMixin):
#     # ... otros métodos ...

#     def form_valid(self, form):
#         agent = self.request.user.agent
#         form.instance.organization = agent.organization
#         form.instance.last_modified_by = agent.user

#         lead = form.save(commit=False)

#         # Actualizar is_closed basado en end_date_time y extended_end_date_time
#         current_time = timezone.now()
#         if lead.end_date_time and lead.end_date_time > current_time:
#             lead.is_closed = True
#         elif lead.extended_end_date_time and lead.extended_end_date_time > current_time:
#             lead.is_closed = True
#         else:
#             lead.is_closed = False

#         # Establecer is_closed en True si el stage es "Close Win" o "Close Lost"
#         if lead.stage in ['close_win', 'close_lost']:
#             lead.is_closed = True

#         lead.save()

#         # Guardar los formularios de LeadProduct
#         formset = LeadProductFormset(
#             self.request.POST, self.request.FILES, instance=lead)
#         if formset.is_valid():
#             formset.save()
#         else:
#             return self.render_to_response(self.get_context_data(form=form))

#         messages.success(self.request, "Lead actualizado")
#         url = reverse('lead:detail', kwargs={
#                       'organization_name': agent.organization, 'pk': lead.pk})
#         return redirect(url)

#     # ... resto de la clase ...
