from django.urls import path
from catalog.views import (
    ProductListView, ProductDetailView, ContactsView,
    ProductCreateView, ProductUpdateView, ProductDeleteView
)
from catalog.apps import CatalogConfig

app_name = CatalogConfig.name

urlpatterns = [
    path('', ProductListView.as_view(), name='home'),
    path('products/', ProductListView.as_view(), name='product_list'),  # Добавьте этот путь
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('contacts/', ContactsView.as_view(), name='contact'),
    path('product/create/', ProductCreateView.as_view(), name='product_create'),
    path('product/<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('product/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
]