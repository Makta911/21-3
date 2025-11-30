from django import forms
from django.utils import timezone
from .models import Product


class ProductForm(forms.ModelForm):
    # Список запрещенных слов
    FORBIDDEN_WORDS = [
        'казино', 'криптовалюта', 'крипта', 'биржа',
        'дешево', 'бесплатно', 'обман', 'полиция', 'радар'
    ]

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'image', 'manufactured_at', 'publish_status']
        # Убрали is_published, добавили publish_status
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название продукта'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите описание продукта',
                'rows': 4
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'manufactured_at': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'publish_status': forms.Select(attrs={
                'class': 'form-select'
            })
        }

    def __init__(self, *args, **kwargs):
        # Получаем пользователя из kwargs
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.add_form_control_class()
        self.update_placeholders()

        # Установить текущую дату по умолчанию для manufactured_at
        if not self.instance.pk and 'manufactured_at' in self.fields:
            self.fields['manufactured_at'].initial = timezone.now().date()

        # Логика для поля статуса публикации
        self.handle_publish_status_field()

    def handle_publish_status_field(self):
        """Управление полем статуса публикации в зависимости от прав пользователя"""
        if 'publish_status' in self.fields:
            # Если пользователь не модератор, ограничиваем выбор статусов
            if self.user and not self.has_moderator_permissions():
                # Обычные пользователи могут выбирать только черновик
                self.fields['publish_status'].choices = [
                    ('draft', 'Черновик'),
                ]
                self.fields['publish_status'].initial = 'draft'
                # Добавляем подсказку
                self.fields['publish_status'].help_text = 'Только модераторы могут публиковать продукты'
            else:
                # Модераторы видят все статусы
                self.fields['publish_status'].help_text = 'Выберите статус публикации продукта'

    def has_moderator_permissions(self):
        """Проверяет, есть ли у пользователя права модератора"""
        if not self.user:
            return False
        return (self.user.has_perm('catalog.can_unpublish_product') or
                self.user.has_perm('catalog.can_delete_any_product') or
                self.user.groups.filter(name='Модератор продуктов').exists())

    def add_form_control_class(self):
        """Добавляет класс form-control ко всем полям"""
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
            elif 'form-control' not in field.widget.attrs['class']:
                field.widget.attrs['class'] += ' form-control'

    def update_placeholders(self):
        """Обновляет плейсхолдеры для полей"""
        placeholders = {
            'name': 'Введите название продукта',
            'description': 'Опишите особенности продукта...',
            'price': '0.00',
            'category': 'Выберите категорию',
            'manufactured_at': 'Выберите дату производства',
        }

        for field_name, placeholder in placeholders.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs['placeholder'] = placeholder

    def clean_name(self):
        """Валидация названия продукта"""
        name = self.cleaned_data['name'].lower()

        for word in self.FORBIDDEN_WORDS:
            if word in name:
                raise forms.ValidationError(
                    f'Название продукта содержит запрещенное слово: "{word}"'
                )

        return self.cleaned_data['name']

    def clean_description(self):
        """Валидация описания продукта"""
        description = self.cleaned_data['description'].lower()

        for word in self.FORBIDDEN_WORDS:
            if word in description:
                raise forms.ValidationError(
                    f'Описание продукта содержит запрещенное слово: "{word}"'
                )

        return self.cleaned_data['description']

    def clean_price(self):
        """Валидация цены продукта - не может быть отрицательной"""
        price = self.cleaned_data['price']

        if price < 0:
            raise forms.ValidationError(
                'Цена продукта не может быть отрицательной'
            )

        if price == 0:
            raise forms.ValidationError(
                'Цена продукта не может быть равна нулю'
            )

        return price

    def clean_publish_status(self):
        """Валидация статуса публикации"""
        publish_status = self.cleaned_data['publish_status']

        # Если пользователь не модератор, не позволяем устанавливать статус "published"
        if (publish_status == 'published' and self.user and
                not self.has_moderator_permissions()):
            raise forms.ValidationError(
                'Только модераторы могут публиковать продукты'
            )

        return publish_status