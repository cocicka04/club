from django.contrib import admin
from .models import Profile, News

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'email_confirmed')
    list_filter = ('role', 'email_confirmed')
    search_fields = ('user__username', 'user__email')

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    ordering = ('-created_at',)