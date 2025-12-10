# places/urls.py
from django.urls import path
from . import views

app_name = 'places'

urlpatterns = [
    path('', views.place_list, name='list'),
    path('<int:pk>/', views.place_detail, name='detail'),
]
