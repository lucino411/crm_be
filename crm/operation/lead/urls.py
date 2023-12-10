from django.urls import path
from .views import HomeLeadView, LeadListView, LeadCreateView, LeadDetailView, LeadUpdateView, LeadDeleteView

app_name = 'lead'

urlpatterns = [
    # path('conf/', HomeConfLeadView.as_view(), name='leads_conf'),
    path('lead/list/', HomeLeadView.as_view(), name='list'),
    path('leads_json/', LeadListView.as_view(), name='lead-json'),
    path('lead/create/', LeadCreateView.as_view(), name='create'),
    # path('create_be/', LeadCreateAnonymousView.as_view(), name='lead_create_be'),
    path('lead/<int:pk>/', LeadDetailView.as_view(), name='detail'),
    path('lead/<int:pk>/update/', LeadUpdateView.as_view(), name='update'),
    path('lead/<int:pk>/delete/', LeadDeleteView.as_view(), name='delete'),
    # path('select_agent/', LeadDefaultAgentView.as_view(), name='select_agent'),
]