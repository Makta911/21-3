from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.views import View
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from .models import Product
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .forms import ProductForm
from .services import get_all_products, get_featured_products, get_products_count, invalidate_products_cache, \
    get_categories_with_counts
from .models import Category


class ProductListView(ListView):
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'product'
    paginate_by = 12  # Добавляем пагинацию

    def get_queryset(self):
        """
        Используем низкоуровневое кеширование для получения продуктов
        """
        return get_all_products()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Добавляем дополнительную информацию в контекст
        context['products_count'] = get_products_count()
        context['featured_products'] = get_featured_products(limit=4)
        context['categories'] = get_categories_with_counts()
        context['page_title'] = "Все продукты"

        # Информация о кешировании для отладки
        context['cache_info'] = {
            'total_products': context['products_count'],
            'featured_count': len(context['featured_products']),
            'current_page': self.request.GET.get('page', 1)
        }

        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    @method_decorator(cache_page(60 * 15))  # Кешировать на 15 минут
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        """Получаем объект продукта с оптимизацией запросов"""
        obj = super().get_object(queryset)
        # Оптимизируем запросы, предзагружая связанные объекты
        return Product.objects.select_related('category', 'owner').get(pk=obj.pk)


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
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        # Инвалидируем кеш при создании нового продукта
        from .services import invalidate_products_cache, invalidate_category_cache
        invalidate_products_cache()
        if self.object.category:
            invalidate_category_cache(category_id=self.object.category.id)
        return response


class ProductUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    login_url = '/users/login/'
    redirect_field_name = 'next'

    def get_success_url(self):
        # Инвалидируем кеш при обновлении продукта
        from .services import invalidate_products_cache, invalidate_category_cache, invalidate_product_cache
        invalidate_products_cache()
        invalidate_product_cache(self.object.pk)
        if self.object.category:
            invalidate_category_cache(category_id=self.object.category.id)
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
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

    def delete(self, request, *args, **kwargs):
        # Инвалидируем кеш перед удалением
        from .services import invalidate_products_cache, invalidate_category_cache, invalidate_product_cache
        product = self.get_object()
        category_id = product.category.id if product.category else None

        invalidate_products_cache()
        invalidate_product_cache(product.pk)
        if category_id:
            invalidate_category_cache(category_id=category_id)

        return super().delete(request, *args, **kwargs)

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


class CategoryProductsView(ListView):
    """
    Представление для отображения продуктов по категории
    """
    template_name = 'catalog/category_products.html'
    context_object_name = 'products'
    paginate_by = 12  # Пагинация по 12 продуктов на странице

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        return get_products_by_category(category_slug=category_slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('category_slug')

        # Получаем информацию о категории
        if category_slug:
            context['current_category'] = get_object_or_404(
                Category,
                title__iexact=category_slug
            )

        # Получаем все категории для сайдбара
        context['categories'] = get_categories_with_counts()
        context['page_title'] = f"Продукты в категории '{category_slug}'" if category_slug else "Все продукты"

        return context


class AllCategoriesView(TemplateView):
    """
    Представление для отображения всех категорий
    """
    template_name = 'catalog/all_categories.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = get_categories_with_counts()
        context['page_title'] = "Все категории"
        return context