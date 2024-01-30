from django.urls import path
from .views import CompanyListView, CompanyHomeView, CompanyDetailView

app_name = 'company'

urlpatterns = [
    path('list/', CompanyHomeView.as_view(), name='company-list'),
    path('companies_json/', CompanyListView.as_view(), name='company-json'),
    path('<int:pk>/', CompanyDetailView.as_view(), name='company-detail'),
]