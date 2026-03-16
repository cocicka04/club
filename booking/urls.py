from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('create/', views.create_booking, name='create'),
    path('create/<int:place_id>/', views.create_booking, name='create_with_place'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel'),
    path('extend/<int:booking_id>/', views.extend_booking, name='extend'),
]
