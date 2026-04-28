from django.urls import path
from . import views

app_name = 'places'

urlpatterns = [
    path('', views.place_list, name='list'),
    path('<int:pk>/', views.place_detail, name='detail'),

    path('create/', views.place_create, name='create'),
    path('<int:pk>/edit/', views.place_edit, name='edit'),
    path('<int:pk>/delete/', views.place_delete, name='delete'),
    path('ajax/', views.place_search_ajax, name='place_search_ajax'),
]
