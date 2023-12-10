from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('administration.core.urls')),
    path('', include('operation.dashboard.urls')),
    path('<str:organization_name>/', include('operation.dashboard.urls')),
    path('<str:organization_name>/', include('configuration.country.urls')),
    path('<str:organization_name>/', include('configuration.stage.urls')),
    path('<str:organization_name>/', include('operation.lead.urls')),
]
