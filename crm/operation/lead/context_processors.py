from .utils import (
    get_leads_statistics,
    get_total_tasks, get_total_tasks_completed, 
    get_total_tasks_canceled, get_lead_with_most_tasks
)


def lead_statistics(request):
    return {'lead_stats': get_leads_statistics()}


def lead_task_statistics(request):
    return {
        'total_tasks': get_total_tasks(),
        'total_tasks_completed': get_total_tasks_completed(),
        'total_tasks_canceled': get_total_tasks_canceled(),
        'lead_with_most_tasks': get_lead_with_most_tasks(),
    }