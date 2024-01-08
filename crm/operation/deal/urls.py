from django.urls import path
# from .views import HomeDealView, DealListView, DealCreateView, DealDetailView, DealUpdateView, DealDeleteView, TaskCreateView, HomeTaskView, TaskListView, TaskDetailView, TaskDeleteView, TaskUpdateView
from .views import HomeDealView, DealListView
app_name = 'deal'

urlpatterns = [
    path('list/', HomeDealView.as_view(), name='list'),
    path('deals_json/', DealListView.as_view(), name='deal-json'),
    # path('create/', DealCreateView.as_view(), name='create'),
    # path('<int:pk>/', DealDetailView.as_view(), name='detail'),
    # path('<int:pk>/update/', DealUpdateView.as_view(), name='update'),
    # path('<int:pk>/delete/', DealDeleteView.as_view(), name='delete'),


    # path('task/list/', HomeTaskView.as_view(), name='task-list'),
    # path('tasks_json/', TaskListView.as_view(), name='task-json'),
    # path('<int:deal_pk>/task/create/', TaskCreateView.as_view(), name='task-create'),
    # path('task/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    # path('task/<int:pk>/update/', TaskUpdateView.as_view(), name='task-update'),
    # path('task/<int:pk>/delete/', TaskDeleteView.as_view(), name='task-delete'),

]
