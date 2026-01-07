from django.db import models
from tariffs.models import Tariff, Category

class Place(models.Model):
    title = models.CharField(max_length=255)
    number = models.PositiveIntegerField("Номер места")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='places/', blank=True, null=True)
    description = models.TextField(blank=True, verbose_name='Описание места')
    cpu = models.CharField(max_length=255, default='')
    gpu = models.CharField(max_length=255, default='')
    ram = models.CharField(max_length=255, default='')
    monitor = models.CharField(max_length=255, default='')
    keyboard = models.CharField(max_length=255, default='')
    mouse = models.CharField(max_length=255, default='')
    headset = models.CharField(max_length=255, default='')

    class Meta:
        verbose_name = "Место"
        verbose_name_plural = "Места"
        ordering = ["number"]

    def __str__(self):
        return f"{self.title} (№{self.number})"