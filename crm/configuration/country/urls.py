from django.urls import path
from .views import CountryListView, CountryDetailView, CountryCreateView, CountryUpdateView, CountryDeleteView

app_name = 'country'

urlpatterns = [
    path('configuration/country/',
         CountryListView.as_view(), name='list'),
    path('configuration/country/<int:pk>/',
         CountryDetailView.as_view(), name='detail'),
    path('configuration/country/create/',
         CountryCreateView.as_view(), name='create'),
    path('configuration/country/<int:pk>/update/',
         CountryUpdateView.as_view(), name='update'),    
     path('configuration/country/<int:pk>/delete/',
         CountryDeleteView.as_view(), name='delete'),
]


