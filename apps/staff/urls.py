from django.urls import path
from . import views

urlpatterns = [
    path('', views.staff_list, name='staff_list'),
    path('create/', views.staff_create, name='staff_create'),
    path('<int:pk>/', views.staff_detail, name='staff_detail'),
    path('<int:pk>/edit/', views.staff_edit, name='staff_edit'),
    path('<int:pk>/delete/', views.staff_delete, name='staff_delete'),
    
    # Departments
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:pk>/', views.department_detail, name='department_detail'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),
] 