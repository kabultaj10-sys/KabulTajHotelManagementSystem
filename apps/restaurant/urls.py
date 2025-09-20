from django.urls import path
from . import views

app_name = 'restaurant'

urlpatterns = [
    # Dashboard
    path('', views.restaurant_dashboard, name='dashboard'),
    
    # Menu Items CRUD
    path('menu/', views.menu_list, name='menu_list'),
    path('menu/create/', views.menu_create, name='menu_create'),
    path('menu/<int:pk>/edit/', views.menu_edit, name='menu_edit'),
    path('menu/<int:pk>/delete/', views.menu_delete, name='menu_delete'),
    
    # Table Management
    path('tables/', views.table_list, name='table_list'),
    path('tables/create/', views.table_create, name='table_create'),
    path('tables/<int:pk>/edit/', views.table_edit, name='table_edit'),
    path('tables/<int:pk>/update-status/', views.table_update_status, name='table_update_status'),
    
    # Order Management
    path('orders/', views.order_list, name='order_list'),
    path('orders/create/', views.order_create, name='order_create'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/edit/', views.order_edit, name='order_edit'),
    path('orders/<int:pk>/update-status/', views.order_update_status, name='order_update_status'),
    path('orders/<int:pk>/delete/', views.order_delete, name='order_delete'),
    path('orders/bulk-delete/', views.order_bulk_delete, name='order_bulk_delete'),
    path('orders/<int:order_id>/invoice/create/', views.restaurant_invoice_create_from_order, name='invoice_create_from_order'),
    path('orders/<int:order_id>/invoice/pay/', views.restaurant_invoice_start_payment, name='invoice_start_payment'),
    
    # Restaurant Billing & Invoices
    path('billing/', views.restaurant_billing_dashboard, name='billing_dashboard'),
    path('billing/invoices/', views.restaurant_invoice_list, name='invoice_list'),
    path('billing/invoices/create/', views.restaurant_invoice_create, name='invoice_create'),
    path('billing/invoices/<int:pk>/', views.restaurant_invoice_detail, name='invoice_detail'),
    path('billing/invoices/<int:pk>/edit/', views.restaurant_invoice_edit, name='invoice_edit'),
    path('billing/invoices/<int:pk>/delete/', views.restaurant_invoice_delete, name='invoice_delete'),
    path('billing/invoices/<int:pk>/print/', views.restaurant_invoice_print, name='invoice_print'),
    path('billing/invoices/<int:pk>/receipt/', views.restaurant_invoice_receipt_print, name='invoice_receipt_print'),
    path('billing/invoices/<int:pk>/receipt-pdf/', views.restaurant_invoice_receipt_pdf, name='invoice_receipt_pdf'),
    path('billing/invoices/<int:pk>/update-status/', views.restaurant_invoice_update_status, name='invoice_update_status'),
    path('billing/invoices/<int:pk>/process-payment/', views.restaurant_invoice_process_payment, name='invoice_process_payment'),
    
    # AJAX endpoints
    path('api/menu-items/', views.get_menu_items, name='get_menu_items'),
    path('api/order-details/<int:order_id>/', views.get_order_details_for_invoice, name='get_order_details_for_invoice'),
] 