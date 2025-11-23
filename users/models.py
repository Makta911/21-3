from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Делаем email обязательным и уникальным
    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True,
        blank=False,
        null=False
    )

    avatar = models.ImageField(
        upload_to='users/avatars/',
        verbose_name='Аватар',
        blank=True,
        null=True,
        help_text='Загрузите изображение для аватара'
    )

    phone = models.CharField(
        max_length=20,
        verbose_name='Номер телефона',
        blank=True,
        null=True,
        help_text='Введите номер телефона'
    )

    country = models.CharField(
        max_length=100,
        verbose_name='Страна',
        blank=True,
        null=True,
        help_text='Введите название страны'
    )

    # Убираем username из обязательных полей
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        null=True
    )

    # Устанавливаем email как поле для авторизации
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['email']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # Автоматически создаем username из email если он не указан
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)