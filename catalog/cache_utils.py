from django.core.cache import cache
from django.conf import settings

def get_product_cache_key(product_id, user_id=None):
    """Генерирует ключ кеша для продукта"""
    if user_id:
        return f'product_{product_id}_user_{user_id}'
    return f'product_{product_id}_anonymous'

def cache_product_detail(product, user_id=None):
    """Кеширует данные продукта"""
    cache_key = get_product_cache_key(product.pk, user_id)
    cache.set(cache_key, product, settings.CACHE_TIMES['product_detail'])
    return cache_key

def get_cached_product(product_id, user_id=None):
    """Получает продукт из кеша"""
    cache_key = get_product_cache_key(product_id, user_id)
    return cache.get(cache_key)

def invalidate_product_cache(product_id):
    """Инвалидирует кеш продукта (при обновлении/удалении)"""
    # Удаляем все варианты кеша для этого продукта
    cache.delete_pattern(f'product_{product_id}*')
    print(f"🗑️ Кеш для продукта {product_id} очищен")