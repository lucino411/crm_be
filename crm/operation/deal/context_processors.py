from .utils import (
    get_deals_statistics,
    get_total_tasks, get_total_tasks_completed, 
    get_total_tasks_canceled, get_deal_with_most_tasks
)


def deal_statistics(request):
    return {'deal_stats': get_deals_statistics()}


def deal_task_statistics(request):
    return {
        'total_tasks': get_total_tasks(),
        'total_tasks_completed': get_total_tasks_completed(),
        'total_tasks_canceled': get_total_tasks_canceled(),
        'deal_with_most_tasks': get_deal_with_most_tasks(),
    }