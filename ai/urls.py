from django.urls import path
from . import views

urlpatterns = [
    path('barista/', views.ai_barista, name='barista'),
    path('admin/', views.ai_admin_assistant, name='admin'),
]