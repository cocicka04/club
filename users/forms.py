from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class UserRegisterForm(forms.ModelForm):
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Повтор пароля", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Этот email уже используется.")
        return email

    def clean_password2(self):
        p1, p2 = self.cleaned_data.get('password1'), self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError("Пароли не совпадают.")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False  # активируется только после подтверждения
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
