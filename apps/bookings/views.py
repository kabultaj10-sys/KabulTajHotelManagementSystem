from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.users.decorators import receptionist_required
from django.http import JsonResponse
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Booking, CheckIn, CheckOut, BookingPayment
from apps.guests.models import Guest
from apps.rooms.models import Room, RoomType
from decimal import Decimal


@receptionist_required
def booking_list(request):
    """List all bookings with filtering and search"""
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date_filter', '')
    guest_search = request.GET.get('guest_search', '')
    
    # Base queryset
    bookings = Booking.objects.select_related('guest', 'room', 'room__room_type')
    
    # Apply filters
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    if date_filter:
        today = timezone.now().date()
        if date_filter == 'today':
            bookings = bookings.filter(check_in_date=today)
        elif date_filter == 'tomorrow':
            tomorrow = today + timedelta(days=1)
            bookings = bookings.filter(check_in_date=tomorrow)
        elif date_filter == 'this_week':
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            bookings = bookings.filter(check_in_date__range=[week_start, week_end])
        elif date_filter == 'overdue':
            bookings = bookings.filter(
                status='active',
                check_out_date__lt=today
            )
    
    if guest_search:
        bookings = bookings.filter(
            Q(guest__first_name__icontains=guest_search) |
            Q(guest__last_name__icontains=guest_search) |
            Q(guest__email__icontains=guest_search)
        )
    
    # Get statistics
    total_bookings = Booking.objects.count()
    active_bookings = Booking.objects.filter(status='active').count()
    today_checkins = Booking.objects.filter(
        check_in_date=timezone.now().date(),
        status__in=['confirmed', 'active']
    ).count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    
    context = {
        'bookings': bookings.order_by('-created_at'),
        'status_filter': status_filter,
        'date_filter': date_filter,
        'guest_search': guest_search,
        'stats': {
            'total': total_bookings,
            'active': active_bookings,
            'today_checkins': today_checkins,
            'pending': pending_bookings,
        }
    }
    return render(request, 'bookings/booking_list.html', context)


@receptionist_required
def booking_create(request):
    """Create a new booking with availability checking"""
    if request.method == 'POST':
        guest_id = request.POST.get('guest')
        room_id = request.POST.get('room')
        check_in_date = request.POST.get('check_in_date')
        number_of_guests = request.POST.get('number_of_guests')
        room_rate = request.POST.get('room_rate')
        special_requests = request.POST.get('special_requests')
        source = request.POST.get('source', 'direct')
        
        # Validation
        if not all([guest_id, room_id, check_in_date, number_of_guests, room_rate]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'bookings/booking_form.html', {'title': 'Create Booking'})
        
        try:
            guest = Guest.objects.get(id=guest_id)
            room = Room.objects.get(id=room_id)
            check_in = datetime.strptime(check_in_date, '%Y-%m-%d').date()
            
            # Validate check-in date
            if check_in < timezone.now().date():
                messages.error(request, 'Check-in date cannot be in the past.')
                return render(request, 'bookings/booking_form.html', {'title': 'Create Booking'})
            
            # Check room capacity
            if int(number_of_guests) > room.room_type.capacity:
                messages.error(request, f'Room capacity is {room.room_type.capacity} guests.')
                return render(request, 'bookings/booking_form.html', {'title': 'Create Booking'})
            
            # Create booking with default values
            booking = Booking.objects.create(
                guest=guest,
                room=room,
                check_in_date=check_in,
                check_out_date=check_in,  # Set same as check-in for now
                number_of_guests=int(number_of_guests),
                room_rate=Decimal(room_rate),
                special_requests=special_requests,
                source=source,
                status='pending',  # Default status
                payment_status='pending',  # Default payment status
            )
            
            # Set total amount to room rate for now
            booking.total_amount = Decimal(room_rate)
            booking.save()
            
            messages.success(request, f'Booking {booking.booking_number} created successfully.')
            return redirect('booking_detail', pk=booking.pk)
            
        except (Guest.DoesNotExist, Room.DoesNotExist):
            messages.error(request, 'Invalid guest or room selected.')
        except ValueError:
            messages.error(request, 'Invalid date format.')
    
    # Get available guests and rooms
    guests = Guest.objects.filter(is_active=True).order_by('first_name', 'last_name')
    rooms = Room.objects.filter(is_active=True, status='available').select_related('room_type')
    
    return render(request, 'bookings/booking_form.html', {
        'title': 'Create Booking',
        'guests': guests,
        'rooms': rooms,
    })


