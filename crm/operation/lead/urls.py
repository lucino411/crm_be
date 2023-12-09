from django.urls import path
from .views import HomeLeadView, LeadListView, LeadCreateView, LeadDetailView, LeadUpdateView, LeadDeleteView

app_name = 'operation'

urlpatterns = [
    # path('conf/', HomeConfLeadView.as_view(), name='leads_conf'),
    path('list/', HomeLeadView.as_view(), name='lead-list'),
    path('leads_json/', LeadListView.as_view(), name='lead-json'),
    path('create/', LeadCreateView.as_view(), name='lead-create'),
    # path('create_be/', LeadCreateAnonymousView.as_view(), name='lead_create_be'),
    path('<int:pk>/', LeadDetailView.as_view(), name='lead-detail'),
    path('<int:pk>/update/', LeadUpdateView.as_view(), name='lead-update'),
    path('<int:pk>/delete/', LeadDeleteView.as_view(), name='lead-delete'),
    # path('select_agent/', LeadDefaultAgentView.as_view(), name='select_agent'),
]