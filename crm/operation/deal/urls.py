from django.urls import path
from .views import HomeDealView, DealListView, DealDetailView, DealUpdateView, DealDeleteView, DealHomeTaskView, DealTaskListView, DealTaskDetailView, DealTaskUpdateView, DealTaskDeleteView, DealTaskCreateView

app_name = 'deal'

urlpatterns = [
    path('list/', HomeDealView.as_view(), name='list'),
    path('deals_json/', DealListView.as_view(), name='deal-json'),
    # path('create/', DealCreateView.as_view(), name='create'),
    path('<int:pk>/', DealDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', DealUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', DealDeleteView.as_view(), name='delete'),

    path('task/list/', DealHomeTaskView.as_view(), name='task-list'),
    path('tasks_json/', DealTaskListView.as_view(), name='task-json'),
    path('<int:deal_pk>/task/create/', DealTaskCreateView.as_view(), name='task-create'),
    path('task/<int:pk>/', DealTaskDetailView.as_view(), name='task-detail'),
    path('task/<int:pk>/update/', DealTaskUpdateView.as_view(), name='task-update'),
    path('task/<int:pk>/delete/', DealTaskDeleteView.as_view(), name='task-delete'),
]
