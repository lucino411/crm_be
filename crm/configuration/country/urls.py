from django.urls import path
from .views import CountryListView, CountryDetailView, CountryCreateView, CountryUpdateView, CountryDeleteView

app_name = 'country'

urlpatterns = [
    path('list/', CountryListView.as_view(), name='list'),
    path('create/', CountryCreateView.as_view(), name='create'),
    path('<int:pk>/', CountryDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', CountryUpdateView.as_view(), name='update'),    
    path('<int:pk>/delete/', CountryDeleteView.as_view(), name='delete'),
]


