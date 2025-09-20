from django.contrib import admin
from django.utils.html import format_html
from .models import MenuCategory, MenuItem, Table, TableReservation, Order, OrderItem, RestaurantInvoice, RestaurantInvoiceItem, Transaction


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['display_order', 'name']
    list_editable = ['display_order', 'is_active']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'cuisine_type', 'is_available', 'preparation_time']
    list_filter = ['category', 'cuisine_type', 'is_available', 'is_vegetarian', 'is_gluten_free', 'is_spicy', 'created_at']
    search_fields = ['name', 'description', 'category__name']
    ordering = ['category', 'name']
    list_editable = ['price', 'is_available', 'preparation_time']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'description', 'price')
        }),
        ('Cuisine Details', {
            'fields': ('cuisine_type', 'preparation_time')
        }),
        ('Dietary Options', {
            'fields': ('is_vegetarian', 'is_gluten_free', 'is_spicy')
        }),
        ('Availability', {
            'fields': ('is_available', 'image')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['table_number', 'capacity', 'location', 'status', 'is_active']
    list_filter = ['status', 'is_active', 'created_at']
    search_fields = ['table_number', 'location']
    ordering = ['table_number']
    list_editable = ['status', 'is_active']


@admin.register(TableReservation)
class TableReservationAdmin(admin.ModelAdmin):
    list_display = ['guest_name', 'table', 'reservation_date', 'reservation_time', 'party_size', 'status']
    list_filter = ['status', 'reservation_date', 'table', 'created_at']
    search_fields = ['guest_name', 'guest_email', 'guest_phone', 'table__table_number']
    ordering = ['-reservation_date', '-reservation_time']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'guest_name', 'table', 'total_amount', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at', 'table']
    search_fields = ['order_number', 'guest_name', 'guest_phone', 'table__table_number']
    ordering = ['-created_at']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'table', 'guest', 'room')
        }),
        ('Customer Details', {
            'fields': ('guest_name', 'guest_phone', 'special_instructions')
        }),
        ('Order Status', {
            'fields': ('status', 'payment_status', 'total_amount')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'menu_item', 'quantity', 'unit_price', 'total_price']
    list_filter = ['menu_item__category', 'created_at']
    search_fields = ['order__order_number', 'menu_item__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


@admin.register(RestaurantInvoice)
class RestaurantInvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'customer_name', 'order', 'total_amount', 'status', 'invoice_date', 'due_date']
    list_filter = ['status', 'payment_method', 'invoice_date', 'due_date', 'created_at']
    search_fields = ['invoice_number', 'customer_name', 'customer_email', 'order__order_number']
    ordering = ['-invoice_date', '-created_at']
    readonly_fields = ['invoice_number', 'tax_amount', 'total_amount', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'order', 'status')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'customer_email', 'customer_phone', 'customer_address')
        }),
        ('Financial Details', {
            'fields': ('subtotal', 'tax_rate', 'tax_amount', 'discount_amount', 'total_amount')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_reference', 'payment_due_date')
        }),
        ('Dates', {
            'fields': ('invoice_date', 'due_date')
        }),
        ('Additional Information', {
            'fields': ('notes', 'terms_conditions')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RestaurantInvoiceItem)
class RestaurantInvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'menu_item', 'quantity', 'unit_price', 'total_price']
    list_filter = ['menu_item__category', 'created_at']
    search_fields = ['invoice__invoice_number', 'menu_item__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'customer_name', 'table_number', 'amount', 'payment_method', 'transaction_type', 'created_at']
    list_filter = ['transaction_type', 'payment_method', 'created_at']
    search_fields = ['transaction_id', 'customer_name', 'table_number']
    ordering = ['-created_at']
    readonly_fields = ['transaction_id', 'created_at']
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('transaction_id', 'transaction_type', 'order', 'invoice')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'table_number')
        }),
        ('Financial Details', {
            'fields': ('amount', 'payment_method')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
