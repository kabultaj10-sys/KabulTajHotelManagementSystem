from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.users.decorators import receptionist_required
from django.db.models import Q, Count, Sum, Min, Max
from django.core.paginator import Paginator
from .models import Guest, GuestPreference, GuestDocument
from apps.bookings.models import Booking, CheckIn, CheckOut
from django.http import HttpResponse
import csv
import io
import json
import os
import zipfile
from django.conf import settings


@receptionist_required
def guest_list(request):
    """List all guests with search and filtering"""
    # Get search and filter parameters
    search = request.GET.get('search', '')
    vip_status = request.GET.get('vip_status', '')
    nationality = request.GET.get('nationality', '')
    
    # Base queryset
    guests = Guest.objects.filter(is_active=True)
    
    # Apply search
    if search:
        guests = guests.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search) |
            Q(passport_number__icontains=search)
        )
    
    # Apply filters
    if vip_status:
        guests = guests.filter(vip_status=vip_status)
    if nationality:
        guests = guests.filter(nationality__icontains=nationality)
    
    # Pagination
    paginator = Paginator(guests.order_by('-created_at'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get statistics
    total_guests = Guest.objects.filter(is_active=True).count()
    vip_guests = Guest.objects.filter(is_active=True, vip_status__in=['silver', 'gold', 'platinum']).count()
    recent_guests = Guest.objects.filter(is_active=True).order_by('-created_at')[:5]
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'vip_status': vip_status,
        'nationality': nationality,
        'stats': {
            'total': total_guests,
            'vip': vip_guests,
        },
        'recent_guests': recent_guests,
    }
    return render(request, 'guests/guest_list.html', context)


@receptionist_required
def guest_create(request):
    """Create a new guest with comprehensive information"""
    if request.method == 'POST':
        # Type selection
        guest_type = request.POST.get('guest_type', 'booking')
        # Basic information
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        guest_source = request.POST.get('guest_source', '')
        age = request.POST.get('age')
        
        # Personal details
        date_of_birth = request.POST.get('date_of_birth')
        gender = request.POST.get('gender')
        nationality = request.POST.get('nationality')
        passport_number = request.POST.get('passport_number')
        id_type = request.POST.get('id_type')
        id_number = request.POST.get('id_number')
        
        # Address
        address = request.POST.get('address')
        city = request.POST.get('city')
        country = request.POST.get('country')
        postal_code = request.POST.get('postal_code')
        
        # VIP and preferences
        vip_status = request.POST.get('vip_status', 'regular')
        special_requests = request.POST.get('special_requests')
        dietary_restrictions = request.POST.get('dietary_restrictions')
        room_preferences = request.POST.get('room_preferences')
        
        # Business information
        company = request.POST.get('company')
        job_title = request.POST.get('job_title')
        business_phone = request.POST.get('business_phone')
        
        # Emergency contact
        emergency_contact_name = request.POST.get('emergency_contact_name')
        emergency_contact_phone = request.POST.get('emergency_contact_phone')
        emergency_contact_relationship = request.POST.get('emergency_contact_relationship')
        
        # File upload
        id_picture = request.FILES.get('id_picture')
        
        # Validation based on guest type
        if guest_type in ['gym', 'swimming']:
            if not all([first_name, last_name, phone]):
                messages.error(request, 'Please fill in required fields: first name, last name, phone.')
                return render(request, 'guests/guest_form.html', {'title': 'Add Guest'})
            # email is optional; clear out unrelated fields
            email = email or None
        else:
            # booking guest: email optional per request, but keep phone required
            if not all([first_name, last_name, phone]):
                messages.error(request, 'Please fill in required fields: first name, last name, phone.')
                return render(request, 'guests/guest_form.html', {'title': 'Add Guest'})
        
        # Check if email already exists (only when provided)
        if email and Guest.objects.filter(email=email).exists():
            messages.error(request, 'A guest with this email already exists.')
            return render(request, 'guests/guest_form.html', {'title': 'Add Guest'})
        
        try:
            guest = Guest.objects.create(
                guest_type=guest_type,
                first_name=first_name,
                last_name=last_name,
                email=email if email else None,
                phone=phone,
                guest_source=guest_source,
                age=int(age) if age else None,
                date_of_birth=date_of_birth if date_of_birth else None,
                gender=gender if gender else '',
                nationality=nationality if nationality else '',
                passport_number=passport_number if passport_number else '',
                id_type=id_type if id_type else '',
                id_number=id_number if id_number else '',
                address=address if address else '',
                city=city if city else None,
                country=country if country else None,
                postal_code=postal_code if postal_code else None,
                vip_status=vip_status,
                special_requests=special_requests if special_requests else '',
                dietary_restrictions=dietary_restrictions if dietary_restrictions else '',
                room_preferences=room_preferences if room_preferences else '',
                company=company if company else '',
                job_title=job_title if job_title else '',
                business_phone=business_phone if business_phone else '',
                emergency_contact_name=emergency_contact_name if emergency_contact_name else '',
                emergency_contact_phone=emergency_contact_phone if emergency_contact_phone else '',
                emergency_contact_relationship=emergency_contact_relationship if emergency_contact_relationship else '',
            )
            
            # Handle file upload
            if id_picture:
                guest.id_picture = id_picture
                guest.save()
            
            messages.success(request, f'Guest {guest.full_name} created successfully.')
            return redirect('guest_list')
        except Exception as e:
            messages.error(request, f'Error creating guest: {str(e)}')
    
    return render(request, 'guests/guest_form.html', {'title': 'Add Guest'})


@receptionist_required
def guest_detail(request, pk):
    """View comprehensive guest details with stay history.
    If the Guest has been deleted, fall back to the latest historical snapshot.
    """
    try:
        guest = Guest.objects.get(pk=pk)
    except Guest.DoesNotExist:
        # Fall back to historical record so deleted guests can still be viewed
        historical = Guest.history.filter(id=pk).order_by('-history_date').first()
        if not historical:
            return render(request, '404.html', status=404)

        context = {
            'historical_guest': historical,
            'is_deleted': historical.history_type == '-',
        }
        return render(request, 'guests/guest_detail_deleted.html', context)

    # Get booking statistics
    total_bookings = guest.bookings.count()
    completed_bookings = guest.bookings.filter(status='completed').count()
    active_bookings = guest.bookings.filter(status='active').count()
    total_spent = guest.total_spent
    
    # Get recent bookings
    recent_bookings = guest.bookings.order_by('-created_at')[:5]
    
    # Get stay history
    stay_history = guest.bookings.filter(status='completed').order_by('-check_out_date')
    
    # Get preferences
    try:
        preferences = guest.preferences
    except GuestPreference.DoesNotExist:
        preferences = None
    
    # Get documents
    documents = guest.documents.all().order_by('-created_at')
    
    context = {
        'guest': guest,
        'stats': {
            'total_bookings': total_bookings,
            'completed_bookings': completed_bookings,
            'active_bookings': active_bookings,
            'total_spent': total_spent,
            'total_stays': guest.total_stays,
            'total_nights': guest.total_nights,
        },
        'recent_bookings': recent_bookings,
        'stay_history': stay_history,
        'preferences': preferences,
        'documents': documents,
    }
    return render(request, 'guests/guest_detail.html', context)


@receptionist_required
def guest_export(request, pk):
    """Download a ZIP containing the guest's data and identity documents.
    The ZIP contains a top-level folder named with the guest's full name and stay dates.
    """
    guest = get_object_or_404(Guest, pk=pk)

    # Compute stay date range from bookings (use all bookings for robustness)
    dates = guest.bookings.aggregate(
        earliest=Min('check_in_date'),
        latest=Max('check_out_date')
    )
    if dates.get('earliest') and dates.get('latest'):
        date_part = f"{dates['earliest']:%Y-%m-%d}_to_{dates['latest']:%Y-%m-%d}"
    else:
        date_part = "no_stays"

    folder_name = f"{guest.full_name} - {date_part}".strip()
    safe_folder_name = folder_name.replace('/', '_')

    # Prepare in-memory ZIP
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Include metadata.json with guest data summary
        guest_data = {
            'id': guest.id,
            'full_name': guest.full_name,
            'email': guest.email,
            'phone': guest.phone,
            'gender': guest.get_gender_display() if hasattr(guest, 'get_gender_display') else guest.gender,
            'date_of_birth': guest.date_of_birth.isoformat() if guest.date_of_birth else None,
            'nationality': guest.nationality,
            'address': guest.address,
            'city': guest.city,
            'country': guest.country,
            'postal_code': guest.postal_code,
            'vip_status': guest.get_vip_status_display(),
            'passport_number': guest.passport_number,
            'id_type': guest.get_id_type_display() if hasattr(guest, 'get_id_type_display') else guest.id_type,
            'id_number': guest.id_number,
            'stays': [
                {
                    'booking_number': b.booking_number,
                    'room_id': b.room_id,
                    'check_in_date': b.check_in_date.isoformat() if b.check_in_date else None,
                    'check_out_date': b.check_out_date.isoformat() if b.check_out_date else None,
                    'status': b.status,
                    'total_amount': str(b.total_amount),
                }
                for b in guest.bookings.order_by('check_in_date')
            ]
        }
        metadata_path = f"{safe_folder_name}/metadata.json"
        zipf.writestr(metadata_path, json.dumps(guest_data, indent=2))

        # Helper to add a file into the zip if it exists
        def add_media_file(field_file, subdir):
            if field_file and getattr(field_file, 'name', None):
                abs_path = os.path.join(settings.MEDIA_ROOT, field_file.name)
                if os.path.exists(abs_path):
                    arcname = f"{safe_folder_name}/{subdir}/{os.path.basename(field_file.name)}"
                    zipf.write(abs_path, arcname)

        # Add ID picture if available
        add_media_file(getattr(guest, 'id_picture', None), 'identity')

        # Add attached GuestDocument files
        for doc in guest.documents.all():
            add_media_file(getattr(doc, 'document_file', None), 'documents')

    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{safe_folder_name}.zip"'
    return response


@receptionist_required
def guest_edit(request, pk):
    """Edit guest with comprehensive information"""
    guest = get_object_or_404(Guest, pk=pk)
    
    if request.method == 'POST':
        guest.guest_type = request.POST.get('guest_type', guest.guest_type)
        # Update all fields
        guest.first_name = request.POST.get('first_name', guest.first_name)
        guest.last_name = request.POST.get('last_name', guest.last_name)
        # Email optional
        guest.email = request.POST.get('email') or None
        guest.phone = request.POST.get('phone', guest.phone)
        guest.guest_source = request.POST.get('guest_source', guest.guest_source)
        age_val = request.POST.get('age')
        guest.age = int(age_val) if age_val else None
        guest.date_of_birth = request.POST.get('date_of_birth') or None
        guest.gender = request.POST.get('gender', guest.gender)
        guest.nationality = request.POST.get('nationality', guest.nationality)
        guest.passport_number = request.POST.get('passport_number', guest.passport_number)
        guest.id_type = request.POST.get('id_type', guest.id_type)
        guest.id_number = request.POST.get('id_number', guest.id_number)
        guest.address = request.POST.get('address', guest.address)
        guest.city = request.POST.get('city') or None
        guest.country = request.POST.get('country') or None
        guest.postal_code = request.POST.get('postal_code') or None
        guest.vip_status = request.POST.get('vip_status', guest.vip_status)
        guest.special_requests = request.POST.get('special_requests', guest.special_requests)
        guest.dietary_restrictions = request.POST.get('dietary_restrictions', guest.dietary_restrictions)
        guest.room_preferences = request.POST.get('room_preferences', guest.room_preferences)
        guest.company = request.POST.get('company', guest.company)
        guest.job_title = request.POST.get('job_title', guest.job_title)
        guest.business_phone = request.POST.get('business_phone', guest.business_phone)
        guest.emergency_contact_name = request.POST.get('emergency_contact_name', guest.emergency_contact_name)
        guest.emergency_contact_phone = request.POST.get('emergency_contact_phone', guest.emergency_contact_phone)
        guest.emergency_contact_relationship = request.POST.get('emergency_contact_relationship', guest.emergency_contact_relationship)
        
        # Handle file upload
        id_picture = request.FILES.get('id_picture')
        if id_picture:
            guest.id_picture = id_picture
        
        # Check if email already exists (excluding current guest)
        new_email = guest.email
        if new_email and Guest.objects.filter(email=new_email).exclude(pk=guest.pk).exists():
            messages.error(request, 'A guest with this email already exists.')
            return render(request, 'guests/guest_form.html', {
                'guest': guest,
                'title': 'Edit Guest'
            })
        
        try:
            guest.save()
            messages.success(request, f'Guest {guest.full_name} updated successfully.')
            return redirect('guest_list')
        except Exception as e:
            messages.error(request, f'Error updating guest: {str(e)}')
    
    return render(request, 'guests/guest_form.html', {
        'guest': guest,
        'title': 'Edit Guest'
    })


@receptionist_required
def guest_delete(request, pk):
    """Delete guest with validation"""
    guest = get_object_or_404(Guest, pk=pk)
    
    # Check if guest has active bookings
    active_bookings = guest.bookings.filter(status__in=['confirmed', 'active'])
    if active_bookings.exists():
        messages.error(request, f'Cannot delete guest {guest.full_name}. They have active bookings.')
        return redirect('guest_list')
    
    if request.method == 'POST':
        name = guest.full_name
        guest.delete()
        messages.success(request, f'Guest {name} deleted successfully.')
        return redirect('guest_list')
    
    return render(request, 'guests/guest_confirm_delete.html', {'guest': guest})


@receptionist_required
def guest_preferences(request, pk):
    """Manage guest preferences"""
    guest = get_object_or_404(Guest, pk=pk)
    
    if request.method == 'POST':
        # Get or create preferences
        preferences, created = GuestPreference.objects.get_or_create(guest=guest)
        
        # Update preferences
        preferences.preferred_floor = request.POST.get('preferred_floor') or None
        preferences.preferred_room_type_id = request.POST.get('preferred_room_type') or None
        preferences.smoking_preference = request.POST.get('smoking_preference') == 'on'
        preferences.accessibility_requirements = request.POST.get('accessibility_requirements', '')
        preferences.housekeeping_frequency = request.POST.get('housekeeping_frequency', 'daily')
        preferences.preferred_language = request.POST.get('preferred_language', 'English')
        preferences.communication_method = request.POST.get('communication_method', 'email')
        preferences.special_notes = request.POST.get('special_notes', '')
        
        preferences.save()
        messages.success(request, f'Preferences updated for {guest.full_name}.')
        return redirect('guest_detail', pk=pk)
    
    # Get room types for preferences
    from apps.rooms.models import RoomType
    room_types = RoomType.objects.filter(is_active=True)
    
    try:
        preferences = guest.preferences
    except GuestPreference.DoesNotExist:
        preferences = None
    
    return render(request, 'guests/guest_preferences.html', {
        'guest': guest,
        'preferences': preferences,
        'room_types': room_types,
    })


@receptionist_required
def guest_documents(request, pk):
    """Manage guest documents"""
    guest = get_object_or_404(Guest, pk=pk)
    
    if request.method == 'POST':
        document_type = request.POST.get('document_type')
        document_number = request.POST.get('document_number')
        issuing_country = request.POST.get('issuing_country')
        issue_date = request.POST.get('issue_date')
        expiry_date = request.POST.get('expiry_date')
        notes = request.POST.get('notes')
        
        if document_type and document_number:
            document = GuestDocument.objects.create(
                guest=guest,
                document_type=document_type,
                document_number=document_number,
                issuing_country=issuing_country,
                issue_date=issue_date if issue_date else None,
                expiry_date=expiry_date if expiry_date else None,
                notes=notes,
            )
            messages.success(request, f'Document added for {guest.full_name}.')
            return redirect('guest_detail', pk=pk)
    
    documents = guest.documents.all().order_by('-created_at')
    return render(request, 'guests/guest_documents.html', {
        'guest': guest,
        'documents': documents,
    })


@receptionist_required
def guest_search(request):
    """Advanced guest search"""
    query = request.GET.get('q', '')
    search_type = request.GET.get('search_type', 'name')
    
    if query:
        if search_type == 'name':
            guests = Guest.objects.filter(
                Q(first_name__icontains=query) | Q(last_name__icontains=query)
            )
        elif search_type == 'email':
            guests = Guest.objects.filter(email__icontains=query)
        elif search_type == 'phone':
            guests = Guest.objects.filter(phone__icontains=query)
        elif search_type == 'passport':
            guests = Guest.objects.filter(passport_number__icontains=query)
        else:
            guests = Guest.objects.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query) |
                Q(phone__icontains=query)
            )
    else:
        guests = Guest.objects.none()
    
    return render(request, 'guests/guest_search.html', {
        'guests': guests,
        'query': query,
        'search_type': search_type,
    })


