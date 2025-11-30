import django
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from catalog.models import Product
from django.core.cache import cache
from django.test import RequestFactory
from catalog.views import ProductDetailView


def test_product_caching():
    print("🧪 Тестируем кеширование страницы продукта...")

    # Получаем первый продукт
    product = Product.objects.first()
    if not product:
        print("❌ Нет продуктов для тестирования")
        return

    print(f"📦 Тестируем продукт: {product.name} (ID: {product.pk})")

    # Очищаем кеш перед тестом
    cache.clear()

    # Создаем mock запрос
    factory = RequestFactory()
    request = factory.get(f'/product/{product.pk}/')

    # Первый запрос - должен загрузить из базы
    start_time = time.time()
    view = ProductDetailView.as_view()
    response = view(request, pk=product.pk)
    first_load_time = time.time() - start_time
    print(f"⏱️  Первый запрос: {first_load_time:.3f} сек")

    # Второй запрос - должен загрузить из кеша
    start_time = time.time()
    response = view(request, pk=product.pk)
    second_load_time = time.time() - start_time
    print(f"⏱️  Второй запрос: {second_load_time:.3f} сек")

    # Проверяем ускорение
    if second_load_time < first_load_time:
        speedup = first_load_time / second_load_time
        print(f"🚀 Ускорение: {speedup:.1f}x")
    else:
        print("⚠️  Кеширование не работает или эффект незначительный")


if __name__ == "__main__":
    test_product_caching()