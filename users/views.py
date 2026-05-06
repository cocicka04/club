from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
import json
from .forms import UserRegisterForm
from booking.models import Booking
from booking.utils import finish_expired_bookings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from places.models import Place
from tariffs.models import Tariff, Category
from django.db.models import Q
from datetime import datetime


def is_superuser(user):
    return user.is_superuser


# ====== ДЕКОРАТОР ДЛЯ КАССИРА ======
def is_admin_or_cashier(user):
    return user.is_authenticated and (
        user.is_superuser or
        (hasattr(user, 'profile') and user.profile.role in ['admin', 'cashier'])
    )

def admin_or_cashier_required(view_func):
    return user_passes_test(is_admin_or_cashier, login_url='users:login')(view_func)


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )
            if user:
                login(request, user)
                messages.success(request, "Регистрация успешна!")
                return redirect('users:profile')
            messages.error(request, "Ошибка авторизации")
            return redirect('users:login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    finish_expired_bookings(user=request.user)
    profile = request.user.profile

    if request.method == 'POST' and request.FILES.get('avatar'):
        profile.avatar = request.FILES['avatar']
        profile.save()
        messages.success(request, "Фото профиля обновлено")
        return redirect('users:profile')

    active = Booking.objects.filter(
        user=request.user,
        status=Booking.STATUS_ACTIVE
    )
    completed = Booking.objects.filter(
        user=request.user,
        status__in=[Booking.STATUS_FINISHED, Booking.STATUS_CANCELED]
    ).order_by('-start_time')

    paginator = Paginator(completed, 10)
    page_number = request.GET.get('page')
    completed = paginator.get_page(page_number)

    return render(request, 'users/profile.html', {
        'active': active,
        'completed': completed,
    })


def update_profile(request):
    if request.method == "POST":
        data = json.loads(request.body)
        request.user.username = data.get("username", request.user.username)
        request.user.email = data.get("email", request.user.email)
        request.user.save()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})


# ====== AJAX: СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ (АДМИН) ======
@staff_member_required
def admin_user_create_ajax(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        role = request.POST.get('role', 'user')

        errors = {}

        if not username:
            errors['username'] = ['Имя пользователя обязательно.']
        elif len(username) < 3:
            errors['username'] = ['Минимум 3 символа.']
        elif len(username) > 12:
            errors['username'] = ['Максимум 12 символов.']
        elif not username.replace('_', '').isalnum():
            errors['username'] = ['Только латиница, цифры и _.']
        elif User.objects.filter(username=username).exists():
            errors['username'] = ['Пользователь с таким именем уже существует.']

        if not email:
            errors['email'] = ['Email обязателен.']
        elif '@' not in email or '.' not in email:
            errors['email'] = ['Введите корректный email.']
        elif User.objects.filter(email=email).exists():
            errors['email'] = ['Этот email уже используется.']

        if len(password1) < 6:
            errors['password1'] = ['Пароль должен быть минимум 6 символов.']
        elif password1 != password2:
            errors['password2'] = ['Пароли не совпадают.']

        if role not in ['user', 'cashier', 'admin']:
            errors['role'] = ['Неверная роль.']

        if errors:
            return JsonResponse({'success': False, 'errors': errors})

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.profile.role = role
        user.profile.save()
        user.save()

        return JsonResponse({'success': True})

    return JsonResponse({'success': False})


# ====== AJAX: РЕДАКТИРОВАНИЕ ПОЛЬЗОВАТЕЛЯ (АДМИН) ======
@staff_member_required
def admin_user_edit_ajax(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        role = request.POST.get('role', 'user')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Пользователь не найден'})

        errors = {}

        if not username:
            errors['username'] = ['Имя пользователя обязательно.']
        elif len(username) < 3:
            errors['username'] = ['Минимум 3 символа.']
        elif len(username) > 12:
            errors['username'] = ['Максимум 12 символов.']
        elif not username.replace('_', '').isalnum():
            errors['username'] = ['Только латиница, цифры и _.']
        elif User.objects.filter(username=username).exclude(id=user.id).exists():
            errors['username'] = ['Пользователь с таким именем уже существует.']

        if not email:
            errors['email'] = ['Email обязателен.']
        elif '@' not in email or '.' not in email:
            errors['email'] = ['Введите корректный email.']
        elif User.objects.filter(email=email).exclude(id=user.id).exists():
            errors['email'] = ['Этот email уже используется.']

        if role not in ['user', 'cashier', 'admin']:
            errors['role'] = ['Неверная роль.']

        if errors:
            return JsonResponse({'success': False, 'errors': errors})

        user.username = username
        user.email = email
        user.profile.role = role
        user.profile.save()
        user.save()

        return JsonResponse({'success': True})

    return JsonResponse({'success': False})