@receptionist_required
def guest_history(request):
    """View historical records for guests, including deleted entries"""
    # Base historical queryset ordered by most recent first
    history_qs = Guest.history.all().order_by('-history_date')

    # Filters
    search = request.GET.get('search', '').strip()
    event = request.GET.get('event', '').strip()  # created | updated | deleted

    if search:
        history_qs = history_qs.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )

    if event in ['created', 'updated', 'deleted']:
        event_map = {'created': '+', 'updated': '~', 'deleted': '-'}
        history_qs = history_qs.filter(history_type=event_map[event])

    # Build live guest stats map for quick access in template
    live_guests = Guest.objects.all().only('id', 'first_name', 'last_name')
    guest_stats = {}
    # Precompute booking stats
    from apps.bookings.models import Booking
    stays = Booking.objects.values('guest_id').annotate(
        total_bookings=Count('id'),
        completed_bookings=Count('id', filter=Q(status='completed')),
    )
    stays_map = {s['guest_id']: s for s in stays}
    for g in live_guests:
        s = stays_map.get(g.id, {'total_bookings': 0, 'completed_bookings': 0})
        guest_stats[g.id] = {
            'name': g.full_name,
            'total_bookings': s['total_bookings'],
            'completed_bookings': s['completed_bookings'],
        }

    # Pagination
    paginator = Paginator(history_qs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search': search,
        'event': event,
        'guest_stats': guest_stats,
    }
    return render(request, 'guests/guest_history.html', context)


