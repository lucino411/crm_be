from django.urls import path
from .views import dashboard

urlpatterns = [
    path('', dashboard, name='dashboard-home'),
]

# handler404 = 'dashboard.views.page_not_found404'