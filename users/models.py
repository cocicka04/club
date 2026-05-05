from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class Profile(models.Model):
    ROLE_CHOICES = (
        ('user', 'Пользователь'),
        ('cashier', 'Сотрудник'),
        ('admin', 'Администратор'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    confirmation_code = models.CharField(max_length=32, blank=True, default='')
    reset_code = models.CharField(max_length=6, blank=True, default='')
    email_confirmed = models.BooleanField(default=False)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_cashier(self):
        return self.role in ['cashier', 'admin'] or self.user.is_superuser

    @property
    def is_admin(self):
        return self.role == 'admin' or self.user.is_superuser


class News(models.Model):
    title = models.CharField(max_length=120)
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ['-created_at']

    def __str__(self):
        return self.title