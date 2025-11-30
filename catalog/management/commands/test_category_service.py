from django.core.management.base import BaseCommand
from catalog.services import get_products_by_category, get_categories_with_counts
from catalog.models import Category


class Command(BaseCommand):
    help = 'Test category service functions'

    def handle(self, *args, **options):
        self.stdout.write('🧪 Тестируем сервисные функции категорий...')

        # Тест получения всех категорий
        categories = get_categories_with_counts()
        self.stdout.write(f'📂 Найдено категорий: {len(categories)}')

        for category in categories:
            self.stdout.write(f'   {category.title}: {category.product_count} продуктов')

        # Тест получения продуктов по категории
        if categories:
            first_category = categories[0]
            products = get_products_by_category(category_slug=first_category.title)
            self.stdout.write(f'📦 Продуктов в категории "{first_category.title}": {len(products)}')

        # Тест получения всех продуктов
        all_products = get_products_by_category()
        self.stdout.write(f'📊 Всего опубликованных продуктов: {len(all_products)}')

        self.stdout.write(self.style.SUCCESS('✅ Тестирование завершено!'))