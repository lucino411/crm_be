from django.urls import path
from .views import HomeLeadView, LeadListView, LeadCreateView, LeadUpdateView, LeadDetailView, LeadDeleteView, LeadTaskCreateView, LeadHomeTaskView, LeadTaskListView, LeadTaskDetailView, LeadTaskDeleteView, LeadTaskUpdateView, convert_lead_to_deal

app_name = 'lead'

urlpatterns = [
    path('list/', HomeLeadView.as_view(), name='list'),
    path('leads_json/', LeadListView.as_view(), name='lead-json'),
    path('create/', LeadCreateView.as_view(), name='create'),
    path('<int:pk>/', LeadDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', LeadUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', LeadDeleteView.as_view(), name='delete'),
    path('converted_to_deal/<int:pk>/', convert_lead_to_deal, name='converted-to-deal'),


    path('task/list/', LeadHomeTaskView.as_view(), name='task-list'),
    path('tasks_json/', LeadTaskListView.as_view(), name='task-json'),
    path('<int:lead_pk>/task/create/', LeadTaskCreateView.as_view(), name='task-create'),
    path('task/<int:pk>/', LeadTaskDetailView.as_view(), name='task-detail'),
    path('task/<int:pk>/update/', LeadTaskUpdateView.as_view(), name='task-update'),
    path('task/<int:pk>/delete/', LeadTaskDeleteView.as_view(), name='task-delete'),

]
