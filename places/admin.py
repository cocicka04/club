from django.contrib import admin
from .models import Place

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('title', 'number', 'category', 'tariff', 'is_active')
    list_filter = ('category', 'tariff')
    search_fields = ('title', 'number')
