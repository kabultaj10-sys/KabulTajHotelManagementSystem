from django.contrib import admin
from django.utils.html import format_html
from .models import Invoice, InvoiceItem, Payment, TaxRate, Discount


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'customer_name', 'invoice_type', 'total_amount', 'status', 'due_date', 'is_overdue')
    list_filter = ('invoice_type', 'status', 'invoice_date', 'created_at')
    search_fields = ('invoice_number', 'customer_name', 'customer_email')
    ordering = ('-invoice_date',)
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'invoice_type', 'invoice_date', 'due_date')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'customer_phone', 'customer_address')
        }),
        ('Financial Information', {
            'fields': ('subtotal', 'tax_amount', 'discount_amount', 'total_amount', 'paid_amount')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Created By', {
            'fields': ('created_by',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'description', 'quantity', 'unit_price', 'total_price')
    list_filter = ('created_at',)
    search_fields = ('invoice__invoice_number', 'description')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Item Information', {
            'fields': ('invoice', 'description', 'quantity', 'unit_price', 'total_price')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'amount', 'payment_method', 'payment_status', 'payment_date', 'transaction_id')
    list_filter = ('payment_method', 'payment_status', 'payment_date')
    search_fields = ('invoice__invoice_number', 'transaction_id', 'processed_by__username')
    ordering = ('-payment_date',)
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('invoice', 'amount', 'payment_method', 'payment_status', 'transaction_id')
        }),
        ('Processing', {
            'fields': ('payment_date', 'processed_by')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('payment_date',)


@admin.register(TaxRate)
class TaxRateAdmin(admin.ModelAdmin):
    list_display = ('name', 'rate', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    fieldsets = (
        ('Tax Rate Information', {
            'fields': ('name', 'rate', 'description', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at',)


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'discount_type', 'value', 'is_valid', 'used_count', 'is_active')
    list_filter = ('discount_type', 'is_active', 'valid_from', 'valid_until')
    search_fields = ('name', 'code', 'description')
    ordering = ('name',)
    
    fieldsets = (
        ('Discount Information', {
            'fields': ('name', 'code', 'discount_type', 'value', 'description')
        }),
        ('Usage Limits', {
            'fields': ('minimum_amount', 'maximum_discount', 'usage_limit', 'used_count')
        }),
        ('Validity Period', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at',)
