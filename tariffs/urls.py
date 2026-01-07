from django.urls import path
from . import views

app_name = 'tariffs'

urlpatterns = [
    path('', views.tariff_list, name='list'),
]
