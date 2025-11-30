from django.urls import path
from catalog.views import (
    ProductListView, ProductDetailView, ContactsView,
    ProductCreateView, ProductUpdateView, ProductDeleteView,
    ProductUnpublishView,
    CategoryProductsView, AllCategoriesView
)
from catalog.apps import CatalogConfig

app_name = CatalogConfig.name

urlpatterns = [
    path('', ProductListView.as_view(), name='home'),  # Главная страница
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('contacts/', ContactsView.as_view(), name='contact'),
    path('product/create/', ProductCreateView.as_view(), name='product_create'),
    path('product/<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('product/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('product/<int:pk>/unpublish/', ProductUnpublishView.as_view(), name='product_unpublish'),
    path('categories/', AllCategoriesView.as_view(), name='all_categories'),
    path('category/<str:category_slug>/', CategoryProductsView.as_view(), name='category_products'),
]