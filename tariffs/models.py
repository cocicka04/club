from django.db import models

class Category(models.Model):
    name = models.CharField("Название категории", max_length=100)
    description = models.TextField("Описание категории", blank=True)

    class Meta:
        verbose_name = "Категория ПК"
        verbose_name_plural = "Категории ПК"

    def __str__(self):
        return self.name

class Tariff(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="tariffs", verbose_name="Категория ПК")
    name = models.CharField("Название тарифа", max_length=100)
    price_per_hour = models.DecimalField("Цена за час (₽)", max_digits=8, decimal_places=2, default=0)
    description = models.TextField("Описание тарифа", blank=True)

    class Meta:
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"

    def __str__(self):
        return f"{self.name} — {self.price_per_hour}₴/час"
