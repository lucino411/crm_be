from django.urls import path
from .views import (
    ProductListView, ProductCreateView, ProductDetailView, ProductUpdateView, ProductDeleteView, 
    ProductCategoryListView, ProductCategoryCreateView, ProductCategoryDetailView, ProductCategoryUpdateView, ProductCategoryDeleteView
)

app_name = 'product'


urlpatterns = [
    # Rutas para Product
    path('list/', ProductListView.as_view(), name='list'),
    path('create/', ProductCreateView.as_view(), name='create'),
    path('<int:pk>/', ProductDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', ProductUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='delete'),

    # Rutas para ProductCategory con prefijo 'category-'
    path('categories/list/', ProductCategoryListView.as_view(), name='category-list'),
    path('categories/create/', ProductCategoryCreateView.as_view(), name='category-create'),
    path('categories/<int:pk>/', ProductCategoryDetailView.as_view(), name='category-detail'),
    path('categories/<int:pk>/update/', ProductCategoryUpdateView.as_view(), name='category-update'),
    path('categories/<int:pk>/delete/', ProductCategoryDeleteView.as_view(), name='category-delete'),
]