def check_room_availability(room, check_in_date, check_out_date):
    """Check if room is available for given dates"""
    conflicting_bookings = Booking.objects.filter(
        room=room,
        status__in=['confirmed', 'active'],
        check_in_date__lt=check_out_date,
        check_out_date__gt=check_in_date
    )
    return conflicting_bookings.count() == 0


@receptionist_required
def booking_detail(request, pk):
    """View booking details with check-in/out information"""
    booking = get_object_or_404(Booking, pk=pk)
    
    # Get check-in/out information
    try:
        check_in = booking.check_in
    except CheckIn.DoesNotExist:
        check_in = None
    
    try:
        check_out = booking.check_out
    except CheckOut.DoesNotExist:
        check_out = None
    
    # Get payment information
    payments = booking.payments.all().order_by('-payment_date')
    total_paid = payments.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    context = {
        'booking': booking,
        'check_in': check_in,
        'check_out': check_out,
        'payments': payments,
        'total_paid': total_paid,
        'remaining_balance': booking.total_amount - total_paid,
    }
    return render(request, 'bookings/booking_detail.html', context)


@receptionist_required
def booking_edit(request, pk):
    """Edit booking with validation"""
    booking = get_object_or_404(Booking, pk=pk)
    
    if request.method == 'POST':
        guest_id = request.POST.get('guest')
        room_id = request.POST.get('room')
        check_in_date = request.POST.get('check_in_date')
        check_out_date = request.POST.get('check_out_date')
        number_of_guests = request.POST.get('number_of_guests')
        room_rate = request.POST.get('room_rate')
        status = request.POST.get('status')
        special_requests = request.POST.get('special_requests')
        
        try:
            guest = Guest.objects.get(id=guest_id)
            room = Room.objects.get(id=room_id)
            check_in = datetime.strptime(check_in_date, '%Y-%m-%d').date()
            
            # Handle check-out date (use existing if not provided)
            if check_out_date:
                check_out = datetime.strptime(check_out_date, '%Y-%m-%d').date()
                # Validate dates
                if check_in >= check_out:
                    messages.error(request, 'Check-out date must be after check-in date.')
                    return render(request, 'bookings/booking_form.html', {
                        'booking': booking,
                        'title': 'Edit Booking'
                    })
            else:
                # If no check-out date provided, use existing one
                check_out = booking.check_out_date
            
            # Check room availability (excluding current booking)
            if not check_room_availability_excluding(room, check_in, check_out, booking):
                messages.error(request, f'Room {room.room_number} is not available for the selected dates.')
                return render(request, 'bookings/booking_form.html', {
                    'booking': booking,
                    'title': 'Edit Booking'
                })
            
            # Update booking
            booking.guest = guest
            booking.room = room
            booking.check_in_date = check_in
            booking.check_out_date = check_out
            booking.number_of_guests = int(number_of_guests)
            booking.room_rate = Decimal(room_rate)
            if status:
                booking.status = status
            booking.special_requests = special_requests
            
            booking.calculate_total_amount()
            booking.save()
            
            messages.success(request, f'Booking {booking.booking_number} updated successfully.')
            return redirect('booking_detail', pk=booking.pk)
            
        except (Guest.DoesNotExist, Room.DoesNotExist):
            messages.error(request, 'Invalid guest or room selected.')
        except ValueError:
            messages.error(request, 'Invalid date format.')
    
    guests = Guest.objects.filter(is_active=True).order_by('first_name', 'last_name')
    rooms = Room.objects.filter(is_active=True).select_related('room_type')
    
    return render(request, 'bookings/booking_form.html', {
        'booking': booking,
        'title': 'Edit Booking',
        'guests': guests,
        'rooms': rooms,
    })


def check_room_availability_excluding(room, check_in_date, check_out_date, exclude_booking):
    """Check room availability excluding a specific booking"""
    conflicting_bookings = Booking.objects.filter(
        room=room,
        status__in=['confirmed', 'active'],
        check_in_date__lt=check_out_date,
        check_out_date__gt=check_in_date
    ).exclude(pk=exclude_booking.pk)
    return conflicting_bookings.count() == 0


@receptionist_required
def booking_delete(request, pk):
    """Delete booking with validation"""
    booking = get_object_or_404(Booking, pk=pk)
    
    # Check if booking is active
    if booking.status == 'active':
        messages.error(request, 'Cannot delete an active booking. Please check out first.')
        return redirect('booking_list')
    
    if request.method == 'POST':
        booking_number = booking.booking_number
        booking.delete()
        messages.success(request, f'Booking {booking_number} deleted successfully.')
        return redirect('booking_list')
    
    return render(request, 'bookings/booking_confirm_delete.html', {'booking': booking})


