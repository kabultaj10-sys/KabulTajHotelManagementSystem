from django.urls import path
from . import views

urlpatterns = [
    path('', views.room_list, name='room_list'),
    path('create/', views.room_create, name='room_create'),
    path('availability/', views.room_availability, name='room_availability'),
    path('<int:pk>/', views.room_detail, name='room_detail'),
    path('<int:pk>/edit/', views.room_edit, name='room_edit'),
    path('<int:pk>/delete/', views.room_delete, name='room_delete'),
    path('<int:pk>/maintenance/', views.room_maintenance, name='room_maintenance'),
    path('<int:pk>/maintenance/<int:maintenance_id>/edit/', views.room_maintenance_edit, name='room_maintenance_edit'),
    path('<int:pk>/maintenance/<int:maintenance_id>/delete/', views.room_maintenance_delete, name='room_maintenance_delete'),
] 