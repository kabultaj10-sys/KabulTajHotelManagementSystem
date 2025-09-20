from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.users.decorators import receptionist_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.http import HttpResponse
from datetime import datetime, timedelta
from decimal import Decimal
import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from .models import Invoice, Payment
from apps.bookings.models import Booking
from apps.restaurant.models import Order
from apps.conference.models import ConferenceBooking


@receptionist_required
def billing_dashboard(request):
    """Enhanced billing dashboard with real revenue tracking"""
    
    # Get time filter from request
    time_filter = request.GET.get('time_filter', 'month')
    
    # Calculate date ranges
    today = timezone.now().date()
    
    if time_filter == 'today':
        start_date = today
        end_date = today
        period_name = 'Today'
    elif time_filter == 'week':
        start_date = today - timedelta(days=7)
        end_date = today
        period_name = 'Last 7 Days'
    elif time_filter == 'month':
        start_date = today - timedelta(days=30)
        end_date = today
        period_name = 'Last 30 Days'
    elif time_filter == 'quarter':
        start_date = today - timedelta(days=90)
        end_date = today
        period_name = 'Last 90 Days'
    elif time_filter == 'year':
        start_date = today - timedelta(days=365)
        end_date = today
        period_name = 'Last Year'
    else:
        # Custom date range
        try:
            start_date = datetime.strptime(request.GET.get('start_date', ''), '%Y-%m-%d').date()
            end_date = datetime.strptime(request.GET.get('end_date', ''), '%Y-%m-%d').date()
            period_name = f'Custom Range ({start_date} to {end_date})'
        except:
            start_date = today - timedelta(days=30)
            end_date = today
            period_name = 'Last 30 Days'
    
    # Get real revenue data from database
    # Invoice revenue
    invoice_revenue = Invoice.objects.filter(
        created_at__date__range=[start_date, end_date],
        status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    # Room booking revenue - only count bookings that have been paid
    room_revenue = Booking.objects.filter(
        created_at__date__range=[start_date, end_date],
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    # Restaurant revenue - only count orders that have been paid
    restaurant_revenue = Order.objects.filter(
        created_at__date__range=[start_date, end_date],
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    # Conference revenue - only count paid conference bookings
    conference_revenue = ConferenceBooking.objects.filter(
        created_at__date__range=[start_date, end_date],
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    # Other Services revenue - paid invoices of specific types
    other_services_revenue = Invoice.objects.filter(
        created_at__date__range=[start_date, end_date],
        status='paid',
        invoice_type__in=['custom', 'gym', 'swimming_pool']
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    # Total revenue (sum of four categories)
    total_revenue = room_revenue + restaurant_revenue + conference_revenue + other_services_revenue
    
    # Invoice statistics
    invoice_count = Invoice.objects.filter(created_at__date__range=[start_date, end_date]).count()
    paid_invoices = Invoice.objects.filter(
        created_at__date__range=[start_date, end_date],
        status='paid'
    ).count()
    pending_invoices = Invoice.objects.filter(
        created_at__date__range=[start_date, end_date],
        status__in=['draft', 'sent']
    ).count()
    
    # Calculate average invoice
    average_invoice = total_revenue / invoice_count if invoice_count > 0 else Decimal('0.00')
    
    # Calculate growth rate (compare with previous period using same categories)
    previous_start = start_date - (end_date - start_date)
    prev_room = Booking.objects.filter(
        created_at__date__range=[previous_start, start_date],
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    prev_restaurant = Order.objects.filter(
        created_at__date__range=[previous_start, start_date],
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    prev_conference = ConferenceBooking.objects.filter(
        created_at__date__range=[previous_start, start_date],
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    prev_other = Invoice.objects.filter(
        created_at__date__range=[previous_start, start_date],
        status='paid',
        invoice_type__in=['custom', 'gym', 'swimming_pool']
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    previous_revenue = prev_room + prev_restaurant + prev_conference + prev_other

    growth_rate = 0
    if previous_revenue > 0:
        growth_rate = ((total_revenue - previous_revenue) / previous_revenue) * 100
    
    revenue_data = {
        'total_revenue': total_revenue,
        'room_revenue': room_revenue,
        'restaurant_revenue': restaurant_revenue,
        'conference_revenue': conference_revenue,
        'invoice_count': invoice_count,
        'paid_invoices': paid_invoices,
        'pending_invoices': pending_invoices,
        'average_invoice': average_invoice,
        'growth_rate': round(growth_rate, 1),
    }
    
    # Revenue breakdown by service type
    service_breakdown = []
    if total_revenue > 0:
        service_breakdown = [
            {
                'service': 'Room Bookings', 
                'amount': room_revenue, 
                'percentage': round((room_revenue / total_revenue) * 100, 1)
            },
            {
                'service': 'Restaurant', 
                'amount': restaurant_revenue, 
                'percentage': round((restaurant_revenue / total_revenue) * 100, 1)
            },
            {
                'service': 'Conference', 
                'amount': conference_revenue, 
                'percentage': round((conference_revenue / total_revenue) * 100, 1)
            },
            {
                'service': 'Other Services', 
                'amount': other_services_revenue, 
                'percentage': round(((other_services_revenue) / total_revenue) * 100, 1)
            },
        ]
    
    # Recent transactions from invoices
    recent_transactions = Invoice.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).select_related().order_by('-created_at')[:10]
    
    # Convert to template format
    transactions_data = []
    for invoice in recent_transactions:
        transactions_data.append({
            'id': invoice.invoice_number,
            'customer': invoice.customer_name,
            'customer_email': invoice.customer_email,
            'service': invoice.get_invoice_type_display(),
            'amount': invoice.total_amount,
            'status': invoice.status,
            'date': invoice.created_at.strftime('%Y-%m-%d')
        })
    
    # Revenue trend data (last 12 months) - includes all income sources
    revenue_trend = []
    for i in range(12):
        month_start = today.replace(day=1) - timedelta(days=30*i)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        # Calculate total revenue from all sources for this month
        # Room booking revenue
        month_room_revenue = Booking.objects.filter(
            created_at__date__range=[month_start, month_end],
            payment_status='paid'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        # Restaurant revenue
        month_restaurant_revenue = Order.objects.filter(
            created_at__date__range=[month_start, month_end],
            payment_status='paid'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        # Conference revenue
        month_conference_revenue = ConferenceBooking.objects.filter(
            created_at__date__range=[month_start, month_end],
            payment_status='paid'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        # Other Services revenue (custom invoices)
        month_other_services_revenue = Invoice.objects.filter(
            created_at__date__range=[month_start, month_end],
            status='paid',
            invoice_type__in=['custom', 'gym', 'swimming_pool']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        # Total revenue for this month
        month_total_revenue = (month_room_revenue + month_restaurant_revenue + 
                             month_conference_revenue + month_other_services_revenue)
        
        revenue_trend.append({
            'month': month_start.strftime('%b'),
            'revenue': float(month_total_revenue)
        })
    
    revenue_trend.reverse()  # Show oldest to newest
    
    context = {
        'period_name': period_name,
        'time_filter': time_filter,
        'start_date': start_date,
        'end_date': end_date,
        'revenue_data': revenue_data,
        'service_breakdown': service_breakdown,
        'recent_transactions': transactions_data,
        'revenue_trend': json.dumps(revenue_trend),
    }
    
    return render(request, 'billing/dashboard.html', context)


@receptionist_required
def invoice_list(request):
    """List all invoices with real data"""
    invoices = Invoice.objects.all().order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        invoices = invoices.filter(
            Q(customer_name__icontains=search_query) |
            Q(invoice_number__icontains=search_query) |
            Q(customer_email__icontains=search_query)
        )
    
    context = {
        'invoices': invoices,
        'total_invoices': invoices.count(),
        'paid_invoices': invoices.filter(status='paid').count(),
        'pending_invoices': invoices.filter(status__in=['draft', 'sent']).count(),
        'overdue_invoices': invoices.filter(status='overdue').count(),
    }
    
    return render(request, 'billing/invoice_list.html', context)


@receptionist_required
def invoice_create(request):
    """Create a new invoice"""
    # Prepare selectable sources
    bookings = (
        Booking.objects
        .filter(status__in=['pending', 'confirmed', 'active', 'completed'])
        .exclude(payment_status='paid')
        .select_related('guest', 'room', 'room__room_type')
        .order_by('-created_at')
    )
    from apps.restaurant.models import Order
    # Filter orders by type based on GET preselect (front-end JS toggles visibility only)
    order_qs = Order.objects.filter(status__in=['served', 'billed'], payment_status__in=['pending']).select_related('guest', 'room').order_by('-created_at')
    filter_type = request.GET.get('type')
    if filter_type == 'gym':
        order_qs = order_qs.filter(special_instructions__icontains='gym')
    elif filter_type == 'swimming_pool':
        order_qs = order_qs.filter(special_instructions__icontains='swimming')
    elif filter_type == 'booking':
        # booking invoice orders; we keep all, UI will show
        pass
    orders = order_qs
    
    # Get conference bookings for conference invoice type
    conference_bookings = (
        ConferenceBooking.objects
        .filter(status__in=['confirmed', 'pending'])
        .exclude(payment_status='paid')
        .select_related('room')
        .order_by('-start_datetime')
    )
    
    if request.method == 'POST':
        try:
            # Generate unique invoice number
            import uuid
            invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
            
            # Get form data
            customer_name = request.POST.get('customer_name')
            customer_email = request.POST.get('customer_email', '')
            invoice_type = request.POST.get('invoice_type')
            total_amount = request.POST.get('total_amount')
            due_date = request.POST.get('due_date')
            status = request.POST.get('status', 'draft')
            description = request.POST.get('description', '')
            # Support both current and legacy field names from the form
            booking_id = request.POST.get('booking_id') or request.POST.get('order_id')
            order_id = request.POST.get('order_id')
            conference_booking_id = request.POST.get('conference_booking_id')
            
            # Prepare booking/order/conference based on invoice type
            booking = None
            order = None
            conference_booking = None

            if invoice_type == 'booking':
                # For booking invoices, derive fields from booking and remaining balance
                if not booking_id:
                    messages.error(request, 'Please select a booking for Booking Invoice.')
                    return render(request, 'billing/invoice_form.html', {
                        'invoice': request.POST,
                        'bookings': bookings,
                        'orders': orders,
                    })
                try:
                    booking = Booking.objects.select_related('guest', 'room').get(id=booking_id)
                except Booking.DoesNotExist:
                    messages.error(request, 'Selected booking not found.')
                    return render(request, 'billing/invoice_form.html', {
                        'invoice': request.POST,
                        'bookings': bookings,
                        'orders': orders,
                    })

                # Compute remaining balance using BookingPayment records
                total_paid = booking.payments.filter(status='completed').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                remaining_due = booking.total_amount - total_paid
                if remaining_due <= 0:
                    messages.error(request, 'This booking is already fully paid.')
                    return render(request, 'billing/invoice_form.html', {
                        'invoice': request.POST,
                        'bookings': bookings,
                        'orders': orders,
                    })

                # Override fields from booking
                customer_name = booking.guest.full_name
                customer_email = booking.guest.email or ''
                total_amount = str(remaining_due)
                # Set due date to booking check-out if not provided
                if not due_date:
                    due_date = booking.check_out_date.strftime('%Y-%m-%d') if booking.check_out_date else ''
                # Default status for generated booking invoice
                status = 'sent'

            elif invoice_type == 'conference':
                # For conference invoices, derive fields from conference booking and remaining balance
                if not conference_booking_id:
                    messages.error(request, 'Please select a conference booking for Conference Invoice.')
                    return render(request, 'billing/invoice_form.html', {
                        'invoice': request.POST,
                        'bookings': bookings,
                        'orders': orders,
                        'conference_bookings': conference_bookings,
                    })
                try:
                    conference_booking = ConferenceBooking.objects.select_related('room').get(id=conference_booking_id)
                except ConferenceBooking.DoesNotExist:
                    messages.error(request, 'Selected conference booking not found.')
                    return render(request, 'billing/invoice_form.html', {
                        'invoice': request.POST,
                        'bookings': bookings,
                        'orders': orders,
                        'conference_bookings': conference_bookings,
                    })

                # Compute remaining balance using ConferenceBookingPayment records if they exist
                # For now, assume full amount is due if not fully paid
                total_paid = conference_booking.paid_amount
                remaining_due = conference_booking.total_amount - total_paid
                if remaining_due <= 0:
                    messages.error(request, 'This conference booking is already fully paid.')
                    return render(request, 'billing/invoice_form.html', {
                        'invoice': request.POST,
                        'bookings': bookings,
                        'orders': orders,
                        'conference_bookings': conference_bookings,
                    })

                # Override fields from conference booking
                customer_name = conference_booking.client_name
                customer_email = conference_booking.client_email
                total_amount = str(remaining_due)
                # Set due date to conference end date if not provided
                if not due_date:
                    due_date = conference_booking.end_datetime.date().strftime('%Y-%m-%d')
                # Default status for generated conference invoice
                status = 'sent'

            # Validate required fields (skip customer and total for booking/conference types as we derived them)
            if not invoice_type:
                messages.error(request, 'Invoice type is required.')
                return render(request, 'billing/invoice_form.html', {
                    'invoice': request.POST,
                    'bookings': bookings,
                    'orders': orders,
                })
            if invoice_type not in ['booking', 'conference'] and (not customer_name or not total_amount):
                messages.error(request, 'Please fill in all required fields.')
                return render(request, 'billing/invoice_form.html', {
                    'invoice': request.POST,
                    'bookings': bookings,
                    'orders': orders,
                    'conference_bookings': conference_bookings,
                })
            
            # Validate invoice type
            valid_types = [choice[0] for choice in Invoice.INVOICE_TYPES]
            if invoice_type not in valid_types:
                messages.error(request, 'Invalid invoice type selected.')
                return render(request, 'billing/invoice_form.html', {
                    'invoice': request.POST,
                    'bookings': bookings
                })
            
            # Validate status
            valid_statuses = [choice[0] for choice in Invoice.STATUS_CHOICES]
            if status not in valid_statuses:
                status = 'draft'  # Default to draft if invalid status
            
            # Convert total_amount to Decimal (using module-level import)
            try:
                total_amount = Decimal(total_amount)
            except (ValueError, TypeError):
                messages.error(request, 'Invalid total amount.')
                return render(request, 'billing/invoice_form.html', {
                    'invoice': request.POST,
                    'bookings': bookings
                })
            
            # Parse due date
            from datetime import datetime
            if due_date:
                try:
                    due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
                except ValueError:
                    due_date = None
            
            # Get order for gym/swimming invoices
            if invoice_type in ['gym', 'swimming_pool'] and order_id:
                try:
                    order = Order.objects.get(id=order_id)
                except Order.DoesNotExist:
                    messages.error(request, 'Selected order not found.')
                    return render(request, 'billing/invoice_form.html', {
                        'invoice': request.POST,
                        'bookings': bookings,
                        'orders': orders
                    })
            
            # Create the invoice
            invoice = Invoice.objects.create(
                invoice_number=invoice_number,
                customer_name=customer_name,
                customer_email=customer_email,
                invoice_type=invoice_type,
                booking=booking,
                order=order,
                conference_booking=conference_booking,
                total_amount=total_amount,
                subtotal=total_amount,  # For now, subtotal equals total_amount
                due_date=due_date or (timezone.now().date() + timedelta(days=30)),
                status=status,
                notes=description,
                created_by=request.user,
            )
            
            messages.success(request, f'Invoice {invoice_number} created successfully.')
            return redirect('invoice_list')
            
        except Exception as e:
            messages.error(request, f'Error creating invoice: {str(e)}')
            return render(request, 'billing/invoice_form.html', {
                'invoice': request.POST,
                'bookings': bookings,
                'orders': orders
            })
    
    return render(request, 'billing/invoice_form.html', {
        'bookings': bookings, 
        'orders': orders, 
        'conference_bookings': conference_bookings
    })


@receptionist_required
def payment_list(request):
    """List all payments with real data"""
    payments = Payment.objects.select_related('invoice').all().order_by('-payment_date')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        payments = payments.filter(payment_status=status_filter)
    
    # Filter by payment method if provided
    method_filter = request.GET.get('method')
    if method_filter:
        payments = payments.filter(payment_method=method_filter)
    
    context = {
        'payments': payments,
        'total_payments': payments.count(),
        'completed_payments': payments.filter(payment_status='completed').count(),
        'pending_payments': payments.filter(payment_status='pending').count(),
        'total_amount': payments.filter(payment_status='completed').aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
    }
    
    return render(request, 'billing/payment_list.html', context)


@receptionist_required
def invoice_detail(request, pk):
    """View invoice details"""
    try:
        invoice = Invoice.objects.get(pk=pk)
    except Invoice.DoesNotExist:
        messages.error(request, 'Invoice not found.')
        return redirect('invoice_list')
    
    context = {
        'invoice': invoice,
    }
    return render(request, 'billing/invoice_detail.html', context)


@receptionist_required
def invoice_edit(request, pk):
    """Edit an existing invoice"""
    try:
        invoice = Invoice.objects.get(pk=pk)
    except Invoice.DoesNotExist:
        messages.error(request, 'Invoice not found.')
        return redirect('invoice_list')
    
    if request.method == 'POST':
        try:
            # Update invoice fields
            invoice.customer_name = request.POST.get('customer_name')
            invoice.customer_email = request.POST.get('customer_email', '')
            invoice.invoice_type = request.POST.get('invoice_type')
            invoice.total_amount = Decimal(request.POST.get('total_amount'))
            invoice.subtotal = invoice.total_amount  # For now, subtotal equals total_amount
            
            # Parse due date
            due_date = request.POST.get('due_date')
            if due_date:
                try:
                    invoice.due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
                except ValueError:
                    pass  # Keep existing due date if invalid
            
            invoice.status = request.POST.get('status', 'draft')
            invoice.notes = request.POST.get('description', '')
            invoice.save()
            
            messages.success(request, f'Invoice {invoice.invoice_number} updated successfully.')
            return redirect('invoice_list')
            
        except Exception as e:
            messages.error(request, f'Error updating invoice: {str(e)}')
    
    context = {
        'invoice': invoice,
        'title': 'Edit Invoice'
    }
    return render(request, 'billing/invoice_form.html', context)


@receptionist_required
def invoice_print(request, pk):
    """Generate and download PDF invoice"""
    try:
        invoice = Invoice.objects.get(pk=pk)
    except Invoice.DoesNotExist:
        messages.error(request, 'Invoice not found.')
        return redirect('invoice_list')
    
    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{invoice.invoice_number}.pdf"'
    
    # Create PDF document with better margins
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles optimized for single page
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=5,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#D4AF37'),
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#666666'),
        fontName='Helvetica'
    )
    
    section_heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=10,
        spaceAfter=4,
        spaceBefore=8,
        textColor=colors.HexColor('#333333'),
        fontName='Helvetica-Bold',
        borderWidth=1,
        borderColor=colors.HexColor('#D4AF37'),
        borderPadding=3,
        backColor=colors.HexColor('#F8F8F8')
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=2,
        fontName='Helvetica'
    )
    
    bold_style = ParagraphStyle(
        'BoldStyle',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=2,
        fontName='Helvetica-Bold'
    )
    
    # Build PDF content
    story = []
    
    # Header Section - Company name and title
    header_data = [
        ['KABUL TAJ HOTEL', ''],
        ['Hotels Invoice', ''],
        ['', ''],
        ['', 'Kabul, Afghanistan'],
        ['', 'Hotel Management System'],
        ['', 'Afghanistan']
    ]
    
    header_table = Table(header_data, colWidths=[3.5*inch, 2.5*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (0, 0), 18),
        ('FONTSIZE', (0, 1), (0, 1), 12),
        ('FONTSIZE', (1, 0), (1, -1), 9),
        ('FONTNAME', (0, 0), (0, 1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    story.append(header_table)
    story.append(Spacer(1, 15))
    
    # Separator line
    story.append(Table([['']], colWidths=[6*inch]))
    story.append(Spacer(1, 10))
    
    # Invoice Details Section
    invoice_details_data = [
        ['INVOICE', ''],
        ['Invoice Number:', invoice.invoice_number],
        ['Invoice Date:', invoice.created_at.strftime('%b %d, %Y')],
        ['Due Date:', invoice.due_date.strftime('%b %d, %Y') if invoice.due_date else 'N/A'],
        ['Status:', invoice.get_status_display()],
        ['Balance Due:', f'${invoice.remaining_amount}'],
        ['', ''],
        ['', invoice.customer_name],
        ['', invoice.customer_email if invoice.customer_email else '']
    ]
    
    invoice_details_table = Table(invoice_details_data, colWidths=[3*inch, 3*inch])
    invoice_details_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (0, 0), 14),
        ('FONTSIZE', (0, 1), (0, 3), 9),
        ('FONTSIZE', (1, 0), (1, -1), 9),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, 3), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (0, 0), colors.HexColor('#D4AF37')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    story.append(invoice_details_table)
    story.append(Spacer(1, 10))
    
    # Separator line
    story.append(Table([['']], colWidths=[6*inch]))
    story.append(Spacer(1, 10))
    
    # Services Table (include booking/order specifics)
    services_data = [
        ['Item', 'Description', 'Unit Cost', 'Quantity', 'Line Total']
    ]
    
    # Add service item
    service_description = f"{invoice.get_invoice_type_display()} Service"
    if invoice.booking:
        service_description += f" - Room {invoice.booking.room.room_number}"
        if invoice.booking.duration > 1:
            service_description += f" ({invoice.booking.duration} days)"
    elif invoice.order:
        service_description += f" - Order {invoice.order.order_number}"
    
    services_data.append([
        invoice.get_invoice_type_display(),
        service_description,
        f'${invoice.total_amount}',
        '1',
        f'${invoice.total_amount}'
    ])
    
    services_table = Table(services_data, colWidths=[1*inch, 2.5*inch, 1*inch, 0.8*inch, 1*inch])
    services_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, 1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 1), (0, 1), colors.HexColor('#D4AF37')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, 1), (-1, 1), 1, colors.black),
    ]))
    
    story.append(services_table)
    story.append(Spacer(1, 10))
    
    # Separator line
    story.append(Table([['']], colWidths=[6*inch]))
    story.append(Spacer(1, 10))
    
    # Payment History Section (always shown)
    story.append(Paragraph("PAYMENT HISTORY", section_heading_style))
    payments = Payment.objects.filter(invoice=invoice).order_by('-payment_date')
    payment_data = [['Date', 'Amount', 'Method', 'Status']]
    if payments.exists():
        for payment in payments:
            payment_data.append([
                payment.payment_date.strftime('%B %d, %Y'),
                f'${payment.amount}',
                payment.get_payment_method_display(),
                payment.get_payment_status_display()
            ])
    else:
        payment_data.append(['No payments recorded', '-', '-', '-'])

    payment_table = Table(payment_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 1*inch])
    payment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D4AF37')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FAFAFA'))
    ]))

    story.append(payment_table)
    story.append(Spacer(1, 10))

    # Footer Section with totals (retain subtotal/paid/remaining)
    footer_data = [
        ['Thanks for your business!', ''],
        ['', ''],
        ['', 'Subtotal:'],
        ['', f'${invoice.total_amount}'],
        ['', 'Paid To Date:'],
        ['', f'${invoice.paid_amount}'],
        ['', 'Balance Due:'],
        ['', f'${invoice.remaining_amount}']
    ]
    
    footer_table = Table(footer_data, colWidths=[3*inch, 3*inch])
    footer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (0, 0), 9),
        ('FONTSIZE', (1, 0), (1, -1), 9),
        ('FONTNAME', (1, 2), (1, 2), 'Helvetica-Bold'),
        ('FONTNAME', (1, 4), (1, 4), 'Helvetica-Bold'),
        ('FONTNAME', (1, 6), (1, 6), 'Helvetica-Bold'),
        ('FONTNAME', (1, 7), (1, 7), 'Helvetica-Bold'),
        ('TEXTCOLOR', (1, 7), (1, 7), colors.HexColor('#D4AF37')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    story.append(footer_table)
    
    # Build PDF
    doc.build(story)
    
    return response


@receptionist_required
def invoice_delete(request, pk):
    """Delete an invoice"""
    try:
        invoice = Invoice.objects.get(pk=pk)
    except Invoice.DoesNotExist:
        messages.error(request, 'Invoice not found.')
        return redirect('invoice_list')
    
    if request.method == 'POST':
        try:
            invoice_number = invoice.invoice_number
            invoice.delete()
            messages.success(request, f'Invoice {invoice_number} deleted successfully.')
            return redirect('invoice_list')
        except Exception as e:
            messages.error(request, f'Error deleting invoice: {str(e)}')
    
    context = {
        'invoice': invoice,
    }
    return render(request, 'billing/invoice_confirm_delete.html', context)


@receptionist_required
def payment_complete(request, pk):
    """Complete payment and handle guest/order deletion if full payment"""
    try:
        invoice = Invoice.objects.get(pk=pk)
    except Invoice.DoesNotExist:
        messages.error(request, 'Invoice not found.')
        return redirect('invoice_list')
    
    if request.method == 'POST':
        payment_amount = request.POST.get('payment_amount')
        payment_method = request.POST.get('payment_method')
        
        if not payment_amount or not payment_method:
            messages.error(request, 'Please provide payment amount and method.')
            return redirect('invoice_detail', pk=invoice.pk)
        
        try:
            payment_amount = Decimal(payment_amount)
            
            # Create payment record
            payment = Payment.objects.create(
                invoice=invoice,
                amount=payment_amount,
                payment_method=payment_method,
                payment_status='completed',
                processed_by=request.user,
                notes=f'Payment completed via {payment_method}'
            )
            
            # Update invoice paid amount
            invoice.paid_amount += payment_amount
            invoice.save()
            
            # Mirror payment to booking payments if this invoice is tied to a booking
            try:
                if invoice.booking:
                    from apps.bookings.models import BookingPayment
                    booking = invoice.booking
                    booking_payment = BookingPayment.objects.create(
                        booking=booking,
                        amount=payment_amount,
                        payment_method=payment_method,
                        status='completed',
                        processed_by=request.user,
                        notes=f'Linked to invoice {invoice.invoice_number}'
                    )

                    # Recompute booking payment status
                    total_paid = booking.payments.filter(status='completed').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                    if total_paid >= booking.total_amount:
                        booking.payment_status = 'paid'
                    elif total_paid > 0:
                        booking.payment_status = 'partial'
                    else:
                        booking.payment_status = 'pending'
                    booking.save()
            except Exception:
                # Non-fatal; continue payment flow
                pass
            
            # Check if payment is full
            if invoice.paid_amount >= invoice.total_amount:
                invoice.status = 'paid'
                invoice.save()
                
                # If this is a booking guest invoice, handle guest and order deletion
                if invoice.invoice_type == 'booking_guest' and invoice.booking:
                    booking = invoice.booking
                    guest = booking.guest
                    
                    # Delete the booking first
                    booking.delete()
                    
                    # Delete any restaurant orders linked to this guest
                    try:
                        Order.objects.filter(guest=guest).delete()
                    except Exception:
                        # Best-effort cleanup; continue even if orders deletion fails
                        pass
                    
                    # Check if guest has any other bookings before deleting the guest
                    remaining_bookings = Booking.objects.filter(guest=guest).count()
                    if remaining_bookings == 0:
                        guest.delete()
                        messages.success(request, f'Payment completed. Guest, related orders, and booking deleted as payment was full.')
                    else:
                        messages.success(request, f'Payment completed. Booking deleted; guest kept due to other bookings. Related orders removed.')
                # If this is a booking (restaurant order) invoice, delete order (and potentially guest)
                elif invoice.invoice_type in ['booking', 'gym', 'swimming_pool'] and invoice.order:
                    from apps.restaurant.models import Order as RestaurantOrder
                    order = invoice.order
                    linked_guest = order.guest
                    order_number = order.order_number
                    # Delete the order
                    try:
                        order.delete()
                    except Exception:
                        pass
                    # If order had a linked guest, consider deleting guest if no other bookings or orders
                    if linked_guest:
                        remaining_bookings = Booking.objects.filter(guest=linked_guest).count()
                        remaining_orders = RestaurantOrder.objects.filter(guest=linked_guest).count()
                        if remaining_bookings == 0 and remaining_orders == 0:
                            try:
                                linked_guest.delete()
                            except Exception:
                                pass
                            messages.success(request, f'Payment completed. Order {order_number} and guest removed (no remaining records).')
                        else:
                            messages.success(request, f'Payment completed. Order {order_number} removed; guest retained due to existing records.')
                else:
                    messages.success(request, f'Payment completed. Invoice marked as paid.')
            else:
                # Partial payment
                invoice.status = 'sent'  # Mark as sent for partial payment
                invoice.save()
                messages.success(request, f'Partial payment of ${payment_amount} recorded. Remaining balance: ${invoice.remaining_amount}')
            
            # On full payment, redirect to detail with a one-time download flag
            if invoice.status == 'paid':
                detail_url = reverse('invoice_detail', kwargs={'pk': invoice.pk})
                return redirect(f"{detail_url}?download=1")
            return redirect('invoice_detail', pk=invoice.pk)
            
        except (ValueError, TypeError) as e:
            messages.error(request, 'Invalid payment amount.')
            return redirect('invoice_detail', pk=invoice.pk)
        except Exception as e:
            messages.error(request, f'Error processing payment: {str(e)}')
            return redirect('invoice_detail', pk=invoice.pk)
    
    context = {
        'invoice': invoice,
    }
    return render(request, 'billing/payment_form.html', context)
