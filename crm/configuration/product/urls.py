from django.urls import path
from .views import (
    ProductListView, ProductCreateView, ProductDetailView, ProductUpdateView, ProductDeleteView, 
    ProductCategoryListView, ProductCategoryCreateView, ProductCategoryDetailView, ProductCategoryUpdateView, ProductCategoryDeleteView
)

app_name = 'product'

urlpatterns = [
    path('list/', ProductListView.as_view(), name='list'),
    path('create/', ProductCreateView.as_view(), name='create'),
    path('<int:pk>/', ProductDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', ProductUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='delete'),

    path('list/', ProductCategoryListView.as_view(), name='category-list'),
    path('create/', ProductCategoryCreateView.as_view(), name='category-create'),
    path('<int:pk>/', ProductCategoryDetailView.as_view(), name='category-detail'),
    path('<int:pk>/update/', ProductCategoryUpdateView.as_view(), name='category-update'),
    path('<int:pk>/delete/', ProductCategoryDeleteView.as_view(), name='category-delete'),
]
