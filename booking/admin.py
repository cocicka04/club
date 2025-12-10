from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('place','user','start_time','end_time','status')
    list_filter = ('status',)
    search_fields = ('user__username','place__title')
