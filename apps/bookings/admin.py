from django.contrib import admin
from .models import Booking, CheckIn, CheckOut, BookingPayment


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_number', 'guest', 'room', 'check_in_date', 'check_out_date', 'status', 'total_amount']
    list_filter = ['status', 'payment_status', 'source', 'check_in_date', 'check_out_date']
    search_fields = ['booking_number', 'guest__first_name', 'guest__last_name', 'guest__email']
    readonly_fields = ['booking_number', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_number', 'guest', 'room', 'check_in_date', 'check_out_date', 'number_of_guests')
        }),
        ('Pricing', {
            'fields': ('room_rate', 'total_amount', 'deposit_amount', 'balance_amount')
        }),
        ('Status', {
            'fields': ('status', 'payment_status', 'source')
        }),
        ('Special Requests', {
            'fields': ('special_requests', 'dietary_restrictions', 'room_preferences')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'confirmed_at', 'cancelled_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ['booking', 'check_in_datetime', 'checked_in_by', 'id_verified', 'payment_verified', 'room_key_issued']
    list_filter = ['check_in_datetime', 'id_verified', 'payment_verified', 'room_key_issued']
    search_fields = ['booking__guest__first_name', 'booking__guest__last_name', 'booking__room__room_number']
    readonly_fields = ['check_in_datetime', 'checked_in_by']
    ordering = ['-check_in_datetime']
    
    fieldsets = (
        ('Check-in Information', {
            'fields': ('booking', 'check_in_datetime', 'checked_in_by')
        }),
        ('Verification', {
            'fields': ('id_verified', 'payment_verified', 'room_inspected')
        }),
        ('Room Assignment', {
            'fields': ('actual_room', 'room_key_issued')
        }),
        ('Additional Information', {
            'fields': ('special_instructions', 'notes')
        }),
    )


@admin.register(CheckOut)
class CheckOutAdmin(admin.ModelAdmin):
    list_display = ['booking', 'check_out_datetime', 'checked_out_by', 'room_inspected', 'keys_returned', 'payment_completed']
    list_filter = ['check_out_datetime', 'room_inspected', 'keys_returned', 'payment_completed', 'late_checkout']
    search_fields = ['booking__guest__first_name', 'booking__guest__last_name', 'booking__room__room_number']
    readonly_fields = ['check_out_datetime', 'checked_out_by']
    ordering = ['-check_out_datetime']
    
    fieldsets = (
        ('Check-out Information', {
            'fields': ('booking', 'check_out_datetime', 'checked_out_by')
        }),
        ('Process', {
            'fields': ('room_inspected', 'keys_returned', 'payment_completed')
        }),
        ('Additional Charges', {
            'fields': ('additional_charges', 'late_checkout', 'late_checkout_hours')
        }),
        ('Guest Feedback', {
            'fields': ('guest_satisfaction', 'feedback')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


@admin.register(BookingPayment)
class BookingPaymentAdmin(admin.ModelAdmin):
    list_display = ['booking', 'amount', 'payment_method', 'payment_date', 'status', 'processed_by']
    list_filter = ['payment_method', 'status', 'payment_date']
    search_fields = ['booking__booking_number', 'booking__guest__first_name', 'booking__guest__last_name', 'reference_number']
    readonly_fields = ['payment_date', 'processed_by']
    ordering = ['-payment_date']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('booking', 'amount', 'payment_method', 'reference_number')
        }),
        ('Status', {
            'fields': ('status', 'payment_date', 'processed_by')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
