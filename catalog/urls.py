from django.urls import path
from catalog.views import ProductListView, ProductDetailView, ContactsView
from catalog.apps import CatalogConfig

app_name = CatalogConfig.name

urlpatterns = [
    path('', ProductListView.as_view(), name='home'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('contacts/', ContactsView.as_view(), name='contact')
]