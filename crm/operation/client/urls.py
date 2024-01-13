from django.urls import path
from .views import HomeClientView, ClientListView, ClientDetailView


app_name = 'client'

urlpatterns = [
    path('list/', HomeClientView.as_view(), name='client-list'),
    path('clients_json/', ClientListView.as_view(), name='client-json'),
    path('<int:pk>/', ClientDetailView.as_view(), name='client-detail'),
    # path('<int:pk>/update/', LeadUpdateView.as_view(), name='update'),   

]
