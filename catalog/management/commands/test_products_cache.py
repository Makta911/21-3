from django.core.management.base import BaseCommand
from django.core.cache import cache
from catalog.services import get_all_products, get_products_count, get_featured_products, invalidate_products_cache
import time


class Command(BaseCommand):
    help = 'Test products caching performance'

    def handle(self, *args, **options):
        self.stdout.write('🧪 Тестируем низкоуровневое кеширование продуктов...')

        # Очищаем кеш перед тестом
        invalidate_products_cache()

        # Тест 1: Первое получение (должно быть медленнее)
        self.stdout.write('\n📥 Первое получение (из базы данных):')
        start_time = time.time()
        products = get_all_products()
        first_time = time.time() - start_time
        self.stdout.write(f'   Время: {first_time:.3f} сек')
        self.stdout.write(f'   Продуктов: {len(products)}')

        # Тест 2: Второе получение (должно быть быстрее - из кеша)
        self.stdout.write('\n📤 Второе получение (из кеша):')
        start_time = time.time()
        products = get_all_products()
        second_time = time.time() - start_time
        self.stdout.write(f'   Время: {second_time:.3f} сек')
        self.stdout.write(f'   Продуктов: {len(products)}')

        # Сравнение производительности
        if second_time < first_time:
            speedup = first_time / second_time
            self.stdout.write(f'\n🚀 Ускорение: {speedup:.1f}x')
        else:
            self.stdout.write('\n⚠️  Кеширование не дало значительного ускорения')

        # Тест количества продуктов
        self.stdout.write(f'\n📊 Количество продуктов: {get_products_count()}')

        # Тест избранных продуктов
        featured = get_featured_products(limit=3)
        self.stdout.write(f'🔥 Избранные продукты: {len(featured)}')

        # Показываем ключи в кеше
        cache_keys = [key for key in cache.keys('*') if 'product' in key]
        self.stdout.write(f'\n🗝️  Ключи в кеше: {len(cache_keys)}')
        for key in cache_keys[:5]:  # Показываем первые 5 ключей
            self.stdout.write(f'   - {key}')

        self.stdout.write(self.style.SUCCESS('\n✅ Тестирование завершено!'))