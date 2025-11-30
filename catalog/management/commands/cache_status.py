from django.core.management.base import BaseCommand
from django.core.cache import cache
from catalog.models import Product


class Command(BaseCommand):
    help = 'Show cache status for products'

    def handle(self, *args, **options):
        self.stdout.write('📊 Статус кеширования продуктов:')

        products = Product.objects.all()[:5]  # Первые 5 продуктов

        for product in products:
            cache_key = f'product_detail_{product.pk}'
            is_cached = cache.get(cache_key) is not None

            status = '✅ В кеше' if is_cached else '❌ Не в кеше'
            self.stdout.write(f'   {product.name} (ID: {product.pk}): {status}')

        # Общая статистика
        self.stdout.write(f'\n📈 Всего продуктов в базе: {Product.objects.count()}')