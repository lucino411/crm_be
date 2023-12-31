from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('administration.core.urls')),
    path('', include('operation.dashboard.urls')),
    path('<str:organization_name>/dashboard/', include('operation.dashboard.urls')),
    path('<str:organization_name>/configuration/country/', include('configuration.country.urls')),
    path('<str:organization_name>/configuration/currency/', include('configuration.currency.urls')),
    path('<str:organization_name>/lead/', include('operation.lead.urls')),
    path('<str:organization_name>/deal/', include('operation.deal.urls')),
    path('<str:organization_name>/product/', include('configuration.product.urls')),
]
