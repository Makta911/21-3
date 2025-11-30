from django.core.cache import cache
from django.db import models
from .models import Product, Category


def get_all_products(use_cache=True):
    """
    Низкоуровневое кеширование для получения всех опубликованных продуктов
    """
    cache_key = 'all_published_products'

    # Пробуем получить из кеша
    if use_cache:
        cached_products = cache.get(cache_key)
        if cached_products is not None:
            print("📤 Список продуктов загружен из кеша")
            return cached_products

    # Если нет в кеше, делаем запрос к БД
    print("📥 Список продуктов загружен из базы данных")
    products = Product.objects.filter(
        publish_status='published'
    ).select_related('category', 'owner').order_by('-created_at')

    # Преобразуем QuerySet в список для кеширования
    products_list = list(products)

    # Кешируем результат на 10 минут
    if use_cache:
        cache.set(cache_key, products_list, 60 * 10)
        print("💾 Список продуктов сохранен в кеш")

    return products_list


def get_featured_products(limit=6, use_cache=True):
    """
    Кеширование избранных продуктов (например, последние добавленные)
    """
    cache_key = f'featured_products_{limit}'

    if use_cache:
        cached_products = cache.get(cache_key)
        if cached_products is not None:
            return cached_products

    # Получаем последние опубликованные продукты
    products = Product.objects.filter(
        publish_status='published'
    ).select_related('category', 'owner').order_by('-created_at')[:limit]

    products_list = list(products)

    if use_cache:
        cache.set(cache_key, products_list, 60 * 15)  # 15 минут

    return products_list


def get_products_count(use_cache=True):
    """
    Кеширование количества продуктов
    """
    cache_key = 'products_count'

    if use_cache:
        cached_count = cache.get(cache_key)
        if cached_count is not None:
            return cached_count

    count = Product.objects.filter(publish_status='published').count()

    if use_cache:
        cache.set(cache_key, count, 60 * 5)  # 5 минут

    return count


def invalidate_products_cache():
    """
    Инвалидация всего кеша продуктов
    """
    keys_to_delete = [
        'all_published_products',
        'products_count',
        'categories_with_counts',
    ]

    # Удаляем также все featured_products
    for key in list(cache.keys('*')):
        if key.startswith('featured_products_'):
            keys_to_delete.append(key)

    for key in keys_to_delete:
        cache.delete(key)

    print(f"🗑️ Очищен кеш продуктов: {keys_to_delete}")


def get_products_by_category(category_slug=None, category_id=None, use_cache=True):
    """
    Сервисная функция для получения продуктов по категории
    """
    # Создаем ключ для кеша
    if category_slug:
        cache_key = f'products_category_slug_{category_slug}'
    elif category_id:
        cache_key = f'products_category_id_{category_id}'
    else:
        cache_key = 'products_all'

    # Пробуем получить из кеша
    if use_cache:
        cached_products = cache.get(cache_key)
        if cached_products is not None:
            return cached_products

    # Если нет в кеше или use_cache=False, делаем запрос к БД
    products = Product.objects.filter(publish_status='published')

    if category_slug:
        products = products.filter(category__title__iexact=category_slug)
    elif category_id:
        products = products.filter(category_id=category_id)

    # Оптимизируем запросы
    products = products.select_related('category', 'owner').order_by('-created_at')

    # Преобразуем в список для кеширования
    products_list = list(products)

    # Кешируем результат
    if use_cache:
        cache.set(cache_key, products_list, 60 * 30)  # 30 минут

    return products_list


def get_categories_with_counts(use_cache=True):
    """
    Сервисная функция для получения категорий с количеством продуктов
    """
    cache_key = 'categories_with_counts'

    if use_cache:
        cached_categories = cache.get(cache_key)
        if cached_categories is not None:
            return cached_categories

    # Простой подход без сложных аннотаций
    categories = Category.objects.all().order_by('title')

    # Добавляем количество продуктов для каждой категории
    categories_with_counts = []
    for category in categories:
        product_count = Product.objects.filter(
            category=category,
            publish_status='published'
        ).count()

        if product_count > 0:
            # Создаем объект с дополнительным атрибутом
            category.product_count = product_count
            categories_with_counts.append(category)

    if use_cache:
        cache.set(cache_key, categories_with_counts, 60 * 60)  # 1 час

    return categories_with_counts


def invalidate_category_cache(category_slug=None, category_id=None):
    """
    Инвалидация кеша категорий
    """
    keys_to_delete = []

    if category_slug:
        keys_to_delete.append(f'products_category_slug_{category_slug}')
    if category_id:
        keys_to_delete.append(f'products_category_id_{category_id}')

    # Также очищаем общий кеш категорий
    keys_to_delete.append('categories_with_counts')
    keys_to_delete.append('all_published_products')
    keys_to_delete.append('products_count')

    for key in keys_to_delete:
        cache.delete(key)

    print(f"🗑️ Очищен кеш категорий: {keys_to_delete}")