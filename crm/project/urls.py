from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('administration.core.urls')),
    path('<slug:organization_slug>/media/', include('administration.organization.urls')),
    path('', include('operation.dashboard.urls')),
    path('<slug:organization_slug>/dashboard/', include('operation.dashboard.urls')),

    path('<slug:organization_slug>/configuration/country/', include('configuration.country.urls')),
    path('<slug:organization_slug>/configuration/currency/', include('configuration.currency.urls')),

    path('<slug:organization_slug>/lead/', include('operation.lead.urls')),
    path('<slug:organization_slug>/deal/', include('operation.deal.urls')),
    path('<slug:organization_slug>/contact/', include('operation.contact.urls')),
    path('<slug:organization_slug>/company/', include('operation.company.urls')),
    path('<slug:organization_slug>/client/', include('operation.client.urls')),
    path('<slug:organization_slug>/product/', include('configuration.product.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)