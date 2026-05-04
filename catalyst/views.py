from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import json
from users.models import News
from users.forms import UserRegisterForm
from tariffs.models import Tariff
from booking.models import Booking
from places.models import Place
from booking.utils import finish_expired_bookings
from .chat_service import ask_gigachat
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

# ===== СТАТИЧНЫЕ СТРАНИЦЫ =====

def home(request):
    tariffs = Tariff.objects.select_related('category').order_by('-id')
    context = {
        "now": timezone.now(),
        "tariffs": tariffs
    }
    return render(request, "index.html", context)


def contacts(request):
    return render(request, 'contacts.html')


def about(request):
    return render(request, 'about.html')


# ===== НОВОСТИ =====

def news_page(request):
    news = News.objects.all()
    paginator = Paginator(news, 5)
    page_number = request.GET.get('page')
    news = paginator.get_page(page_number)

    if request.method == 'POST' and request.user.is_superuser:
        if 'create' in request.POST:
            News.objects.create(
                title=request.POST.get('title', '')[:120],
                text=request.POST.get('text', '')[:1000]
            )
            return redirect('news')
        if 'edit' in request.POST:
            item = get_object_or_404(News, pk=request.POST.get('news_id'))
            item.title = request.POST.get('title', '')[:120]
            item.text = request.POST.get('text', '')[:1000]
            item.save()
            return redirect('news')

    return render(request, 'news.html', {'news': news})


@staff_member_required
def news_delete(request, pk):
    News.objects.filter(pk=pk).delete()
    return redirect('news')


# ===== АДМИН-ПАНЕЛЬ =====

@staff_member_required
def admin_dashboard(request):
    context = {
        "bookings": Booking.objects.all().order_by('-start_time'),
        "places": Place.objects.all(),
        "tariffs": Tariff.objects.all(),
        "users": User.objects.all(),
        "news": News.objects.all().order_by('-created_at'),
    }
    return render(request, "users/dashboard.html", context)


# ===== РЕГИСТРАЦИЯ И ПОДТВЕРЖДЕНИЕ ПОЧТЫ =====

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # аккаунт не активен до подтверждения почты
            user.save()

            confirmation_code = get_random_string(length=32)
            user.profile.confirmation_code = confirmation_code
            user.profile.save()

            confirm_link = request.build_absolute_uri(
                f'/users/confirm-email/?code={confirmation_code}&user={user.id}'
            )

            send_mail(
                'Подтверждение регистрации — Catalyst Cyber Lounge',
                f'Вы регистрируетесь на сайте Catalyst.\n\n'
                f'Подтвердите свою почту, перейдя по ссылке:\n{confirm_link}\n\n'
                f'Если это сделали не Вы — просто проигнорируйте это письмо.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            messages.success(request, 'Проверьте почту для подтверждения аккаунта.')
            return redirect('users:login')
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


def confirm_email(request):
    code = request.GET.get('code')
    user_id = request.GET.get('user')

    if not code or not user_id:
        messages.error(request, 'Неверная ссылка подтверждения.')
        return redirect('users:login')

    user = get_object_or_404(User, pk=user_id)

    if user.profile.confirmation_code == code:
        user.is_active = True
        user.save()
        user.profile.confirmation_code = ''
        user.profile.save()

        login(request, user)
        messages.success(request, 'Почта подтверждена! Добро пожаловать в Catalyst.')
        return redirect('places:list')
    else:
        messages.error(request, 'Ссылка подтверждения недействительна.')
        return redirect('users:login')


# ===== ПРОФИЛЬ =====

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


# ===== СБРОС ПАРОЛЯ =====

def password_reset_request(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()

        if not username or not email:
            return render(request, 'users/password_reset.html', {
                'error': 'Заполните все поля.',
                'username': username,
                'email': email,
            })

        try:
            user = User.objects.get(username=username, email=email)
        except User.DoesNotExist:
            return render(request, 'users/password_reset.html', {
                'error': 'Пользователь с таким логином и email не найден.',
                'username': username,
                'email': email,
            })

        reset_code = get_random_string(length=6, allowed_chars='0123456789')
        user.profile.reset_code = reset_code
        user.profile.save()

        context = {'reset_code': reset_code}
        text_content = render_to_string('users/email_password_reset.txt', context)
        html_content = render_to_string('users/email_password_reset.html', context)

        msg = EmailMultiAlternatives(
            subject='Сброс пароля — Catalyst Cyber Lounge',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        return redirect('users:password_reset_confirm')

    return render(request, 'users/password_reset.html')


def password_reset_confirm(request):
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not code or not new_password or not confirm_password:
            messages.error(request, 'Заполните все поля.')
            return render(request, 'users/password_reset_confirm.html')

        if new_password != confirm_password:
            messages.error(request, 'Пароли не совпадают.')
            return render(request, 'users/password_reset_confirm.html')

        if len(new_password) < 6:
            messages.error(request, 'Пароль должен содержать минимум 6 символов.')
            return render(request, 'users/password_reset_confirm.html')

        try:
            user = User.objects.get(profile__reset_code=code)
        except User.DoesNotExist:
            messages.error(request, 'Неверный код.')
            return render(request, 'users/password_reset_confirm.html')

        user.set_password(new_password)
        user.profile.reset_code = ''
        user.profile.save()
        user.save()

        messages.success(request, 'Пароль изменён. Войдите с новым паролем.')
        return redirect('users:login')

    return render(request, 'users/password_reset_confirm.html')

@login_required
@csrf_exempt
def send_confirm_code(request):
    if request.method == 'POST':
        code = get_random_string(length=6, allowed_chars='0123456789')
        request.user.profile.confirmation_code = code
        request.user.profile.save()

        send_mail(
            'Подтверждение почты — Catalyst Cyber Lounge',
            f'Ваш код подтверждения: {code}',
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            fail_silently=False,
        )
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'POST required'})

@login_required
@csrf_exempt
def confirm_email_code(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('code', '').strip()

        if code == request.user.profile.confirmation_code:
            request.user.profile.email_confirmed = True
            request.user.profile.confirmation_code = ''
            request.user.profile.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Неверный код'})
    return JsonResponse({'success': False, 'error': 'POST required'})

# ===== AI CHAT =====

@csrf_exempt
def ai_chat(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Только POST-запросы'}, status=405)

    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
    except json.JSONDecodeError:
        return JsonResponse({'reply': '🤖 Не могу разобрать твой запрос. Попробуй ещё раз.'})

    if not user_message:
        return JsonResponse({'reply': '🤖 Напиши что-нибудь, я слушаю.'})

    reply = ask_gigachat(user_message)
    return JsonResponse({'reply': reply})

