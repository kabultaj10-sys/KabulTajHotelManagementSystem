from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.users.decorators import receptionist_required
from django.http import JsonResponse
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Room, RoomType, RoomMaintenance
from apps.bookings.models import Booking


@receptionist_required
def room_list(request):
    """List all rooms with availability status and current booking info"""
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    floor_filter = request.GET.get('floor', '')
    room_type_filter = request.GET.get('room_type', '')
    
    # Base queryset with related data
    rooms = Room.objects.select_related('room_type').filter(is_active=True)
    
    # Apply filters
    if status_filter:
        rooms = rooms.filter(status=status_filter)
    if floor_filter:
        rooms = rooms.filter(floor=floor_filter)
    if room_type_filter:
        rooms = rooms.filter(room_type_id=room_type_filter)
    
    # Get room types for filter
    room_types = RoomType.objects.filter(is_active=True)
    
    # Get availability statistics
    total_rooms = Room.objects.filter(is_active=True).count()
    available_rooms = Room.objects.filter(status='available', is_active=True).count()
    occupied_rooms = Room.objects.filter(status='occupied', is_active=True).count()
    maintenance_rooms = Room.objects.filter(status='maintenance', is_active=True).count()
    
    # Get current date for availability checking
    today = timezone.now().date()
    
    # Enhance rooms with booking information
    for room in rooms:
        # Get current active booking
        current_booking = room.bookings.filter(
            status__in=['confirmed', 'active'],
            check_in_date__lte=today,
            check_out_date__gte=today
        ).first()
        
        # Get next available date if room is occupied
        if current_booking:
            room.next_available_date = current_booking.check_out_date
            room.current_guest = current_booking.guest.full_name
        else:
            room.next_available_date = None
            room.current_guest = None
        
        # Get upcoming bookings
        upcoming_bookings = room.bookings.filter(
            status__in=['confirmed', 'active'],
            check_in_date__gt=today
        ).order_by('check_in_date')[:3]
        
        room.upcoming_bookings = upcoming_bookings
        
        # Calculate availability status with colors
        if room.status == 'available':
            room.availability_color = 'success'
            room.availability_label = 'Available'
        elif room.status == 'occupied':
            room.availability_color = 'danger'
            room.availability_label = 'Occupied'
        elif room.status == 'maintenance':
            room.availability_color = 'warning'
            room.availability_label = 'Maintenance'
        elif room.status == 'cleaning':
            room.availability_color = 'info'
            room.availability_label = 'Cleaning'
        elif room.status == 'reserved':
            room.availability_color = 'primary'
            room.availability_label = 'Reserved'
        else:
            room.availability_color = 'secondary'
            room.availability_label = room.get_status_display()
    
    context = {
        'rooms': rooms,
        'room_types': room_types,
        'status_filter': status_filter,
        'floor_filter': floor_filter,
        'room_type_filter': room_type_filter,
        'stats': {
            'total': total_rooms,
            'available': available_rooms,
            'occupied': occupied_rooms,
            'maintenance': maintenance_rooms,
        },
        'today': today,
    }
    return render(request, 'rooms/room_list.html', context)


@receptionist_required
def room_availability(request):
    """Check room availability for specific dates"""
    if request.method == 'POST':
        check_in_date = request.POST.get('check_in_date')
        check_out_date = request.POST.get('check_out_date')
        guests = request.POST.get('guests', 1)
        
        if check_in_date and check_out_date:
            # Convert to date objects
            check_in = datetime.strptime(check_in_date, '%Y-%m-%d').date()
            check_out = datetime.strptime(check_out_date, '%Y-%m-%d').date()
            
            # Find available rooms
            available_rooms = get_available_rooms(check_in, check_out, int(guests))
            
            return JsonResponse({
                'available_rooms': [
                    {
                        'id': room.id,
                        'room_number': room.room_number,
                        'room_type': room.room_type.name,
                        'capacity': room.room_type.capacity,
                        'price': float(room.effective_price),
                        'floor': room.get_floor_display(),
                    }
                    for room in available_rooms
                ]
            })
    
    return render(request, 'rooms/room_availability.html')


def get_available_rooms(check_in_date, check_out_date, guests=1):
    """Get available rooms for given dates and guest count"""
    # Get all active rooms
    rooms = Room.objects.filter(is_active=True)
    
    # Filter by capacity
    rooms = rooms.filter(room_type__capacity__gte=guests)
    
    # Get conflicting bookings
    conflicting_bookings = Booking.objects.filter(
        status__in=['confirmed', 'active'],
        check_in_date__lt=check_out_date,
        check_out_date__gt=check_in_date
    )
    
    # Get rooms that are not in conflicting bookings
    booked_room_ids = conflicting_bookings.values_list('room_id', flat=True)
    available_rooms = rooms.exclude(id__in=booked_room_ids)
    
    # Filter by room status
    available_rooms = available_rooms.filter(status='available')
    
    return available_rooms


