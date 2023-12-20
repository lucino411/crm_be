from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from configuration.country.models import Country
from administration.organization.models import Organization
from configuration.currency.models import Currency
from configuration.product.models import Product

def get_sentinel_user():
    user, created = User.objects.get_or_create(username="deleted")
    if created:
        user.set_unusable_password()
        user.save()
    return user

def get_sentinel_product():
    return Product.objects.get_or_create(name="deleted")[0]


class Lead(models.Model):
    STAGE_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('dorman', 'Dorman'),
        ('close_win', 'Close Win'),
        ('close_lost', 'Close Lost'),
    ]

    lead_name = models.CharField(max_length=100, unique=True, blank=False, null=True)
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=False)
    primary_email = models.EmailField(
        blank=False, help_text="Please use the following format: <em>YYYY-MM-DD</em>.")
    country = models.ForeignKey(
        Country, on_delete=models.SET_NULL, blank=False, null=True, limit_choices_to={'is_selected': True})
    assigned_to = models.ForeignKey(User, related_name='assigned_lead', on_delete=models.SET(get_sentinel_user))
    created_by = models.ForeignKey(User, related_name='created_lead', on_delete=models.SET(get_sentinel_user))
    last_modified_by = models.ForeignKey(User, related_name='last_modified_lead', on_delete=models.SET(get_sentinel_user))
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    start_date_time = models.DateTimeField()
    end_date_time = models.DateTimeField(null=True, blank=True)
    extended_end_date_time = models.DateTimeField(null=True, blank=True)    
    actual_completion_date = models.DateTimeField(null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    organization = models.ForeignKey(
        Organization, related_name='lead', on_delete=models.CASCADE)    
    stage = models.CharField(
        max_length=20, choices=STAGE_CHOICES, default='new')
    is_closed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        current_time = timezone.now()

        # Si hay una fecha extendida y es futura, reabrir el lead
        if self.extended_end_date_time and self.extended_end_date_time > current_time:
            self.is_closed = False
        # Si no hay fecha extendida, pero la fecha de fin ha pasado, cerrar el lead
        elif not self.extended_end_date_time and self.end_date_time and self.end_date_time <= current_time:
            self.is_closed = True
        # Si hay fecha extendida y ha pasado, cerrar el lead
        elif self.extended_end_date_time and self.extended_end_date_time <= current_time:
            self.is_closed = True

        super().save(*args, **kwargs)


class LeadProduct(models.Model):
    lead = models.ForeignKey(
        Lead, related_name='lead_product', on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, on_delete=models.SET(get_sentinel_product))
    cotizacion_url = models.URLField(null=True, blank=True)


class Task(models.Model):
    STAGE_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
        ('skipped', 'Skipped'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)    
    start_date_time = models.DateTimeField()
    original_end_date_time = models.DateTimeField(null=True, blank=True)
    actual_completion_date = models.DateTimeField(null=True, blank=True)
    last_modified_time = models.DateTimeField(auto_now=True)
    lead = models.ForeignKey(
        'Lead', related_name='tasks', on_delete=models.CASCADE, null=True, blank=True)
    lead_product = models.ForeignKey('LeadProduct', related_name='tasks', on_delete=models.CASCADE, null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='created_tasks', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='assigned_tasks', on_delete=models.CASCADE)
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='modified_tasks', on_delete=models.CASCADE)
    parent_task = models.ForeignKey(
        'self', null=True, blank=True, related_name='subtasks', on_delete=models.CASCADE)
    related_task = models.ForeignKey(
        'self', null=True, blank=True, related_name='related_tasks', on_delete=models.SET_NULL)
    related_subtask = models.ForeignKey(
        'self', null=True, blank=True, related_name='related_subtasks', on_delete=models.SET_NULL)
    stage = models.CharField(
        max_length=20, choices=STAGE_CHOICES, default='pending')
    
    is_closed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.original_end_date_time:
            self.original_end_date_time = self.end_date_time

        if self.is_closed and not self.actual_completion_date:
            self.actual_completion_date = timezone.now()

    @property
    def delay(self):
        if self.original_end_date_time and self.actual_completion_date:
            return self.actual_completion_date - self.original_end_date_time
        return None

    def is_general_task(self):
        return self.lead is not None and self.lead_product is None

    def save(self, *args, **kwargs):
        self.is_closed = self.stage not in ['pending', 'in_progress']
        # Cerrar la tarea si la fecha de finalización ha pasado
        if self.end_date_time and timezone.now() > self.end_date_time:
            self.is_closed = True
        super(Task, self).save(*args, **kwargs)

        # Si la tarea se completa, salta o cancela, actualiza también todas sus subtareas
        if self.is_closed:
            self.close_subtasks(self.stage)

    def close_subtasks(self, new_stage):
        # Cierra todas las subtareas, estableciendo su stage al mismo que la tarea principal y marcándolas como cerradas si es necesario.
        for subtask in self.subtasks.all():
            subtask.stage = new_stage
            subtask.is_closed = True
            subtask.save()


# class SubTask(models.Model):
#     title = models.CharField(max_length=200)
#     description = models.TextField()
#     created_time = models.DateTimeField(auto_now_add=True)
#     start_date_time = models.DateTimeField()
#     end_date_time = models.DateTimeField()
#     last_modified_time = models.DateTimeField(auto_now=True)
#     parent_task = models.ForeignKey(
#         Task, related_name='subtasks', on_delete=models.CASCADE)
    
    
#     created_by = models.ForeignKey(User, related_name='created_subtasks', on_delete=models.CASCADE)
#     assigned_to = models.ForeignKey(User, related_name='assigned_subtasks', on_delete=models.CASCADE)
#     last_modified_by = models.ForeignKey(User, related_name='modified_subtasks', on_delete=models.CASCADE)

#     def save(self, *args, **kwargs):
#         # Ejemplo: Actualizar automáticamente el estado basado en las fechas
#         if self.end_date_time and timezone.now() > self.end_date_time:
#             # Aquí podrías tener lógica para cambiar el estado, si aplica
#             pass

#         super(SubTask, self).save(*args, **kwargs)

