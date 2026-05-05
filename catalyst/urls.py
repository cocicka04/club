from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from booking.views import admin_booking_edit, admin_booking_delete

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('users/', include(('users.urls', 'users'))),
    path('places/', include(('places.urls', 'places'))),
    path('booking/', include(('booking.urls', 'booking'))),
    path('tariffs/', include(('tariffs.urls', 'tariffs'))),
    path('news/', views.news_page, name='news'),
    path('news/delete/<int:pk>/', views.news_delete, name='news_delete'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('api/ai-chat/', views.ai_chat, name='ai_chat'),
    path('users/confirm-email/', views.confirm_email, name='confirm_email'),
    path('users/password-reset/', views.password_reset_request, name='password_reset'),
    path('users/password-reset/confirm/', views.password_reset_confirm, name='password_reset_confirm'),
    path('users/send-confirm-code/', views.send_confirm_code, name='send_confirm_code'),
    path('users/confirm-email-code/', views.confirm_email_code, name='confirm_email_code'),
    path('dashboard/booking/edit/<int:pk>/', admin_booking_edit, name='admin_booking_edit'),
    path('dashboard/booking/delete/<int:pk>/', admin_booking_delete, name='admin_booking_delete'),
    path('dashboard/user/create/', views.admin_user_create, name='admin_user_create'),
    path('dashboard/user/edit/<int:pk>/', views.admin_user_edit, name='admin_user_edit'),
    path('dashboard/user/delete/<int:pk>/', views.admin_user_delete, name='admin_user_delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)