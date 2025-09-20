from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden


def admin_required(view_func):
    """Decorator to require admin role only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_admin:
            messages.error(request, 'You do not have permission to access this page. Admin access required.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def receptionist_required(view_func):
    """Decorator to require receptionist or admin role"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not (request.user.is_admin or request.user.is_receptionist):
            messages.error(request, 'You do not have permission to access this page. Receptionist or Admin access required.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def restaurant_required(view_func):
    """Decorator to require restaurant or admin role"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not (request.user.is_admin or request.user.is_restaurant):
            messages.error(request, 'You do not have permission to access this page. Restaurant Manager or Admin access required.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def role_required(*allowed_roles):
    """Decorator to require specific roles"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role not in allowed_roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def user_management_required(view_func):
    """Decorator to require admin role for user management (only admins can create users)"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_admin:
            messages.error(request, 'You do not have permission to manage users. Only administrators can create and manage user accounts.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
