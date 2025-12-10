from django.db import models
from tariffs.models import Category, Tariff

class Place(models.Model):
    number = models.CharField("Номер места", max_length=20)
    title = models.CharField("Название места/зоны", max_length=200)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name="Категория ПК")
    tariff = models.ForeignKey(Tariff, on_delete=models.PROTECT, verbose_name="Тариф по умолчанию")
    description = models.TextField("Описание места/зоны", blank=True)
    specs = models.TextField("Характеристики ПК", blank=True)
    is_active = models.BooleanField("Доступно для бронирования", default=True)
    image = models.ImageField("Фото места", upload_to="places/", blank=True, null=True)

    class Meta:
        verbose_name = "Место/Зона"
        verbose_name_plural = "Места/Зоны"

    def __str__(self):
        return f"{self.title} ({self.number})"
