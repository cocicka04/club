from django.urls import path
from . import views

app_name = 'tariffs'

urlpatterns = [
    path('', views.tariff_list, name='list'),

    path('create/', views.tariff_create, name='create'),
    path('edit/<int:pk>/', views.tariff_edit, name='edit'),
    path('delete/<int:pk>/', views.tariff_delete, name='delete'),
]
