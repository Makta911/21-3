from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Check Redis connection and basic functionality'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Проверяем подключение к Redis...')

        try:
            # Тест записи
            cache.set('test_connection', 'success', 10)

            # Тест чтения
            result = cache.get('test_connection')

            if result == 'success':
                self.stdout.write(
                    self.style.SUCCESS('✅ Redis подключен и работает корректно!')
                )

                # Дополнительные тесты
                cache.set('counter', 0, 30)
                cache.incr('counter')
                counter = cache.get('counter')
                self.stdout.write(f'📊 Тест счетчика: {counter}')

            else:
                self.stdout.write(
                    self.style.ERROR('❌ Ошибка: данные не сохранились в Redis')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка подключения к Redis: {e}')
            )
            self.stdout.write(
                self.style.WARNING('💡 Убедитесь, что Redis запущен на localhost:6379')
            )