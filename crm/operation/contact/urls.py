from django.urls import path
from .views import HomeContactView, ContactListView, ContactDetailView


app_name = 'contact'

urlpatterns = [
    path('list/', HomeContactView.as_view(), name='contact-list'),
    path('contacts_json/', ContactListView.as_view(), name='contact-json'),
    path('<int:pk>/', ContactDetailView.as_view(), name='contact-detail'),
]
