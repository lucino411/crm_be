from django.urls import path
from .views import CountryListView, CountryDetailView, CountryCreateView, CountryUpdateView, CountryDeleteView

app_name = 'configuration'

urlpatterns = [
    path('configuration/country/',
         CountryListView.as_view(), name='country-list'),
    path('configuration/option/country/<int:pk>/',
         CountryDetailView.as_view(), name='country-detail'),
    path('configuration/option/country/create/',
         CountryCreateView.as_view(), name='country-create'),
    path('configuration/option/country/<int:pk>/update/',
         CountryUpdateView.as_view(), name='country-update'),    
     path('configuration/option/country/<int:pk>/delete/',
         CountryDeleteView.as_view(), name='country-delete'),
]


