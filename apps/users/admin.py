from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'hire_date')
    list_filter = ('role', 'is_active', 'hire_date', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'address', 'date_of_birth')}),
        ('Role & Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'hire_date')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'first_name', 'last_name'),
        }),
    )
    
    readonly_fields = ('hire_date', 'date_joined', 'last_login')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()
    
    def colored_role(self, obj):
        colors = {
            'admin': 'red',
            'manager': 'orange',
            'receptionist': 'blue',
            'housekeeping': 'green',
            'restaurant': 'purple',
            'conference': 'brown',
        }
        color = colors.get(obj.role, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.get_role_display()
        )
    colored_role.short_description = 'Role'
