from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('administration.core.urls')),
    path('<str:organization_name>/media/', include('administration.organization.urls')),
    path('', include('operation.dashboard.urls')),
    path('<str:organization_name>/dashboard/', include('operation.dashboard.urls')),
    path('<str:organization_name>/configuration/country/', include('configuration.country.urls')),
    path('<str:organization_name>/configuration/currency/', include('configuration.currency.urls')),
    path('<str:organization_name>/lead/', include('operation.lead.urls')),
    path('<str:organization_name>/deal/', include('operation.deal.urls')),
    path('<str:organization_name>/contact/', include('operation.contact.urls')),
    # path('<str:organization_name>/company/', include('operation.company.urls')),
    path('<str:organization_name>/client/', include('operation.client.urls')),
    path('<str:organization_name>/product/', include('configuration.product.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)