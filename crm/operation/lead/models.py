# from django.db import models
# from administration.organization.models import Organization

# def get_sentinel_user():
#     user, created = CustomUser.objects.get_or_create(username="deleted")
#     if created:
#         # Si se crea un nuevo usuario, establece los otros campos según sea necesario
#         user.set_unusable_password()
#         user.save()
#     return user

# class Lead(models.Model):
#     primary_email = models.EmailField(
#         unique=True, blank=False, help_text="Please use the following format: <em>YYYY-MM-DD</em>.")
#     lead_status = models.CharField(
#         max_length=100, choices=LEAD_STATUS_CHOICES, default='NEW')
#     assigned_to = models.ForeignKey(
#         settings.AUTH_USER_MODEL, related_name='assigned_leads', on_delete=models.SET(get_sentinel_user))
#     created_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL, related_name='created_leads', on_delete=models.SET(get_sentinel_user))
#     created_time = models.DateTimeField(auto_now_add=True)
#     modified_time = models.DateTimeField(auto_now=True)
#     last_modified_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL, related_name='last_modified_leads', on_delete=models.SET(get_sentinel_user))
#     organization = models.ForeignKey(
#         Organization, related_name='leads', on_delete=models.SET_NULL, null=True, blank=True)
#     is_closed = models.BooleanField(default=False)