from django.db import models
from django.contrib.auth.models import User
from places.models import Place

class Booking(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активно'),
        ('completed', 'Завершено'),
        ('cancelled', 'Отменено'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь", related_name="bookings")
    place = models.ForeignKey(Place, on_delete=models.CASCADE, verbose_name="Место")
    start_time = models.DateTimeField("Время начала")
    end_time = models.DateTimeField("Время окончания")
    hours = models.PositiveIntegerField("Часы", default=1)
    total_price = models.DecimalField("Итоговая стоимость", max_digits=10, decimal_places=2)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"

    def __str__(self):
        return f"{self.place} — {self.user.username} ({self.start_time} — {self.end_time})"
