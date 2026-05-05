from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
import json

from .forms import UserRegisterForm
from booking.models import Booking
from booking.utils import finish_expired_bookings


def is_superuser(user):
    return user.is_superuser


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