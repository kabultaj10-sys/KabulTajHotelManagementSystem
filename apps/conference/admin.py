from django.contrib import admin
from django.utils.html import format_html
from .models import ConferenceRoom, ConferenceEquipment, ConferenceBooking, ConferenceEvent, ConferencePayment


@admin.register(ConferenceRoom)
class ConferenceRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'floor', 'status', 'hourly_rate', 'daily_rate', 'is_active')
    list_filter = ('status', 'floor', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    fieldsets = (
        ('Room Information', {
            'fields': ('name', 'capacity', 'floor', 'status')
        }),
        ('Pricing', {
            'fields': ('hourly_rate', 'daily_rate')
        }),
        ('Details', {
            'fields': ('description', 'amenities')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ConferenceEquipment)
class ConferenceEquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'equipment_type', 'is_available', 'maintenance_date', 'created_at')
    list_filter = ('equipment_type', 'is_available', 'maintenance_date', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('equipment_type', 'name')
    
    fieldsets = (
        ('Equipment Information', {
            'fields': ('name', 'equipment_type', 'description')
        }),
        ('Status & Maintenance', {
            'fields': ('is_available', 'maintenance_date')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at',)


@admin.register(ConferenceBooking)
class ConferenceBookingAdmin(admin.ModelAdmin):
    list_display = ('booking_number', 'room', 'client_name', 'event_title', 'start_datetime', 'status', 'payment_status', 'total_amount')
    list_filter = ('status', 'payment_status', 'start_datetime', 'created_at')
    search_fields = ('booking_number', 'client_name', 'client_email', 'event_title', 'room__name')
    ordering = ('-start_datetime',)
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_number', 'room', 'client_name', 'client_email', 'client_phone')
        }),
        ('Event Details', {
            'fields': ('event_title', 'event_description', 'start_datetime', 'end_datetime', 'attendees_count')
        }),
        ('Financial Information', {
            'fields': ('total_amount', 'paid_amount', 'payment_status')
        }),
        ('Status & Requirements', {
            'fields': ('status', 'special_requirements')
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


@admin.register(ConferenceEvent)
class ConferenceEventAdmin(admin.ModelAdmin):
    list_display = ('booking', 'event_type', 'organizer_name', 'catering_required', 'technical_support_required')
    list_filter = ('event_type', 'catering_required', 'technical_support_required', 'created_at')
    search_fields = ('booking__event_title', 'organizer_name', 'organizer_phone')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Event Information', {
            'fields': ('booking', 'event_type', 'organizer_name', 'organizer_phone')
        }),
        ('Event Details', {
            'fields': ('agenda', 'setup_time_required', 'cleanup_time_required')
        }),
        ('Services Required', {
            'fields': ('catering_required', 'catering_details', 'technical_support_required', 'technical_requirements')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at',)


@admin.register(ConferencePayment)
class ConferencePaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'payment_method', 'payment_date', 'transaction_id', 'processed_by')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('booking__booking_number', 'transaction_id', 'processed_by__username')
    ordering = ('-payment_date',)
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('booking', 'amount', 'payment_method', 'transaction_id')
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
