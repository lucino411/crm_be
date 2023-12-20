from django.urls import path
from .views import CurrencyListView, CurrencyDetailView, CurrencyCreateView, CurrencyUpdateView, CurrencyDeleteView

app_name = 'currency'

urlpatterns = [
    path('list/', CurrencyListView.as_view(), name='list'),
    path('create/', CurrencyCreateView.as_view(), name='create'),
    path('<int:pk>/', CurrencyDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', CurrencyUpdateView.as_view(), name='update'),    
    path('<int:pk>/delete/', CurrencyDeleteView.as_view(), name='delete'),
]


