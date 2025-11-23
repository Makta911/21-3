from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.views import View
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Product
from .forms import ProductForm


# Доступно для всех - просмотр списка продуктов
class ProductListView(ListView):
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'product'


# Доступно для всех - просмотр деталей продукта
class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'


# Доступно для всех - страница контактов
class ContactsView(View):
    template_name = 'catalog/contacts.html'

    def get(self, request):
        # Обработка GET запроса - просто показываем страницу
        return render(request, self.template_name)

    def post(self, request):
        # Обработка POST запроса - сохраняем данные формы
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        # Сохраняем в файл
        with open('catalog/text.txt', 'a', encoding='utf-8') as file:
            file.write(f"Имя пользователя: {name}\nТелефон: {phone}\nСообщение: {message}\n\n")

        # Выводим в консоль
        print(f"Имя пользователя: {name}")
        print(f"Телефон: {phone}")
        print(f"Сообщение: {message}")
        print("---")

        return render(request, self.template_name)


# Только для авторизованных пользователей - создание продукта
class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:product_list')
    login_url = '/users/login/'  # Перенаправление на страницу входа
    redirect_field_name = 'next'  # Сохранение URL для возврата после входа


# Только для авторизованных пользователей - редактирование продукта
class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    login_url = '/users/login/'
    redirect_field_name = 'next'

    def get_success_url(self):
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.pk})


# Только для авторизованных пользователей - удаление продукта
class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog:product_list')
    login_url = '/users/login/'
    redirect_field_name = 'next'