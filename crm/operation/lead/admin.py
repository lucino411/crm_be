from django.contrib import admin
from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'organization_name', 'country_name')

    def organization_name(self, obj):
        return obj.organization.name
    
    def country_name(self, obj):
        return obj.country.name
