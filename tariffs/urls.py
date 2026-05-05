from django.urls import path
from . import views

app_name = 'tariffs'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.tariff_create, name='create'),
    path('edit/<int:pk>/', views.tariff_edit, name='edit'),
    path('delete/<int:pk>/', views.tariff_delete, name='delete'),

    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/edit/<int:pk>/', views.category_edit, name='category_edit'),
    path('categories/delete/<int:pk>/', views.category_delete, name='category_delete'),
]