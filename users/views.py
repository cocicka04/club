# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate  # Добавил authenticate
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
from .utils import send_activation_email
from .tokens import account_activation_token
from booking.models import Booking
from booking.utils import finish_expired_bookings


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
                send_activation_email(request, user)
                messages.success(
                    request,
                    "Регистрация успешна! Проверьте почту для активации аккаунта."
                )
                return redirect('places:list')

            messages.error(request, "Ошибка авторизации")
            return redirect('users:login')

    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        
        # 🔹 Авторизуем пользователя после активации
        login(request, user)
        
        messages.success(request, "Аккаунт успешно активирован!")
        return redirect('places:index')

    else:
        messages.error(request, "Ссылка активации недействительна.")
        return redirect('users:login')

@login_required
def profile(request):
    # 🔹 автоматически закрываем истёкшие брони
    finish_expired_bookings(user=request.user)

    # 🔹 активные сессии
    active = Booking.objects.filter(
        user=request.user,
        status=Booking.STATUS_ACTIVE
    )

    # 🔹 история (ТОЛЬКО завершённые и отменённые)
    completed = Booking.objects.filter(
        user=request.user,
        status__in=[
            Booking.STATUS_FINISHED,
            Booking.STATUS_CANCELED
        ]
    ).order_by('-start_time')

    return render(request, 'users/profile.html', {
        'active': active,
        'completed': completed,
    })