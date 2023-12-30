from django.urls import path
from .views import HomeLeadView, LeadListView, LeadCreateView, LeadDetailView, LeadUpdateView, LeadDeleteView, TaskCreateView, HomeTaskView, TaskListView, TaskDetailView, TaskDeleteView, TaskUpdateView

app_name = 'lead'

urlpatterns = [
    path('list/', HomeLeadView.as_view(), name='list'),
    path('leads_json/', LeadListView.as_view(), name='lead-json'),
    path('create/', LeadCreateView.as_view(), name='create'),
    path('<int:pk>/', LeadDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', LeadUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', LeadDeleteView.as_view(), name='delete'),


    path('task/list/', HomeTaskView.as_view(), name='task-list'),
    path('tasks_json/', TaskListView.as_view(), name='task-json'),
    path('<int:pk>/task/create/', TaskCreateView.as_view(), name='task-create'),
    path('task/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('task/<int:pk>/update/', TaskUpdateView.as_view(), name='task-update'),
    path('task/<int:pk>/delete/', TaskDeleteView.as_view(), name='task-delete'),


]
