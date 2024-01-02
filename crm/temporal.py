from django.utils import timezone
from django.shortcuts import get_object_or_404

# ... otros imports ...

def get_form(self, form_class=None):
    form = super().get_form(form_class)
    agent = self.request.user.agent
    lead_id = self.kwargs.get('pk')
    lead = get_object_or_404(Lead, pk=lead_id)
    task = self.get_object()
    current_time = timezone.now()

    # Validaciones basadas en el estado del Lead
    if lead.is_closed:
        # Deshabilitar todos los campos si el lead está cerrado
        for field in form.fields:
            form.fields[field].disabled = True
    else:
        # Validaciones basadas en las fechas de la tarea
        task_disabled = False
        if lead.end_date_time and lead.end_date_time < current_time:
            task_disabled = True

        if lead.extended_end_date_time and lead.extended_end_date_time < current_time:
            task_disabled = True

        # Si la tarea está deshabilitada por alguna de las condiciones de fecha
        if task_disabled:
            for field in form.fields:
                form.fields[field].disabled = True
        else:
            # Estado predeterminado: habilitar todos los campos
            for field in form.fields:
                form.fields[field].disabled = False

    # ... Resto de lógica existente ...
    
    return form
