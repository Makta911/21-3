from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from .models import Product
from .forms import ProductForm


class ProductListView(ListView):
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'product'

    def get_queryset(self):
        # Показываем только опубликованные продукты для всех пользователей
        return Product.objects.filter(publish_status='published')


class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'


class ContactsView(View):
    template_name = 'catalog/contacts.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        with open('catalog/text.txt', 'a', encoding='utf-8') as file:
            file.write(f"Имя пользователя: {name}\nТелефон: {phone}\nСообщение: {message}\n\n")

        print(f"Имя пользователя: {name}")
        print(f"Телефон: {phone}")
        print(f"Сообщение: {message}")
        print("---")

        return render(request, self.template_name)


class OwnerRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки, что пользователь - владелец продукта"""

    def test_func(self):
        product = self.get_object()
        user = self.request.user
        return product.owner == user


class ModeratorRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки прав модератора"""

    def test_func(self):
        user = self.request.user
        return (user.has_perm('catalog.can_unpublish_product') or
                user.has_perm('catalog.can_delete_any_product') or
                user.groups.filter(name='Модератор продуктов').exists())


class OwnerOrModeratorRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки, что пользователь - владелец ИЛИ модератор"""

    def test_func(self):
        product = self.get_object()
        user = self.request.user

        # Владелец может редактировать/удалять
        if product.owner == user:
            return True

        # Модератор может удалять
        if (user.has_perm('catalog.can_delete_any_product') or
                user.groups.filter(name='Модератор продуктов').exists()):
            return True

        return False


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:product_list')
    login_url = '/users/login/'
    redirect_field_name = 'next'

    def get_form_kwargs(self):
        """Передаем пользователя в форму"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Автоматически устанавливаем владельца при создании продукта"""
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    login_url = '/users/login/'
    redirect_field_name = 'next'

    def get_success_url(self):
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        """Передаем пользователя в форму"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def handle_no_permission(self):
        messages.error(self.request, 'Вы можете редактировать только свои продукты!')
        return redirect('catalog:product_list')


class ProductDeleteView(LoginRequiredMixin, OwnerOrModeratorRequiredMixin, DeleteView):
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog:product_list')
    login_url = '/users/login/'
    redirect_field_name = 'next'

    def handle_no_permission(self):
        messages.error(self.request, 'У вас нет прав для удаления этого продукта!')
        return redirect('catalog:product_list')


class ProductUnpublishView(LoginRequiredMixin, ModeratorRequiredMixin, View):
    """Представление для отмены публикации продукта"""

    def post(self, request, pk):
        product = Product.objects.get(pk=pk)
        if product.publish_status == 'published':
            product.publish_status = 'draft'
            product.save()
            messages.success(request, f'Публикация продукта "{product.name}" отменена')
        else:
            messages.warning(request, 'Продукт уже не опубликован')

        return redirect('catalog:product_detail', pk=pk)