from django.db.models import Count, Q

from .models import Lead, LeadProduct
from .models import LeadTask

def get_lead_products_statistics():
    total_products = LeadProduct.objects.count()    
    # Si deseas más estadísticas, como el número de productos por lead, puedes hacerlo aquí.
    return {
        'total_products': total_products,
    }


def get_leads_statistics():
    total_leads = Lead.objects.count()
    closed_leads = Lead.objects.filter(stage='close_lost').count()
    non_close_lost_leads = Lead.objects.exclude(stage='close_lost').count()
    if total_leads > 0:  # Asegurarse de no dividir por cero
        non_close_lost_percentage = (non_close_lost_leads / total_leads) * 100
    else:
        non_close_lost_percentage = 0  # Si no hay leads, el porcentaje es 0
    products_stats = get_lead_products_statistics()  # Obtener estadísticas de productos para Leads
    return {
        'total_leads': total_leads,
        'closed_leads': closed_leads,
        'non_close_lost_percentage': non_close_lost_percentage,  # Agregar esta línea
        **products_stats,  # Incorporar estadísticas de productos    
    }



# LEAD TASKS STATISTICS

def get_total_tasks():
    return LeadTask.objects.count()

def get_total_tasks_completed():
    return LeadTask.objects.filter(stage='completed').count()

def get_total_tasks_canceled():
    return LeadTask.objects.filter(stage='canceled').count()

def get_lead_with_most_tasks():
    lead_with_most_tasks = LeadTask.objects.values('lead__id', 'lead__lead_name')\
        .annotate(task_count=Count('id'))\
        .order_by('-task_count')\
        .first()
    if lead_with_most_tasks:
        return {'lead_id': lead_with_most_tasks['lead__id'], 'lead_name': lead_with_most_tasks['lead__lead_name'], 'task_count': lead_with_most_tasks['task_count']}
    return None