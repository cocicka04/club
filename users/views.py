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
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter


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
        form = UserRegisterForm(request.POST, request=request)
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
        form = UserRegisterForm(request=request)
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

# Полностью замените функцию generate_captcha на эту

@never_cache
def generate_captcha(request):
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    code = ''.join(random.choice(chars) for _ in range(4))
    request.session['captcha_code'] = code.lower()

    width, height = 140, 60
    # Тёмный фон в стиле проекта
    bg_color = (10, 8, 26)  # #0a081a
    image = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(image)

    # Шрифт
    try:
        font = ImageFont.truetype('arial.ttf', 40)
    except IOError:
        font = ImageFont.load_default()

    # Неоновые цвета для символов
    colors = [
        (110, 203, 245),  # cyan
        (194, 82, 225),   # purple
        (88, 106, 226),   # royal blue
        (255, 255, 255)   # white
    ]

    # Рисуем символы с поворотом
    for i, char in enumerate(code):
        color = random.choice(colors)
        # Создаем временное изображение для символа
        txt_img = Image.new('RGBA', (40, 50), (0, 0, 0, 0))
        txt_draw = ImageDraw.Draw(txt_img)
        txt_draw.text((2, 2), char, font=font, fill=color)
        # Поворот до 25 градусов
        rotated = txt_img.rotate(random.randint(-25, 25), expand=1, fillcolor=(0,0,0,0))
        # Позиция символа с небольшим смещением
        x = 15 + i * 30 + random.randint(-5, 5)
        y = random.randint(5, 10)
        image.paste(rotated, (x, y), rotated)

    # Шум: линии
    for _ in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line(((x1, y1), (x2, y2)), fill=(100, 100, 100), width=1)

    # Шум: точки
    for _ in range(80):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.point((x, y), fill=(200, 200, 200))

    # Легкое размытие для сглаживания
    image = image.filter(ImageFilter.GaussianBlur(0.3))

    buffer = BytesIO()
    image.save(buffer, format='PNG')
    return HttpResponse(buffer.getvalue(), content_type='image/png')