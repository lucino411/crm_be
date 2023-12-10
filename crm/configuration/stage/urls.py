from django.urls import path
from .views import StageListView, StageDetailView, StageCreateView, StageUpdateView, StageDeleteView

app_name = 'stage'

urlpatterns = [
    path('configuration/stage/',
         StageListView.as_view(), name='list'),
    path('configuration/stage/<int:pk>/', StageDetailView.as_view(), name='detail'),
    path('configuration/stage/create/', StageCreateView.as_view(), name='create'),
    path('configuration/stage/<int:pk>/update/', StageUpdateView.as_view(), name='update'),    
     path('configuration/stage/<int:pk>/delete/', StageDeleteView.as_view(), name='delete'),
]


