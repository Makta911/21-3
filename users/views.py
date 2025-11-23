from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, DetailView, FormView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth import login

from .models import User
from .forms import UserRegisterForm, UserLoginForm, UserProfileForm
from .services import send_welcome_email


class UserRegisterView(SuccessMessageMixin, CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('catalog:home')
    success_message = 'Регистрация прошла успешно! Добро пожаловать!'

    def form_valid(self, form):
        """Обработка успешной регистрации"""
        response = super().form_valid(form)

        # Автоматически входим пользователя после регистрации
        user = form.save()
        login(self.request, user)

        # Отправляем приветственное письмо
        try:
            send_welcome_email(
                user_email=user.email,
                user_name=user.first_name or user.email
            )
            messages.info(self.request, 'На вашу почту отправлено приветственное письмо!')
        except Exception as e:
            # Если отправка письма не удалась, продолжаем без ошибки
            messages.warning(self.request, 'Регистрация прошла успешно, но не удалось отправить приветственное письмо.')

        return response


class UserLoginView(SuccessMessageMixin, LoginView):
    form_class = UserLoginForm
    template_name = 'users/login.html'
    success_message = 'Вы успешно вошли в систему!'

    def get_success_url(self):
        return reverse_lazy('catalog:home')


class UserLogoutView(LogoutView):
    def get_next_page(self):
        messages.info(self.request, 'Вы успешно вышли из системы!')
        return reverse_lazy('catalog:home')


class UserProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_message = 'Профиль успешно обновлен!'

    def get_success_url(self):
        return reverse('users:profile')

    def get_object(self, queryset=None):
        return self.request.user


class UserDetailView(DetailView):
    model = User
    template_name = 'users/user_detail.html'
    context_object_name = 'user_object'