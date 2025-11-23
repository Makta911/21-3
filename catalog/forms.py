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
        fields = ['name', 'description', 'price', 'category', 'image', 'manufactured_at', 'is_published']
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
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_form_control_class()
        self.update_placeholders()

        # Установить текущую дату по умолчанию для manufactured_at
        if not self.instance.pk and 'manufactured_at' in self.fields:
            self.fields['manufactured_at'].initial = timezone.now().date()

    def add_form_control_class(self):
        """Добавляет класс form-control ко всем полям"""
        for field_name, field in self.fields.items():
            if field_name not in ['is_published']:  # Для чекбокса не добавляем form-control
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