@receptionist_required
def check_in_create(request, pk):
    """Create check-in for a booking - simplified one-click process"""
    booking = get_object_or_404(Booking, pk=pk)
    
    # Check if already checked in
    if hasattr(booking, 'check_in'):
        messages.error(request, 'Guest is already checked in.')
        return redirect('booking_detail', pk=booking.pk)
    
    # Validate booking status
    if booking.status not in ['confirmed', 'pending']:
        messages.error(request, 'Booking must be confirmed or pending to check in.')
        return redirect('booking_detail', pk=booking.pk)
    
    # Create check-in with default values (simplified process)
    check_in = CheckIn.objects.create(
        booking=booking,
        checked_in_by=request.user,
        id_verified=True,  # Assume verified for simplified process
        payment_verified=True,  # Assume verified for simplified process
        room_inspected=True,  # Assume inspected for simplified process
        room_key_issued=True,  # Assume issued for simplified process
        special_instructions='',
        notes='Check-in completed via simplified process',
    )
    
    # Complete check-in
    check_in.complete_check_in()
    
    messages.success(request, f'Check-in completed for {booking.guest.full_name}. Guest is now checked in.')
    return redirect('booking_detail', pk=booking.pk)


@receptionist_required
def check_out_create(request, pk):
    """Create check-out for a booking - simplified one-click process"""
    booking = get_object_or_404(Booking, pk=pk)
    
    # Check if already checked out
    if hasattr(booking, 'check_out'):
        messages.error(request, 'Guest is already checked out.')
        return redirect('booking_detail', pk=booking.pk)
    
    # Check if checked in
    if not hasattr(booking, 'check_in'):
        messages.error(request, 'Guest must be checked in before check-out.')
        return redirect('booking_detail', pk=booking.pk)
    
    # Create check-out with default values (simplified process)
    check_out = CheckOut.objects.create(
        booking=booking,
        checked_out_by=request.user,
        room_inspected=True,  # Assume inspected for simplified process
        keys_returned=True,  # Assume returned for simplified process
        payment_completed=True,  # Assume completed for simplified process
        additional_charges=Decimal('0.00'),  # No additional charges by default
        late_checkout=False,
        late_checkout_hours=0,
        guest_satisfaction=None,  # Optional
        feedback='',
        notes='Check-out completed via simplified process',
    )
    
    # Complete check-out
    final_amount = check_out.complete_check_out()
    
    messages.success(request, f'Check-out completed for {booking.guest.full_name}. Final amount: ${final_amount}')
    return redirect('booking_detail', pk=booking.pk)


@receptionist_required
def booking_payment_create(request, pk):
    """Create payment for a booking"""
    booking = get_object_or_404(Booking, pk=pk)
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')
        reference_number = request.POST.get('reference_number')
        notes = request.POST.get('notes')
        
        if amount and payment_method:
            payment = BookingPayment.objects.create(
                booking=booking,
                amount=Decimal(amount),
                payment_method=payment_method,
                reference_number=reference_number,
                processed_by=request.user,
                notes=notes,
            )
            
            # Process payment
            if payment.process_payment():
                messages.success(request, f'Payment of ${amount} processed successfully.')
            else:
                messages.error(request, 'Payment processing failed.')
            
            return redirect('booking_detail', pk=booking.pk)
    
    return render(request, 'bookings/payment_form.html', {'booking': booking})


@receptionist_required
def availability_check(request):
    """Check room availability for specific dates"""
    if request.method == 'POST':
        check_in_date = request.POST.get('check_in_date')
        check_out_date = request.POST.get('check_out_date')
        guests = int(request.POST.get('guests', 1))
        
        if check_in_date and check_out_date:
            check_in = datetime.strptime(check_in_date, '%Y-%m-%d').date()
            check_out = datetime.strptime(check_out_date, '%Y-%m-%d').date()
            
            # Get available rooms
            available_rooms = []
            rooms = Room.objects.filter(is_active=True, room_type__capacity__gte=guests)
            
            for room in rooms:
                if check_room_availability(room, check_in, check_out):
                    available_rooms.append({
                        'id': room.id,
                        'room_number': room.room_number,
                        'room_type': room.room_type.name,
                        'capacity': room.room_type.capacity,
                        'price': float(room.effective_price),
                        'floor': room.get_floor_display(),
                    })
            
            return JsonResponse({
                'available_rooms': available_rooms,
                'check_in': check_in_date,
                'check_out': check_out_date,
                'guests': guests,
            })
    
    return render(request, 'bookings/availability_check.html')
