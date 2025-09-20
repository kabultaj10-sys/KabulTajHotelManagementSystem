from django.urls import path
from . import views

urlpatterns = [
    path('', views.billing_dashboard, name='billing_dashboard'),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:pk>/edit/', views.invoice_edit, name='invoice_edit'),
    path('invoices/<int:pk>/print/', views.invoice_print, name='invoice_print'),
    path('invoices/<int:pk>/delete/', views.invoice_delete, name='invoice_delete'),
    path('invoices/<int:pk>/payment/', views.payment_complete, name='payment_complete'),
    path('payments/', views.payment_list, name='payment_list'),
] 