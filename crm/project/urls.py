from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('administration.core.urls')),
    path('', include('operation.dashboard.urls')),
    path('<str:organization_name>/', include('operation.dashboard.urls')),
    path('<str:organization_name>/', include('configuration.option.urls')),
]
