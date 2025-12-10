from django.contrib import admin
from .models import Tariff, Category
from django import forms

class TariffAdminForm(forms.ModelForm):
    class Meta:
        model = Tariff
        fields = '__all__'

    class Media:
        js = ('admin/js/filter_tariffs.js',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    form = TariffAdminForm
    list_display = ('name', 'category', 'price_per_hour')
