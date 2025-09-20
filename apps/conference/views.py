from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ConferenceRoom, ConferenceBooking, ConferenceEquipment
from django.db.models import Sum
from django.db import models
from django import forms
from django.utils import timezone
from datetime import datetime
from apps.users.decorators import admin_required


@admin_required
def conference_list(request):
    """Conference dashboard with room and booking overview"""
    
    # Get conference rooms
    rooms = ConferenceRoom.objects.all()
    total_rooms = rooms.count()
    available_rooms = rooms.filter(status='available').count()
    occupied_rooms = rooms.filter(status='occupied').count()
    
    # Get recent bookings
    recent_bookings = ConferenceBooking.objects.select_related('room').order_by('-created_at')[:5]
    
    # Get equipment
    equipment = ConferenceEquipment.objects.all()
    total_equipment = equipment.count()
    available_equipment = equipment.filter(is_available=True).count()
    
    # Calculate revenue
    total_revenue = ConferenceBooking.objects.filter(status='confirmed').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    context = {
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'total_equipment': total_equipment,
        'available_equipment': available_equipment,
        'total_revenue': total_revenue,
        'rooms': rooms,
        'recent_bookings': recent_bookings,
        'equipment': equipment,
    }
    
    return render(request, 'conference/conference_list.html', context)


@admin_required
def room_list(request):
    """List conference rooms"""
    rooms = ConferenceRoom.objects.all().order_by('name')
    
    context = {
        'rooms': rooms,
        'total_rooms': rooms.count(),
        'available_rooms': rooms.filter(status='available').count(),
        'occupied_rooms': rooms.filter(status='occupied').count(),
        'maintenance_rooms': rooms.filter(status='maintenance').count(),
    }
    
    return render(request, 'conference/room_list.html', context)


