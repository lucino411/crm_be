from django.db.models import Count, Q

from .models import Deal, DealProduct
from .models import DealTask

def get_deal_products_statistics():
    total_products = DealProduct.objects.count()    
    # Si deseas más estadísticas, como el número de productos por deal, puedes hacerlo aquí.
    return {
        'total_products': total_products,
    }


def get_deals_statistics():
    total_deals = Deal.objects.count()
    closed_deals = Deal.objects.filter(stage='close_lost').count()
    non_close_lost_deals = Deal.objects.exclude(stage='close_lost').count()
    if total_deals > 0:  # Asegurarse de no dividir por cero
        non_close_lost_percentage = (non_close_lost_deals / total_deals) * 100
    else:
        non_close_lost_percentage = 0  # Si no hay deals, el porcentaje es 0
    products_stats = get_deal_products_statistics()  # Obtener estadísticas de productos para Deals
    return {
        'total_deals': total_deals,
        'closed_deals': closed_deals,
        'non_close_lost_percentage': non_close_lost_percentage,  # Agregar esta línea
        **products_stats,  # Incorporar estadísticas de productos    
    }



# DEAL TASKS STATISTICS

def get_total_tasks():
    return DealTask.objects.count()

def get_total_tasks_completed():
    return DealTask.objects.filter(stage='completed').count()

def get_total_tasks_canceled():
    return DealTask.objects.filter(stage='canceled').count()

def get_deal_with_most_tasks():
    deal_with_most_tasks = DealTask.objects.values('deal__id', 'deal__deal_name')\
        .annotate(task_count=Count('id'))\
        .order_by('-task_count')\
        .first()
    if deal_with_most_tasks:
        return {'deal_id': deal_with_most_tasks['deal__id'], 'deal_name': deal_with_most_tasks['deal__deal_name'], 'task_count': deal_with_most_tasks['task_count']}
    return None