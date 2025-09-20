from django.contrib import admin
from .models import Guest, GuestPreference, GuestDocument


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'vip_status', 'nationality', 'created_at']
    list_filter = ['vip_status', 'gender', 'is_active', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'passport_number']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Personal Details', {
            'fields': ('date_of_birth', 'gender', 'nationality', 'passport_number', 'id_type', 'id_number')
        }),
        ('Address', {
            'fields': ('address', 'city', 'country', 'postal_code')
        }),
        ('VIP & Preferences', {
            'fields': ('vip_status', 'special_requests', 'dietary_restrictions', 'room_preferences')
        }),
        ('Business Information', {
            'fields': ('company', 'job_title', 'business_phone')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(GuestPreference)
class GuestPreferenceAdmin(admin.ModelAdmin):
    list_display = ['guest', 'preferred_floor', 'preferred_room_type', 'smoking_preference', 'housekeeping_frequency']
    list_filter = ['smoking_preference', 'housekeeping_frequency', 'communication_method']
    search_fields = ['guest__first_name', 'guest__last_name', 'guest__email']
    ordering = ['guest__first_name']
    
    fieldsets = (
        ('Guest', {
            'fields': ('guest',)
        }),
        ('Room Preferences', {
            'fields': ('preferred_floor', 'preferred_room_type', 'smoking_preference', 'accessibility_requirements')
        }),
        ('Service Preferences', {
            'fields': ('housekeeping_frequency', 'preferred_language', 'communication_method')
        }),
        ('Additional Notes', {
            'fields': ('special_notes',)
        }),
    )


@admin.register(GuestDocument)
class GuestDocumentAdmin(admin.ModelAdmin):
    list_display = ['guest', 'document_type', 'document_number', 'issuing_country', 'is_verified', 'is_expired']
    list_filter = ['document_type', 'is_verified', 'issue_date', 'expiry_date']
    search_fields = ['guest__first_name', 'guest__last_name', 'document_number']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Document Information', {
            'fields': ('guest', 'document_type', 'document_number', 'issuing_country')
        }),
        ('Dates', {
            'fields': ('issue_date', 'expiry_date')
        }),
        ('Verification', {
            'fields': ('is_verified', 'document_file')
        }),
        ('Notes', {
            'fields': ('notes', 'created_at')
        }),
    )
    
    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = 'Expired'
