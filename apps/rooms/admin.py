from django.contrib import admin
from .models import Room, RoomType, RoomMaintenance, RoomAmenity


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_price', 'capacity', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'base_price', 'capacity')
        }),
        ('Amenities', {
            'fields': ('amenities',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'room_type', 'floor', 'status', 'effective_price', 'is_active']
    list_filter = ['status', 'floor', 'room_type', 'is_active']
    search_fields = ['room_number', 'room_type__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['room_number']
    
    fieldsets = (
        ('Room Information', {
            'fields': ('room_number', 'room_type', 'floor')
        }),
        ('Status & Pricing', {
            'fields': ('status', 'current_price')
        }),
        ('Additional Information', {
            'fields': ('notes', 'is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(RoomMaintenance)
class RoomMaintenanceAdmin(admin.ModelAdmin):
    list_display = ['room', 'maintenance_type', 'scheduled_date', 'status', 'cost']
    list_filter = ['maintenance_type', 'status', 'scheduled_date', 'completed_date']
    search_fields = ['room__room_number', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-scheduled_date']
    
    fieldsets = (
        ('Maintenance Information', {
            'fields': ('room', 'maintenance_type', 'description', 'scheduled_date')
        }),
        ('Completion', {
            'fields': ('completed_date', 'cost', 'status')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(RoomAmenity)
class RoomAmenityAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'icon', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    ordering = ['name']
    
    fieldsets = (
        ('Amenity Information', {
            'fields': ('name', 'description', 'icon')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at')
        }),
    )
