        # for lead_task in lead.lead_leadtask.all():
        #     # Obtener el DealProduct mapeado correspondiente al LeadProduct de la tarea
        #     deal_product = deal_product_mapping.get(lead_task.lead_product)
        #     DealTask.objects.create(
        #         deal = deal,
        #         name = lead_task.name,
        #         deal_product = deal_product,
        #         # parent_task = lead_task.parent_task,
        #         description = lead_task.description,
        #         created_by = lead_task.created_by,
        #         created_time = lead_task.created_time,
        #         modified_time = lead_task.modified_time,
        #         assigned_to = lead_task.assigned_to,
        #         last_modified_by = lead_task.last_modified_by,
        #         organization = lead_task.organization,
        #         stage = lead_task.stage,
        #         is_closed = lead_task.is_closed,
        #     )





    # Se verifica que el el email no este repetido, se va a usar en Company y Contact . No se usa en Leads ni Deals
        # agent = self.request.user.agent
        # email = form.cleaned_data['primary_email']
        # Verificar si existe un lead con el mismo email en la misma organización
        # if Lead.objects.filter(
        #     primary_email=email,
        #     organization=agent.organization
        # ).exists():
        #     messages.error(
        #         self.request, "A lead with this email already exists in your organization.")
        #     return render(self.request, self.template_name, {'form': form, 'organization_name': agent.organization})
        # else:
        #     # Obtener la organización del agente que está creando el lead
        #     agent = self.request.user.agent
        #     # Asignar la organización al lead
        #     form.instance.organization = agent.organization
        #     form.instance.created_by = agent.user
        #     form.instance.last_modified_by = agent.user
            # form.instance.assigned_to = agent.user
        #     form.save()

        #     messages.success(self.request, "Lead was created")
        #     return redirect('operation:lead-list', organization_name=agent.organization)
