from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from catalyst.views import confirm_email, password_reset_request, password_reset_confirm

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('confirm-email/', confirm_email, name='confirm_email'),
path('password-reset/', password_reset_request, name='password_reset'),
path('password-reset/confirm/', password_reset_confirm, name='password_reset_confirm'),
]
