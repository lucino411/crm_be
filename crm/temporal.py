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