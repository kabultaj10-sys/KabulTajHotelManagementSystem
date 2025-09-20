from django.urls import path
from . import views

app_name = 'conference'

urlpatterns = [
    path('', views.conference_list, name='conference_list'),
    path('rooms/', views.room_list, name='conference_room_list'),
    path('rooms/create/', views.room_create, name='room_create'),
    path('rooms/<int:pk>/', views.room_detail, name='room_detail'),
    path('rooms/<int:pk>/edit/', views.room_edit, name='room_edit'),
    path('rooms/<int:pk>/delete/', views.room_delete, name='room_delete'),
    path('bookings/', views.booking_list, name='conference_booking_list'),
    path('bookings/create/', views.booking_create, name='booking_create'),
    path('bookings/<int:pk>/', views.booking_detail, name='booking_detail'),
    path('bookings/<int:pk>/edit/', views.booking_edit, name='booking_edit'),
    path('bookings/<int:pk>/delete/', views.booking_delete, name='booking_delete'),
    path('bookings/<int:pk>/mark-completed/', views.booking_mark_completed, name='booking_mark_completed'),
] 