@receptionist_required
def room_create(request):
    """Create a new room with validation"""
    if request.method == 'POST':
        room_number = request.POST.get('room_number')
        room_type_id = request.POST.get('room_type')
        floor = request.POST.get('floor')
        current_price = request.POST.get('current_price')
        notes = request.POST.get('notes')
        
        # Validation
        if not all([room_number, room_type_id, floor]):
            messages.error(request, 'Please fill in all required fields.')
            room_types = RoomType.objects.filter(is_active=True)
            return render(request, 'rooms/room_form.html', {
                'room_types': room_types,
                'title': 'Add Room'
            })
        
        # Check if room number already exists
        if Room.objects.filter(room_number=room_number).exists():
            messages.error(request, f'Room number {room_number} already exists.')
            room_types = RoomType.objects.filter(is_active=True)
            return render(request, 'rooms/room_form.html', {
                'room_types': room_types,
                'title': 'Add Room'
            })
        
        try:
            room_type = RoomType.objects.get(id=room_type_id)
            room = Room.objects.create(
                room_number=room_number,
                room_type=room_type,
                floor=floor,
                current_price=current_price if current_price else None,
                notes=notes
            )
            messages.success(request, f'Room {room.room_number} created successfully.')
            return redirect('room_list')
        except RoomType.DoesNotExist:
            messages.error(request, 'Invalid room type selected.')
    
    room_types = RoomType.objects.filter(is_active=True)
    return render(request, 'rooms/room_form.html', {
        'room_types': room_types,
        'title': 'Add Room'
    })


@receptionist_required
def room_edit(request, pk):
    """Edit room with validation"""
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        room_number = request.POST.get('room_number')
        room_type_id = request.POST.get('room_type')
        floor = request.POST.get('floor')
        status = request.POST.get('status')
        current_price = request.POST.get('current_price')
        notes = request.POST.get('notes')
        
        # Check if room number already exists (excluding current room)
        if room_number != room.room_number and Room.objects.filter(room_number=room_number).exists():
            messages.error(request, f'Room number {room_number} already exists.')
            room_types = RoomType.objects.filter(is_active=True)
            return render(request, 'rooms/room_form.html', {
                'room': room,
                'room_types': room_types,
                'title': 'Edit Room'
            })
        
        try:
            room.room_number = room_number
            if room_type_id:
                room.room_type = RoomType.objects.get(id=room_type_id)
            room.floor = floor
            room.status = status
            room.current_price = current_price if current_price else None
            room.notes = notes
            room.save()
            
            messages.success(request, f'Room {room.room_number} updated successfully.')
            return redirect('room_list')
        except RoomType.DoesNotExist:
            messages.error(request, 'Invalid room type selected.')
    
    room_types = RoomType.objects.filter(is_active=True)
    return render(request, 'rooms/room_form.html', {
        'room': room,
        'room_types': room_types,
        'title': 'Edit Room'
    })


@receptionist_required
def room_detail(request, pk):
    """View room details with comprehensive guest and booking information"""
    room = get_object_or_404(Room, pk=pk)
    
    # Get current date for availability checking
    today = timezone.now().date()
    
    # Get current active booking
    current_booking = room.bookings.filter(
        status__in=['confirmed', 'active'],
        check_in_date__lte=today,
        check_out_date__gte=today
    ).first()
    
    # Get upcoming confirmed bookings
    upcoming_bookings = room.bookings.filter(
        status__in=['confirmed', 'active'],
        check_in_date__gt=today
    ).order_by('check_in_date')[:5]
    
    # Get all recent bookings (last 30 days)
    recent_bookings = room.bookings.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    ).order_by('-created_at')[:10]
    
    # Get all-time booking history
    all_bookings = room.bookings.all().order_by('-created_at')[:20]
    
    # Get recent maintenance records
    maintenance_records = room.maintenance_records.filter(
        status__in=['scheduled', 'in_progress']
    ).order_by('-scheduled_date')[:5]
    
    # Get all maintenance history
    all_maintenance = room.maintenance_records.all().order_by('-scheduled_date')[:10]
    
    # Calculate room statistics
    total_bookings = room.bookings.count()
    completed_bookings = room.bookings.filter(status='completed').count()
    cancelled_bookings = room.bookings.filter(status='cancelled').count()
    total_revenue = room.bookings.filter(status='completed').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Get current guest details if room is occupied
    current_guest = None
    if current_booking:
        current_guest = current_booking.guest
    
    # Get payment information for current booking
    current_payments = []
    if current_booking:
        # Import here to avoid circular imports
        from apps.billing.models import Payment
        current_payments = Payment.objects.filter(
            invoice__booking=current_booking
        ).order_by('-payment_date')
    
    context = {
        'room': room,
        'current_booking': current_booking,
        'current_guest': current_guest,
        'upcoming_bookings': upcoming_bookings,
        'recent_bookings': recent_bookings,
        'all_bookings': all_bookings,
        'maintenance_records': maintenance_records,
        'all_maintenance': all_maintenance,
        'current_payments': current_payments,
        'today': today,
        'stats': {
            'total_bookings': total_bookings,
            'completed_bookings': completed_bookings,
            'cancelled_bookings': cancelled_bookings,
            'total_revenue': total_revenue,
        }
    }
    return render(request, 'rooms/room_detail.html', context)


