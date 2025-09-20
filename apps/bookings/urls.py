from django.urls import path
from . import views

urlpatterns = [
    path('', views.booking_list, name='booking_list'),
    path('create/', views.booking_create, name='booking_create'),
    path('availability/', views.availability_check, name='availability_check'),
    path('<int:pk>/', views.booking_detail, name='booking_detail'),
    path('<int:pk>/edit/', views.booking_edit, name='booking_edit'),
    path('<int:pk>/delete/', views.booking_delete, name='booking_delete'),
    path('<int:pk>/check-in/', views.check_in_create, name='check_in_create'),
    path('<int:pk>/check-out/', views.check_out_create, name='check_out_create'),
    path('<int:pk>/payment/', views.booking_payment_create, name='booking_payment_create'),
] 

