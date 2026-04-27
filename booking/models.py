from django.conf import settings
from django.db import models
from django.utils import timezone
import random

def generate_code():
    return str(random.randint(1000, 9999))

class Booking(models.Model):

    STATUS_ACTIVE = 'active'
    STATUS_FINISHED = 'finished'
    STATUS_CANCELED = 'canceled'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Активно'),
        (STATUS_FINISHED, 'Завершено'),
        (STATUS_CANCELED, 'Отменено'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )

    place = models.ForeignKey(
        'places.Place',
        on_delete=models.CASCADE,
        verbose_name='Место'
    )

    start_time = models.DateTimeField(verbose_name='Начало бронирования')
    end_time = models.DateTimeField(verbose_name='Окончание бронирования')

    total_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='Итоговая стоимость'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        verbose_name='Статус'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['-start_time']

    def __str__(self):
        return f'{self.place} — {self.user} ({self.get_status_display()})'

    def is_expired(self):
        return timezone.now() >= self.end_time
    code = models.CharField(max_length=4, blank=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_code()
        super().save(*args, **kwargs)
