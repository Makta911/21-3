from django.contrib import admin
from catalog.models import Product, Category

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'category', 'publish_status', 'created_at')
    list_filter = ('category', 'publish_status', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('publish_status',)  # Позволяет быстро менять статус в списке


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)