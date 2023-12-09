from userprofile.models import CustomUser
from django.db.models.signals import pre_delete
from django.dispatch import receiver

@receiver(pre_delete, sender=CustomUser)
def user_delete(sender, instance, **kwargs):
    from lead.models import Lead

    leads = Lead.objects.filter(created_by=instance)
    for lead in leads:
        lead.created_by = CustomUser.objects.get(username='admin')  # Cambia 'admin' por el nombre de usuario deseado
        lead.save()

'''
El archivo signals.py se utiliza para definir señales en Django. Las señales son mecanismos que permiten ejecutar código en respuesta a ciertos eventos que ocurren en tu aplicación. En este caso particular, estás utilizando la señal pre_delete, que se dispara justo antes de que se elimine un objeto del modelo CustomUser.
En tu implementación específica, estás utilizando la señal pre_delete para el modelo CustomUser. Cuando un usuario es eliminado, tu señal se activa y ejecuta el código definido en la función user_delete. El propósito de este código es encontrar y actualizar todos los Lead objetos que están asociados con el usuario que se está eliminando. En este caso, estás cambiando el valor de created_by del Lead a un usuario específico, en este caso, el usuario con el nombre de usuario 'admin'.
Este tipo de señales pueden ser útiles para realizar acciones específicas en tu base de datos o en tu lógica de negocio en respuesta a eventos específicos, como la eliminación de un usuario en este caso.
'''
