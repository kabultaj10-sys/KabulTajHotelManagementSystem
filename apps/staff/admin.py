from django.contrib import admin
from django.utils.html import format_html
from .models import Department, StaffProfile, WorkSchedule


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description', 'manager__first_name', 'manager__last_name')
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Management', {
            'fields': ('manager',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'department', 'position', 'hire_date', 'is_active')
    list_filter = ('department', 'is_active', 'hire_date')
    search_fields = ('user__first_name', 'user__last_name', 'employee_id', 'position')
    ordering = ('user__first_name', 'user__last_name')
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'employee_id', 'position', 'hire_date')
        }),
        ('Department & Salary', {
            'fields': ('department', 'salary')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact', 'emergency_phone'),
            'classes': ('collapse',)
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


@admin.register(WorkSchedule)
class WorkScheduleAdmin(admin.ModelAdmin):
    list_display = ('staff', 'day_of_week', 'start_time', 'end_time', 'is_active')
    list_filter = ('day_of_week', 'is_active', 'staff__department')
    search_fields = ('staff__user__first_name', 'staff__user__last_name')
    ordering = ('staff', 'day_of_week')
    
    fieldsets = (
        ('Schedule Information', {
            'fields': ('staff', 'day_of_week', 'start_time', 'end_time')
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