@receptionist_required
def room_delete(request, pk):
    """Delete room with validation"""
    room = get_object_or_404(Room, pk=pk)
    
    # Check if room has active bookings
    active_bookings = room.bookings.filter(status__in=['confirmed', 'active'])
    if active_bookings.exists():
        messages.error(request, f'Cannot delete room {room.room_number}. It has active bookings.')
        return redirect('room_list')
    
    if request.method == 'POST':
        room_number = room.room_number
        room.delete()
        messages.success(request, f'Room {room_number} deleted successfully.')
        return redirect('room_list')
    
    return render(request, 'rooms/room_confirm_delete.html', {'room': room})


@receptionist_required
def room_maintenance(request, pk):
    """Manage room maintenance"""
    room = get_object_or_404(Room, pk=pk)
    
    if request.method == 'POST':
        maintenance_type = request.POST.get('maintenance_type')
        description = request.POST.get('description')
        scheduled_date = request.POST.get('scheduled_date')
        cost = request.POST.get('cost')
        notes = request.POST.get('notes')
        status = request.POST.get('status', 'scheduled')

        if all([maintenance_type, description, scheduled_date]):
            RoomMaintenance.objects.create(
                room=room,
                maintenance_type=maintenance_type,
                description=description,
                scheduled_date=scheduled_date,
                cost=cost if cost else None,
                notes=notes or '',
                status=status
            )

            # Update room status to maintenance when a new maintenance is added
            room.status = 'maintenance'
            room.save()

            messages.success(request, f'Maintenance record added for Room {room.room_number}.')
            return redirect('room_maintenance', pk=pk)
    
    maintenance_records = room.maintenance_records.all().order_by('-scheduled_date')
    return render(request, 'rooms/room_maintenance.html', {
        'room': room,
        'maintenance_records': maintenance_records
    })


@receptionist_required
def room_maintenance_edit(request, pk, maintenance_id):
    """Edit an existing maintenance record for a room"""
    room = get_object_or_404(Room, pk=pk)
    maintenance = get_object_or_404(RoomMaintenance, pk=maintenance_id, room=room)

    if request.method == 'POST':
        maintenance.maintenance_type = request.POST.get('maintenance_type') or maintenance.maintenance_type
        maintenance.description = request.POST.get('description') or maintenance.description
        maintenance.scheduled_date = request.POST.get('scheduled_date') or maintenance.scheduled_date
        maintenance.completed_date = request.POST.get('completed_date') or maintenance.completed_date
        cost = request.POST.get('cost')
        maintenance.cost = cost if cost else None
        maintenance.notes = request.POST.get('notes') or ''
        maintenance.status = request.POST.get('status') or maintenance.status
        maintenance.save()

        # Optionally update room status based on maintenance status
        if maintenance.status in ['scheduled', 'in_progress']:
            room.status = 'maintenance'
            room.save()
        elif maintenance.status == 'completed' and room.status == 'maintenance':
            room.status = 'available'
            room.save()

        messages.success(request, f'Maintenance updated for Room {room.room_number}.')
        return redirect('room_maintenance', pk=pk)

    return render(request, 'rooms/room_maintenance.html', {
        'room': room,
        'maintenance_records': room.maintenance_records.all().order_by('-scheduled_date'),
        'edit_record': maintenance,
    })


@receptionist_required
def room_maintenance_delete(request, pk, maintenance_id):
    """Delete a maintenance record for a room"""
    room = get_object_or_404(Room, pk=pk)
    maintenance = get_object_or_404(RoomMaintenance, pk=maintenance_id, room=room)

    if request.method == 'POST':
        maintenance.delete()
        messages.success(request, f'Maintenance record deleted for Room {room.room_number}.')
        return redirect('room_maintenance', pk=pk)

    # Perform delete via POST only; for GET redirect back
    messages.error(request, 'Invalid request method for delete.')
    return redirect('room_maintenance', pk=pk)
