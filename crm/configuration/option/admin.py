from django.contrib import admin
from .models import Country

@admin.register(Country)
class OrganizerAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_selected', 'organization_name')

    def organization_name(self, obj):
        return obj.organization.name

