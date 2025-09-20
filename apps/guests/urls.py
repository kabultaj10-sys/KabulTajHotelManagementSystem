from django.urls import path
from . import views

urlpatterns = [
    path('', views.guest_list, name='guest_list'),
    path('create/', views.guest_create, name='guest_create'),
    path('search/', views.guest_search, name='guest_search'),
    path('history/', views.guest_history, name='guest_history'),
    path('history/export/', views.guest_history_export, name='guest_history_export'),
    path('<int:pk>/', views.guest_detail, name='guest_detail'),
    path('<int:pk>/export/', views.guest_export, name='guest_export'),
    path('<int:pk>/edit/', views.guest_edit, name='guest_edit'),
    path('<int:pk>/delete/', views.guest_delete, name='guest_delete'),
    path('<int:pk>/preferences/', views.guest_preferences, name='guest_preferences'),
    path('<int:pk>/documents/', views.guest_documents, name='guest_documents'),
] 