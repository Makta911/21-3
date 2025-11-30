from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Product


class Command(BaseCommand):
    help = 'Create moderator groups with permissions'

    def handle(self, *args, **options):
        # Создаем группу "Модератор продуктов"
        moderator_group, created = Group.objects.get_or_create(name='Модератор продуктов')

        if created:
            self.stdout.write(
                self.style.SUCCESS('Группа "Модератор продуктов" создана')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Группа "Модератор продуктов" уже существует')
            )

        # Получаем разрешения
        content_type = ContentType.objects.get_for_model(Product)

        try:
            # Разрешение на отмену публикации
            unpublish_permission = Permission.objects.get(
                codename='can_unpublish_product',
                content_type=content_type
            )
        except Permission.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Разрешение can_unpublish_product не найдено')
            )
            return

        try:
            # Разрешение на удаление любого продукта
            delete_permission = Permission.objects.get(
                codename='delete_product',
                content_type=content_type
            )
        except Permission.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Разрешение delete_product не найдено')
            )
            return

        # Добавляем разрешения в группу
        moderator_group.permissions.add(unpublish_permission, delete_permission)

        self.stdout.write(
            self.style.SUCCESS(
                f'Добавлены разрешения для группы "Модератор продуктов": '
                f'{unpublish_permission.name}, {delete_permission.name}'
            )
        )