@admin_required
def room_create(request):
    """Create a new conference room"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            capacity = request.POST.get('capacity')
            floor = request.POST.get('floor')
            hourly_rate = request.POST.get('hourly_rate')
            daily_rate = request.POST.get('daily_rate')
            description = request.POST.get('description', '')
            amenities = request.POST.get('amenities', '')
            status = request.POST.get('status', 'available')
            is_active = request.POST.get('is_active') == 'on'
            
            # Validate required fields
            if not name or not capacity or not floor or not hourly_rate or not daily_rate:
                messages.error(request, 'Please fill in all required fields.')
                return render(request, 'conference/room_form.html', {
                    'room': request.POST
                })
            
            # Convert numeric fields
            from decimal import Decimal
            try:
                capacity = int(capacity)
                floor = int(floor)
                hourly_rate = Decimal(hourly_rate)
                daily_rate = Decimal(daily_rate)
            except (ValueError, TypeError):
                messages.error(request, 'Invalid numeric values.')
                return render(request, 'conference/room_form.html', {
                    'room': request.POST
                })
            
            # Create the room
            room = ConferenceRoom.objects.create(
                name=name,
                capacity=capacity,
                floor=floor,
                hourly_rate=hourly_rate,
                daily_rate=daily_rate,
                description=description,
                amenities=amenities,
                status=status,
                is_active=is_active,
            )
            
            # Handle image uploads
            if request.FILES.get('image_1'):
                room.image_1 = request.FILES['image_1']
            if request.FILES.get('image_2'):
                room.image_2 = request.FILES['image_2']
            if request.FILES.get('image_3'):
                room.image_3 = request.FILES['image_3']
            
            room.save()
            
            messages.success(request, f'Conference room "{room.name}" created successfully.')
            return redirect('conference:conference_room_list')
            
        except Exception as e:
            messages.error(request, f'Error creating conference room: {str(e)}')
            return render(request, 'conference/room_form.html', {
                'room': request.POST
            })
    
    context = {
        'title': 'Add Conference Room',
        'status_choices': ConferenceRoom.STATUS_CHOICES,
    }
    return render(request, 'conference/room_form.html', context)


@admin_required
def room_detail(request, pk):
    """View conference room details"""
    try:
        room = ConferenceRoom.objects.get(pk=pk)
    except ConferenceRoom.DoesNotExist:
        messages.error(request, 'Conference room not found.')
        return redirect('conference:conference_room_list')
    
    # Get recent bookings for this room
    recent_bookings = room.bookings.all().order_by('-created_at')[:5]
    
    context = {
        'room': room,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'conference/room_detail.html', context)


@admin_required
def room_edit(request, pk):
    """Edit conference room"""
    try:
        room = ConferenceRoom.objects.get(pk=pk)
    except ConferenceRoom.DoesNotExist:
        messages.error(request, 'Conference room not found.')
        return redirect('conference:conference_room_list')
    
    if request.method == 'POST':
        try:
            # Update room fields
            room.name = request.POST.get('name')
            room.capacity = int(request.POST.get('capacity'))
            room.floor = int(request.POST.get('floor'))
            room.hourly_rate = Decimal(request.POST.get('hourly_rate'))
            room.daily_rate = Decimal(request.POST.get('daily_rate'))
            room.description = request.POST.get('description', '')
            room.amenities = request.POST.get('amenities', '')
            room.status = request.POST.get('status', 'available')
            room.is_active = request.POST.get('is_active') == 'on'
            
            # Handle image updates
            if request.FILES.get('image_1'):
                room.image_1 = request.FILES['image_1']
            if request.FILES.get('image_2'):
                room.image_2 = request.FILES['image_2']
            if request.FILES.get('image_3'):
                room.image_3 = request.FILES['image_3']
            
            # Handle image removal
            if request.POST.get('remove_image_1'):
                room.image_1.delete(save=False)
                room.image_1 = None
            if request.POST.get('remove_image_2'):
                room.image_2.delete(save=False)
                room.image_2 = None
            if request.POST.get('remove_image_3'):
                room.image_3.delete(save=False)
                room.image_3 = None
            
            room.save()
            
            messages.success(request, f'Conference room "{room.name}" updated successfully.')
            return redirect('conference:conference_room_list')
            
        except Exception as e:
            messages.error(request, f'Error updating conference room: {str(e)}')
    
    context = {
        'room': room,
        'title': 'Edit Conference Room',
        'status_choices': ConferenceRoom.STATUS_CHOICES,
    }
    return render(request, 'conference/room_form.html', context)


@admin_required
def room_delete(request, pk):
    """Delete conference room"""
    try:
        room = ConferenceRoom.objects.get(pk=pk)
    except ConferenceRoom.DoesNotExist:
        messages.error(request, 'Conference room not found.')
        return redirect('conference:conference_room_list')
    
    if request.method == 'POST':
        try:
            # Check if room has active bookings
            active_bookings = room.bookings.filter(
                status__in=['confirmed', 'pending']
            ).exists()
            
            if active_bookings:
                messages.warning(
                    request, 
                    f'Conference room "{room.name}" has active bookings. '
                    'Please cancel those bookings before deleting this room.'
                )
                return redirect('conference:conference_room_list')
            
            room_name = room.name
            room.delete()
            
            messages.success(request, f'Conference room "{room_name}" deleted successfully.')
            return redirect('conference:conference_room_list')
            
        except Exception as e:
            messages.error(request, f'Error deleting conference room: {str(e)}')
    
    context = {
        'room': room,
    }
    return render(request, 'conference/room_confirm_delete.html', context)


@admin_required
def booking_list(request):
    """List conference bookings"""
    bookings = ConferenceBooking.objects.select_related('room').all().order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    # Filter by date if provided
    date_filter = request.GET.get('date')
    if date_filter:
        bookings = bookings.filter(start_datetime__date=date_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        bookings = bookings.filter(
            models.Q(client_name__icontains=search_query) |
            models.Q(event_title__icontains=search_query) |
            models.Q(booking_number__icontains=search_query)
        )
    
    context = {
        'bookings': bookings,
        'total_bookings': bookings.count(),
        'confirmed_bookings': bookings.filter(status='confirmed').count(),
        'pending_bookings': bookings.filter(status='pending').count(),
        'cancelled_bookings': bookings.filter(status='cancelled').count(),
    }
    
    return render(request, 'conference/booking_list.html', context)


class DateTimeLocalInput(forms.DateTimeInput):
    input_type = 'datetime-local'

class ConferenceBookingForm(forms.ModelForm):
    class Meta:
        model = ConferenceBooking
        fields = ['room', 'client_name', 'client_email', 'client_phone', 'event_title', 'event_description', 'start_datetime', 'end_datetime', 'attendees_count', 'total_amount', 'special_requirements']
        exclude = ['booking_number', 'created_by', 'created_at', 'updated_at']
        widgets = {
            'start_datetime': DateTimeLocalInput(attrs={'class': 'form-control'}),
            'end_datetime': DateTimeLocalInput(attrs={'class': 'form-control'}),
            'event_description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Describe the event, agenda, or any special details...'}),
            'special_requirements': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Any special requirements, equipment needs, or additional notes...'}),
            'client_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter client full name'}),
            'client_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'client@example.com'}),
            'client_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 123-4567'}),
            'event_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter event title'}),
            'attendees_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 1000}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'room': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter rooms to only show available ones
        self.fields['room'].queryset = ConferenceRoom.objects.filter(status='available', is_active=True)
        
        # Add help text
        self.fields['client_name'].help_text = 'Full name of the person making the booking'
        self.fields['client_email'].help_text = 'Email address for booking confirmations'
        self.fields['client_phone'].help_text = 'Contact phone number'
        self.fields['event_title'].help_text = 'Name or title of the event'
        self.fields['attendees_count'].help_text = 'Expected number of attendees'
        self.fields['total_amount'].help_text = 'Total cost for the booking'
        self.fields['room'].help_text = 'Select an available conference room'
        self.fields['start_datetime'].help_text = 'Select a future date and time for the event start'
        self.fields['end_datetime'].help_text = 'Select a date and time after the start time'
    
    def clean_start_datetime(self):
        start_datetime = self.cleaned_data.get('start_datetime')
        if start_datetime and start_datetime.date() < timezone.now().date():
            raise forms.ValidationError('Start date cannot be in the past.')
        return start_datetime
    
    def clean_end_datetime(self):
        end_datetime = self.cleaned_data.get('end_datetime')
        start_datetime = self.cleaned_data.get('start_datetime')
        if start_datetime and end_datetime and end_datetime <= start_datetime:
            raise forms.ValidationError('End date/time must be after start date/time.')
        return end_datetime
    
    def clean_attendees_count(self):
        attendees_count = self.cleaned_data.get('attendees_count')
        room = self.cleaned_data.get('room')
        if attendees_count and room and attendees_count > room.capacity:
            raise forms.ValidationError(f'Number of attendees ({attendees_count}) exceeds room capacity ({room.capacity}).')
        return attendees_count

@admin_required
def booking_create(request):
    if request.method == 'POST':
        form = ConferenceBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.created_by = request.user
            # Set default values for fields not in form
            booking.status = 'pending'
            booking.payment_status = 'pending'
            booking.paid_amount = 0
            # Generate booking number if not provided
            if not booking.booking_number:
                import uuid
                booking.booking_number = f"CONF-{uuid.uuid4().hex[:8].upper()}"
            booking.save()
            messages.success(request, f'Conference booking "{booking.booking_number}" created successfully.')
            return redirect('conference:conference_booking_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ConferenceBookingForm()
    
    # Get available rooms for the form
    available_rooms = ConferenceRoom.objects.filter(status='available', is_active=True)
    
    # Check if there are available rooms
    if not available_rooms.exists():
        messages.warning(request, 'No conference rooms are currently available. Please contact the administrator.')
    
    context = {
        'form': form,
        'available_rooms': available_rooms,
        'title': 'Create Conference Booking',
    }
    return render(request, 'conference/booking_form.html', context)


@admin_required
def booking_detail(request, pk):
    """View conference booking details"""
    try:
        booking = ConferenceBooking.objects.get(pk=pk)
    except ConferenceBooking.DoesNotExist:
        from django.contrib import messages
        messages.error(request, 'Conference booking not found.')
        return redirect('conference:conference_booking_list')
    
    context = {
        'booking': booking,
    }
    return render(request, 'conference/booking_detail.html', context)


@admin_required
def booking_edit(request, pk):
    """Edit conference booking"""
    try:
        booking = ConferenceBooking.objects.get(pk=pk)
    except ConferenceBooking.DoesNotExist:
        messages.error(request, 'Conference booking not found.')
        return redirect('conference:conference_booking_list')
    
    if request.method == 'POST':
        form = ConferenceBookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, f'Conference booking "{booking.booking_number}" updated successfully.')
            return redirect('conference:conference_booking_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ConferenceBookingForm(instance=booking)
    
    # Get available rooms for the form
    available_rooms = ConferenceRoom.objects.filter(status='available', is_active=True)
    
    context = {
        'form': form,
        'booking': booking,
        'available_rooms': available_rooms,
        'title': 'Edit Conference Booking'
    }
    return render(request, 'conference/booking_form.html', context)


@admin_required
def booking_delete(request, pk):
    """Delete conference booking"""
    try:
        booking = ConferenceBooking.objects.get(pk=pk)
    except ConferenceBooking.DoesNotExist:
        from django.contrib import messages
        messages.error(request, 'Conference booking not found.')
        return redirect('conference:conference_booking_list')
    
    if request.method == 'POST':
        try:
            booking_number = booking.booking_number
            booking.delete()
            from django.contrib import messages
            messages.success(request, f'Conference booking {booking_number} deleted successfully.')
            return redirect('conference:conference_booking_list')
        except Exception as e:
            from django.contrib import messages
            messages.error(request, f'Error deleting conference booking: {str(e)}')
    
    context = {
        'booking': booking,
    }
    return render(request, 'conference/booking_confirm_delete.html', context)


@admin_required
def booking_mark_completed(request, pk):
    """Mark a conference booking as completed (happened)."""
    booking = get_object_or_404(ConferenceBooking, pk=pk)
    if request.method == 'POST':
        try:
            if booking.status != 'completed':
                booking.status = 'completed'
                booking.save(update_fields=['status', 'updated_at'])
            messages.success(request, f'Conference booking "{booking.booking_number}" marked as completed.')
            return redirect('conference:conference_booking_list')
        except Exception as e:
            messages.error(request, f'Error updating booking status: {str(e)}')
            return redirect('conference:booking_detail', pk=pk)
    # Fallback for non-POST requests
    return redirect('conference:booking_detail', pk=pk)
