from django.urls import path
from . import views

app_name = 'tariffs'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.tariff_create, name='create'),
    path('edit/<int:pk>/', views.tariff_edit, name='edit'),
    path('delete/<int:pk>/', views.tariff_delete, name='delete'),
]