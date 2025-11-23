from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import UserRegisterView, UserProfileView, UserDetailView
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
]