from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import UserRegisterForm
from .utils import send_activation_email
from .tokens import account_activation_token
from booking.models import Booking

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_activation_email(request, user)
            messages.info(request, "Проверьте почту для активации аккаунта.")
            return redirect('core:index')
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
        login(request, user)
        messages.success(request, "Аккаунт активирован!")
        return redirect('core:index')
    else:
        messages.error(request, "Ссылка недействительна.")
        return redirect('core:index')

@login_required
def profile(request):
    active = request.user.bookings.filter(status='active')
    completed = request.user.bookings.exclude(status='active')
    return render(request, 'users/profile.html', {'active': active, 'completed': completed})
