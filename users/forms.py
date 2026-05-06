import re
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class UserRegisterForm(forms.ModelForm):
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Повтор пароля", widget=forms.PasswordInput)
    captcha_answer = forms.CharField(label="Код с картинки", max_length=10)

    ALLOWED_EMAIL_DOMAINS = [
        'yandex.ru', 'yandex.com', 'yandex.ua', 'yandex.by', 'yandex.kz',
        'ya.ru', 'gmail.com', 'mail.ru', 'inbox.ru', 'list.ru', 'bk.ru', 'rambler.ru',
    ]
    ALLOWED_TLDS = ['ru', 'com', 'ua', 'by', 'kz']

    class Meta:
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 3:
            raise ValidationError("Имя пользователя должно содержать минимум 3 символа.")
        if len(username) > 12:
            raise ValidationError("Имя пользователя не может быть длиннее 12 символов.")
        if not re.match(r'^[A-Za-z0-9_]+$', username):
            raise ValidationError("Разрешены только латинские буквы, цифры и знак подчёркивания.")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Пользователь с таким именем уже существует.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email').lower().strip()
        if len(email) < 5:
            raise ValidationError("Email слишком короткий (минимум 5 символов).")
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            raise ValidationError("Введите корректный email адрес.")
        
        local_part, domain = email.split('@', 1)
        if len(local_part) < 1 or len(local_part) > 64:
            raise ValidationError("Локальная часть email должна быть от 1 до 64 символов.")
        if '.' not in domain:
            raise ValidationError("Домен должен содержать точку (например, gmail.com).")
        
        tld = domain.split('.')[-1].lower()
        if tld not in self.ALLOWED_TLDS:
            raise ValidationError(f"Домен .{tld} не поддерживается.")
        if domain not in self.ALLOWED_EMAIL_DOMAINS:
            raise ValidationError(f"Почтовый сервис {domain} не поддерживается.")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Этот email уже используется.")
        return email

    def clean_password2(self):
        p1, p2 = self.cleaned_data.get('password1'), self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError("Пароли не совпадают.")
        return p2

    def clean_captcha_answer(self):
        answer = self.cleaned_data.get('captcha_answer', '').strip().lower()
        session_code = self.request.session.get('captcha_code', '') if self.request else ''
        if answer != session_code:
            raise ValidationError('Неверный код с картинки.')
        # очищаем код после успешной проверки
        if self.request:
            self.request.session['captcha_code'] = ''
        return answer

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = True
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
