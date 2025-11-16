from django.views.generic import ListView, DetailView, TemplateView
from django.views import View
from django.shortcuts import render
from .models import Product


# Заменяем home(request)
class ProductListView(ListView):
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'product'


# Заменяем product_detail(request, pk)
class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'


# Заменяем contacts(request)
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