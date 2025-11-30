from django.db import models
from django.conf import settings


class Category(models.Model):
    title = models.CharField(
        max_length=100,
        verbose_name="Наименование категории",
        help_text="Укажите название категории",
        default="Default Title",
    )
    description = models.TextField(
        verbose_name="Описание категории",
        help_text="Добавьте описание категории",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["title"]

    def __str__(self):
        return self.title


class Product(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Наименование продукта",
        help_text="Укажите название продукта",
    )
    description = models.TextField(
        verbose_name="Описание продукта",
        help_text="Добавьте описание продукта",
        blank=True,
        null=True,
    )
    image = models.ImageField(
        upload_to="catalog/images",
        blank=True,
        null=True,
        verbose_name="Фото",
        help_text="Загрузите изображение товара",
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Категория",
        related_name="products",
    )
    price = models.FloatField(
        verbose_name="Цена",
        help_text="Укажите стоимость продукта",
    )

    # Добавляем поле владельца
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Владелец",
        help_text="Пользователь, создавший продукт",
        related_name="products"
    )

    # Поле для статуса публикации
    PUBLISH_STATUS = [
        ('draft', 'Черновик'),
        ('published', 'Опубликовано'),
        ('rejected', 'Отклонено'),
    ]

    publish_status = models.CharField(
        max_length=20,
        choices=PUBLISH_STATUS,
        default='draft',
        verbose_name="Статус публикации",
        help_text="Выберите статус публикации продукта"
    )

    manufactured_at = models.DateField(
        verbose_name="Дата производства",
        null=True,
        blank=True,
        help_text="Дата производства продукта",
    )

    created_at = models.DateField(
        auto_now_add=True,
        verbose_name="Дата создания записи",
        help_text="Дата добавления продукта в каталог",
    )
    updated_at = models.DateField(
        auto_now=True,
        verbose_name="Дата последнего изменения продукта",
        help_text="Дата последнего изменения продукта",
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name="Маркер публикации",
        help_text="Укажите, будет ли продукт опубликован",
    )

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ["name", "price"]
        permissions = [
            ("can_cancel_publication", "Can cancel publication"),
            ("can_edit_description", "Can edit description"),
            ("can_change_category", "Can change category"),
            ("can_unpublish_product", "Может отменять публикацию продукта"),
            ("can_delete_any_product", "Может удалять любой продукт"),
        ]

    def __str__(self):
        return self.name

    @property
    def is_published_display(self):
        """Возвращает отображаемое значение статуса публикации"""
        return dict(self.PUBLISH_STATUS).get(self.publish_status, 'Неизвестно')