from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import User as CustomUser
from .forms import UserForm, SignUpForm, UserSettingsForm
from .decorators import admin_required, receptionist_required, restaurant_required, user_management_required
from apps.guests.models import Guest
from apps.rooms.models import Room
from apps.bookings.models import Booking
from apps.restaurant.models import Order
from apps.conference.models import ConferenceBooking
from apps.billing.models import Invoice
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta


class CustomLoginView(LoginView):
    """Custom login view that redirects users based on their role"""
    template_name = 'users/login.html'
    
    def get_success_url(self):
        """Redirect users to appropriate dashboard based on their role"""
        user = self.request.user
        
        # If user is a superuser, they can access admin or main dashboard
        if user.is_superuser:
            # Check if they want to go to admin (from next parameter)
            next_url = self.request.GET.get('next', '')
            if 'admin' in next_url:
                return '/admin/'
            return '/'
        
        # For regular users, always go to main dashboard
        return '/'
    
    def form_valid(self, form):
        """Handle successful login"""
        user = form.get_user()
        login(self.request, user)
        
        # Add success message
        messages.success(self.request, f'Welcome back, {user.get_full_name() or user.username}!')
        
        return HttpResponseRedirect(self.get_success_url())


@login_required
def dashboard(request):
    """Main dashboard view with role-based content"""
    # Get current date
    today = timezone.now().date()
    
    # Base context
    context = {
        'user_role': request.user.role,
        'is_admin': request.user.is_admin,
        'is_receptionist': request.user.is_receptionist,
        'is_restaurant': request.user.is_restaurant,
    }
    
    # Admin and Receptionist can see hotel-wide statistics
    if request.user.is_admin or request.user.is_receptionist:
        context.update({
            'total_guests': Guest.objects.filter(is_active=True).count(),
            'total_rooms': Room.objects.filter(is_active=True).count(),
            'available_rooms': Room.objects.filter(status='available', is_active=True).count(),
            'total_bookings': Booking.objects.count(),
            'today_bookings': Booking.objects.filter(check_in_date=today).count(),
            'pending_bookings': Booking.objects.filter(status='pending').count(),
            'total_invoices': Invoice.objects.count(),
            'pending_invoices': Invoice.objects.filter(status='sent').count(),
            'total_revenue': Invoice.objects.filter(status='paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        })
        
        # Recent activities for admin and receptionist
        context['recent_bookings'] = Booking.objects.select_related('guest', 'room').order_by('-created_at')[:5]
        context['recent_guests'] = Guest.objects.filter(is_active=True).order_by('-created_at')[:5]
    
    # Restaurant manager can see restaurant statistics
    if request.user.is_restaurant or request.user.is_admin:
        context.update({
            'total_orders': Order.objects.count(),
            'today_orders': Order.objects.filter(created_at__date=today).count(),
        })
        context['recent_orders'] = Order.objects.select_related('table').order_by('-created_at')[:5]
    
    # Admin can see conference statistics
    if request.user.is_admin:
        context.update({
            'total_conferences': ConferenceBooking.objects.count(),
            'today_conferences': ConferenceBooking.objects.filter(start_datetime__date=today).count(),
        })
    
    return render(request, 'users/dashboard.html', context)


@user_management_required
def user_list(request):
    """List all users - Admin only"""
    users = CustomUser.objects.all().order_by('-date_joined')
    return render(request, 'users/user_list.html', {'users': users})


@user_management_required
def user_create(request):
    """Create a new user - Admin only"""
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.username} created successfully.')
            return redirect('user_list')
    else:
        form = UserForm()
    
    return render(request, 'users/user_form.html', {'form': form, 'title': 'Create User'})


@user_management_required
def user_detail(request, pk):
    """View user details - Admin only"""
    user = get_object_or_404(CustomUser, pk=pk)
    return render(request, 'users/user_detail.html', {'user': user})


@user_management_required
def user_edit(request, pk):
    """Edit user - Admin only"""
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user.username} updated successfully.')
            return redirect('user_list')
    else:
        form = UserForm(instance=user)
    
    return render(request, 'users/user_form.html', {'form': form, 'title': 'Edit User'})


@user_management_required
def user_delete(request, pk):
    """Delete user - Admin only"""
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} deleted successfully.')
        return redirect('user_list')
    
    return render(request, 'users/user_confirm_delete.html', {'user': user})


@login_required
def settings_view(request):
    """User settings/profile page"""
    if request.method == 'POST':
        form = UserSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('settings')
    else:
        form = UserSettingsForm(instance=request.user)
    return render(request, 'users/settings.html', {'form': form})


@user_management_required
def signup(request):
    """Sign up a new user (admin-only)"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.username} created successfully.')
            return redirect('signup')
    else:
        form = SignUpForm()
    return render(request, 'users/signup.html', {'form': form})