@receptionist_required
def guest_history_export(request):
    """Export the currently filtered and paginated guest history page as CSV."""
    # Base historical queryset ordered by most recent first
    history_qs = Guest.history.all().order_by('-history_date')

    # Same filters as the HTML view
    search = request.GET.get('search', '').strip()
    event = request.GET.get('event', '').strip()  # created | updated | deleted
    page_number = request.GET.get('page')

    if search:
        history_qs = history_qs.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )

    if event in ['created', 'updated', 'deleted']:
        event_map = {'created': '+', 'updated': '~', 'deleted': '-'}
        history_qs = history_qs.filter(history_type=event_map[event])

    # Paginate to the specific page like the HTML view
    paginator = Paginator(history_qs, 25)
    page_obj = paginator.get_page(page_number)

    # Prepare CSV response
    response = HttpResponse(content_type='text/csv')
    filename = f"guest_history_page_{page_obj.number or 1}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(['When', 'Event', 'Guest ID', 'First Name', 'Last Name', 'Email', 'Phone', 'By'])

    for h in page_obj:
        if h.history_type == '+':
            event_label = 'Created'
        elif h.history_type == '~':
            event_label = 'Updated'
        elif h.history_type == '-':
            event_label = 'Deleted'
        else:
            event_label = '—'
        writer.writerow([
            h.history_date.strftime('%Y-%m-%d %H:%M:%S'),
            event_label,
            getattr(h, 'id', ''),
            h.first_name,
            h.last_name,
            h.email,
            h.phone,
            getattr(h, 'history_user', None) or 'System'
        ])

    return response
