from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.users.decorators import restaurant_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import JsonResponse
from apps.restaurant.models import MenuItem, MenuCategory, Table, Order, OrderItem, Transaction
from apps.guests.models import Guest
from apps.rooms.models import Room
import json
from apps.restaurant.models import RestaurantInvoice, RestaurantInvoiceItem
from django.utils import timezone
from django.http import HttpResponse
from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm as mm_unit
from reportlab.lib import colors


@restaurant_required
def restaurant_dashboard(request):
    """Restaurant dashboard with key metrics"""
    # Get key statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='placed').count()
    active_tables = Table.objects.filter(status='occupied').count()
    
    # Calculate revenue from transactions instead of orders
    total_revenue = Transaction.objects.aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Recent orders
    recent_orders = Order.objects.select_related('table', 'guest', 'room').order_by('-created_at')[:5]
    
    # Recent transactions (for the new section)
    recent_transactions = Transaction.objects.select_related('order', 'invoice').order_by('-created_at')[:10]
    
    # Available tables (limit to 6)
    available_tables = Table.objects.filter(status='available', is_active=True)[:6]
    
    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'active_tables': active_tables,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'recent_transactions': recent_transactions,
        'available_tables': available_tables,
    }
    return render(request, 'restaurant/dashboard.html', context)


# Menu Items CRUD
@restaurant_required
def menu_list(request):
    """List all menu items with filtering"""
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    cuisine = request.GET.get('cuisine', '')
    availability = request.GET.get('availability', '')
    
    menu_items = MenuItem.objects.select_related('category').all()
    
    if search:
        menu_items = menu_items.filter(
            Q(name__icontains=search) | 
            Q(description__icontains=search) |
            Q(category__name__icontains=search)
        )
    
    if category:
        menu_items = menu_items.filter(category_id=category)
    
    if cuisine:
        menu_items = menu_items.filter(cuisine_type=cuisine)
    
    if availability:
        if availability == 'available':
            menu_items = menu_items.filter(is_available=True)
        elif availability == 'unavailable':
            menu_items = menu_items.filter(is_available=False)
    
    # Pagination
    paginator = Paginator(menu_items, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter
    categories = MenuCategory.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'category': category,
        'cuisine': cuisine,
        'availability': availability,
        'categories': categories,
        'cuisine_choices': MenuItem.CUISINE_CHOICES,
    }
    return render(request, 'restaurant/menu_list.html', context)


@restaurant_required
def menu_create(request):
    """Create a new menu item"""
    if request.method == 'POST':
        try:
            menu_item = MenuItem.objects.create(
                name=request.POST.get('name'),
                category_id=request.POST.get('category'),
                description=request.POST.get('description', ''),
                price=request.POST.get('price'),
                cuisine_type=request.POST.get('cuisine_type', 'local'),
                preparation_time=request.POST.get('preparation_time', 0),
                is_vegetarian=request.POST.get('is_vegetarian') == 'on',
                is_gluten_free=request.POST.get('is_gluten_free') == 'on',
                is_spicy=request.POST.get('is_spicy') == 'on',
                is_available=request.POST.get('is_available') == 'on',
            )
            
            # Handle image upload
            if request.FILES.get('image'):
                menu_item.image = request.FILES['image']
                menu_item.save()
            
            messages.success(request, f'Menu item "{menu_item.name}" created successfully.')
            return redirect('restaurant:menu_list')
        except Exception as e:
            messages.error(request, f'Error creating menu item: {str(e)}')
    
    categories = MenuCategory.objects.filter(is_active=True)
    context = {
        'categories': categories,
        'cuisine_choices': MenuItem.CUISINE_CHOICES,
        'title': 'Add Menu Item'
    }
    return render(request, 'restaurant/menu_form.html', context)


@restaurant_required
def menu_edit(request, pk):
    """Edit a menu item"""
    menu_item = get_object_or_404(MenuItem, pk=pk)
    
    if request.method == 'POST':
        try:
            menu_item.name = request.POST.get('name')
            menu_item.category_id = request.POST.get('category')
            menu_item.description = request.POST.get('description', '')
            menu_item.price = request.POST.get('price')
            menu_item.cuisine_type = request.POST.get('cuisine_type', 'local')
            menu_item.preparation_time = request.POST.get('preparation_time', 0)
            menu_item.is_vegetarian = request.POST.get('is_vegetarian') == 'on'
            menu_item.is_gluten_free = request.POST.get('is_gluten_free') == 'on'
            menu_item.is_spicy = request.POST.get('is_spicy') == 'on'
            menu_item.is_available = request.POST.get('is_available') == 'on'
            
            # Handle image upload
            if request.FILES.get('image'):
                menu_item.image = request.FILES['image']
            
            menu_item.save()
            messages.success(request, f'Menu item "{menu_item.name}" updated successfully.')
            return redirect('restaurant:menu_list')
        except Exception as e:
            messages.error(request, f'Error updating menu item: {str(e)}')
    
    categories = MenuCategory.objects.filter(is_active=True)
    context = {
        'menu_item': menu_item,
        'categories': categories,
        'cuisine_choices': MenuItem.CUISINE_CHOICES,
        'title': 'Edit Menu Item'
    }
    return render(request, 'restaurant/menu_form.html', context)


@restaurant_required
def menu_delete(request, pk):
    """Delete a menu item with proper validation and error handling"""
    menu_item = get_object_or_404(MenuItem, pk=pk)
    
    if request.method == 'POST':
        try:
            # Check if item is being used in active orders
            active_orders = OrderItem.objects.filter(
                menu_item=menu_item,
                order__status__in=['placed', 'preparing', 'ready', 'served']
            ).exists()
            
            if active_orders:
                messages.warning(
                    request, 
                    f'Menu item "{menu_item.name}" is currently being used in active orders. '
                    'Please complete or cancel those orders before deleting this item.'
                )
                return redirect('restaurant:menu_list')
            
            # Store name for success message
            item_name = menu_item.name
            
            # Delete the item
            menu_item.delete()
            
            messages.success(
                request, 
                f'Menu item "{item_name}" has been permanently deleted from the menu.'
            )
            return redirect('restaurant:menu_list')
            
        except Exception as e:
            messages.error(
                request, 
                f'Error deleting menu item "{menu_item.name}": {str(e)}. '
                'Please try again or contact support if the problem persists.'
            )
    
    # Get additional context for the confirmation page
    context = {
        'menu_item': menu_item,
        'active_orders_count': OrderItem.objects.filter(
            menu_item=menu_item,
            order__status__in=['placed', 'preparing', 'ready', 'served']
        ).count(),
        'total_orders_count': OrderItem.objects.filter(menu_item=menu_item).count(),
    }
    
    return render(request, 'restaurant/menu_confirm_delete.html', context)


# Table Management
@restaurant_required
def table_list(request):
    """List all tables with status and statistics"""
    # Get search and filter parameters
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    # Base queryset
    tables = Table.objects.all()
    
    # Apply search filter
    if search:
        tables = tables.filter(
            Q(table_number__icontains=search) |
            Q(location__icontains=search)
        )
    
    # Apply status filter
    if status_filter:
        tables = tables.filter(status=status_filter)
    
    # Order by table number
    tables = tables.order_by('table_number')
    
    # Calculate statistics
    total_tables = Table.objects.count()
    available_tables = Table.objects.filter(status='available').count()
    occupied_tables = Table.objects.filter(status='occupied').count()
    out_of_order_tables = Table.objects.filter(status='out_of_order').count()
    
    context = {
        'tables': tables,
        'status_choices': Table.STATUS_CHOICES,
        'total_tables': total_tables,
        'available_tables': available_tables,
        'occupied_tables': occupied_tables,
        'out_of_order_tables': out_of_order_tables,
    }
    return render(request, 'restaurant/table_list.html', context)


@restaurant_required
def table_create(request):
    """Create a new table"""
    if request.method == 'POST':
        try:
            table = Table.objects.create(
                table_number=request.POST.get('table_number'),
                capacity=request.POST.get('capacity'),
                location=request.POST.get('location', ''),
                status=request.POST.get('status', 'available'),
                is_active=request.POST.get('is_active') == 'on',
            )
            messages.success(request, f'Table {table.table_number} created successfully.')
            return redirect('restaurant:table_list')
        except Exception as e:
            messages.error(request, f'Error creating table: {str(e)}')
    
    context = {
        'status_choices': Table.STATUS_CHOICES,
        'title': 'Add Table'
    }
    return render(request, 'restaurant/table_form.html', context)


@restaurant_required
def table_edit(request, pk):
    """Edit a table"""
    table = get_object_or_404(Table, pk=pk)
    
    if request.method == 'POST':
        try:
            table.table_number = request.POST.get('table_number')
            table.capacity = request.POST.get('capacity')
            table.location = request.POST.get('location', '')
            table.status = request.POST.get('status', 'available')
            table.is_active = request.POST.get('is_active') == 'on'
            table.save()
            
            messages.success(request, f'Table {table.table_number} updated successfully.')
            return redirect('restaurant:table_list')
        except Exception as e:
            messages.error(request, f'Error updating table: {str(e)}')
    
    context = {
        'table': table,
        'status_choices': Table.STATUS_CHOICES,
        'title': 'Edit Table'
    }
    return render(request, 'restaurant/table_form.html', context)


@restaurant_required
def table_update_status(request, pk):
    """Update table status via AJAX"""
    if request.method == 'POST':
        table = get_object_or_404(Table, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in dict(Table.STATUS_CHOICES):
            table.status = new_status
            table.save()
            
            return JsonResponse({'success': True, 'status': new_status})
    
    return JsonResponse({'success': False})


# Order Management
@restaurant_required
def order_list(request):
    """List all orders with filtering"""
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    payment_status = request.GET.get('payment_status', '')
    guest_id = request.GET.get('guest_id', '')
    
    orders = Order.objects.select_related('table', 'guest', 'room').all()
    
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(guest_name__icontains=search) |
            Q(guest_phone__icontains=search)
        )
    
    if status:
        orders = orders.filter(status=status)
    
    if payment_status:
        orders = orders.filter(payment_status=payment_status)

    if guest_id:
        orders = orders.filter(guest_id=guest_id)
    
    # Calculate statistics
    total_orders = orders.count()
    pending_orders = orders.filter(status__in=['placed', 'preparing', 'ready']).count()
    completed_orders = orders.filter(status='served').count()
    # Only count revenue from orders that have been paid
    total_revenue = orders.filter(payment_status='paid').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Pagination
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'status': status,
        'payment_status': payment_status,
        'guest_id': guest_id,
        'status_choices': Order.STATUS_CHOICES,
        'payment_status_choices': Order.PAYMENT_STATUS_CHOICES,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'total_revenue': total_revenue,
    }
    return render(request, 'restaurant/order_list.html', context)


@restaurant_required
def order_create(request):
    """Create a new order"""
    if request.method == 'POST':
        try:
            # Get order data
            table_id = request.POST.get('table')
            guest_id = request.POST.get('guest') or None
            room_id = request.POST.get('room') or None
            guest_name = request.POST.get('guest_name')
            guest_phone = request.POST.get('guest_phone', '')
            special_instructions = request.POST.get('special_instructions', '')
            
            # Create order
            order = Order.objects.create(
                table_id=table_id,
                guest_id=guest_id,
                room_id=room_id,
                guest_name=guest_name,
                guest_phone=guest_phone,
                special_instructions=special_instructions,
                created_by=request.user,
            )
            
            # Add order items
            items_data = json.loads(request.POST.get('items', '[]'))
            total_amount = 0
            
            for item_data in items_data:
                menu_item = MenuItem.objects.get(id=item_data['menu_item_id'])
                quantity = int(item_data['quantity'])
                unit_price = menu_item.price
                
                OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=quantity,
                    unit_price=unit_price,
                    special_instructions=item_data.get('special_instructions', '')
                )
                
                total_amount += quantity * unit_price
            
            # Update order total
            order.total_amount = total_amount
            order.save()
            
            # Update table status
            table = order.table
            table.status = 'occupied'
            table.save()
            
            messages.success(request, f'Order {order.order_number} created successfully.')
            return redirect('restaurant:order_list')
        except Exception as e:
            messages.error(request, f'Error creating order: {str(e)}')
    
    # Get available data
    tables = Table.objects.filter(status='available', is_active=True)
    guests = Guest.objects.all().order_by('first_name', 'last_name')
    rooms = Room.objects.filter(status='available')
    menu_items = MenuItem.objects.filter(is_available=True).select_related('category')
    
    context = {
        'tables': tables,
        'guests': guests,
        'rooms': rooms,
        'menu_items': menu_items,
        'title': 'Create Order'
    }
    return render(request, 'restaurant/order_form.html', context)


@restaurant_required
def order_detail(request, pk):
    """View order details"""
    order = get_object_or_404(Order, pk=pk)
    
    context = {
        'order': order,
    }
    return render(request, 'restaurant/order_detail.html', context)


@restaurant_required
def order_edit(request, pk):
    """Edit an existing order"""
    order = get_object_or_404(Order, pk=pk)
    
    # Don't allow editing of completed orders
    if order.status in ['billed', 'cancelled']:
        messages.warning(request, 'Cannot edit completed or cancelled orders.')
        return redirect('restaurant:order_detail', pk=order.pk)
    
    if request.method == 'POST':
        try:
            # Update order basic information
            order.guest_name = request.POST.get('guest_name', order.guest_name)
            order.guest_phone = request.POST.get('guest_phone', order.guest_phone)
            order.special_instructions = request.POST.get('special_instructions', order.special_instructions)
            
            # Update table if changed
            new_table_id = request.POST.get('table')
            if new_table_id and new_table_id != str(order.table.id):
                old_table = order.table
                new_table = get_object_or_404(Table, pk=new_table_id)
                
                # Free up old table if no other orders
                if not old_table.orders.exclude(id=order.id).filter(status__in=['placed', 'preparing', 'ready', 'served']).exists():
                    old_table.status = 'available'
                    old_table.save()
                
                # Update order table
                order.table = new_table
                new_table.status = 'occupied'
                new_table.save()
            
            # Update order items
            items_data = json.loads(request.POST.get('items', '[]'))
            total_amount = 0
            
            # Clear existing items
            order.items.all().delete()
            
            # Add new items
            for item_data in items_data:
                menu_item = MenuItem.objects.get(id=item_data['menu_item_id'])
                quantity = int(item_data['quantity'])
                unit_price = menu_item.price
                
                OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=quantity,
                    unit_price=unit_price,
                    special_instructions=item_data.get('special_instructions', '')
                )
                
                total_amount += quantity * unit_price
            
            # Update order total
            order.total_amount = total_amount
            order.save()
            
            messages.success(request, f'Order {order.order_number} updated successfully.')
            return redirect('restaurant:order_detail', pk=order.pk)
            
        except Exception as e:
            messages.error(request, f'Error updating order: {str(e)}')
    
    # Get available data for editing
    tables = Table.objects.filter(is_active=True)
    menu_items = MenuItem.objects.filter(is_available=True).select_related('category')
    
    context = {
        'order': order,
        'tables': tables,
        'menu_items': menu_items,
        'title': 'Edit Order'
    }
    return render(request, 'restaurant/order_edit.html', context)


@restaurant_required
def order_update_status(request, pk):
    """Update order status via AJAX"""
    if request.method == 'POST':
        order = get_object_or_404(Order, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            
            # Update table status if order is completed or served
            if new_status in ['served', 'billed', 'cancelled']:
                table = order.table
                table.status = 'available'
                table.save()
            
            return JsonResponse({'success': True, 'status': new_status})
    
    return JsonResponse({'success': False})


@restaurant_required
def get_menu_items(request):
    """Get menu items for AJAX requests"""
    category_id = request.GET.get('category')
    menu_items = MenuItem.objects.filter(is_available=True)
    
    if category_id:
        menu_items = menu_items.filter(category_id=category_id)
    
    items_data = []
    for item in menu_items:
        items_data.append({
            'id': item.id,
            'name': item.name,
            'price': float(item.price),
            'description': item.description,
            'category': item.category.name,
        })
    
    return JsonResponse({'items': items_data})


@restaurant_required
def order_delete(request, pk):
    """Delete a single order with proper validation"""
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'POST':
        try:
            # Check if order can be deleted (only allow deletion of cancelled or billed orders)
            if order.status not in ['cancelled', 'billed']:
                messages.warning(
                    request, 
                    f'Order {order.order_number} cannot be deleted. Only cancelled or billed orders can be deleted.'
                )
                return redirect('restaurant:order_list')
            
            # Store order info for success message
            order_number = order.order_number
            customer_name = order.guest_name
            
            # Delete the order (this will cascade delete order items)
            order.delete()
            
            messages.success(
                request, 
                f'Order {order_number} for {customer_name} has been permanently deleted.'
            )
            return redirect('restaurant:order_list')
            
        except Exception as e:
            messages.error(
                request, 
                f'Error deleting order {order.order_number}: {str(e)}. '
                'Please try again or contact support if the problem persists.'
            )
    
    # Get additional context for the confirmation page
    context = {
        'order': order,
        'can_delete': order.status in ['cancelled', 'billed'],
    }
    
    return render(request, 'restaurant/order_confirm_delete.html', context)


@restaurant_required
def order_bulk_delete(request):
    """Delete multiple orders with proper validation"""
    if request.method == 'POST':
        order_ids = request.POST.getlist('order_ids')
        
        if not order_ids:
            messages.warning(request, 'No orders selected for deletion.')
            return redirect('restaurant:order_list')
        
        try:
            # Get orders that can be deleted
            orders_to_delete = Order.objects.filter(
                id__in=order_ids,
                status__in=['cancelled', 'billed']
            )
            
            # Get orders that cannot be deleted
            orders_cannot_delete = Order.objects.filter(
                id__in=order_ids
            ).exclude(status__in=['cancelled', 'billed'])
            
            deleted_count = 0
            for order in orders_to_delete:
                order.delete()
                deleted_count += 1
            
            # Show appropriate messages
            if deleted_count > 0:
                messages.success(
                    request, 
                    f'{deleted_count} order(s) have been permanently deleted.'
                )
            
            if orders_cannot_delete.exists():
                cannot_delete_numbers = [order.order_number for order in orders_cannot_delete]
                messages.warning(
                    request, 
                    f'The following orders could not be deleted (only cancelled or billed orders can be deleted): {", ".join(cannot_delete_numbers)}'
                )
            
            if deleted_count == 0 and not orders_cannot_delete.exists():
                messages.warning(request, 'No valid orders found for deletion.')
                
        except Exception as e:
            messages.error(
                request, 
                f'Error deleting orders: {str(e)}. '
                'Please try again or contact support if the problem persists.'
            )
    
    return redirect('restaurant:order_list')


# Restaurant Billing & Invoice Views
@restaurant_required
def restaurant_billing_dashboard(request):
    """Restaurant billing dashboard with key metrics"""
    # Get key statistics
    total_invoices = RestaurantInvoice.objects.count()
    pending_invoices = RestaurantInvoice.objects.filter(status='sent').count()
    overdue_invoices = RestaurantInvoice.objects.filter(status='overdue').count()
    total_revenue = RestaurantInvoice.objects.filter(status='paid').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Recent invoices
    recent_invoices = RestaurantInvoice.objects.select_related('order').order_by('-created_at')[:5]
    
    # Overdue invoices
    overdue_invoices_list = RestaurantInvoice.objects.filter(status='overdue').select_related('order')[:5]
    
    context = {
        'total_invoices': total_invoices,
        'pending_invoices': pending_invoices,
        'overdue_invoices': overdue_invoices,
        'total_revenue': total_revenue,
        'recent_invoices': recent_invoices,
        'overdue_invoices_list': overdue_invoices_list,
    }
    return render(request, 'restaurant/billing_dashboard.html', context)


@restaurant_required
def restaurant_invoice_list(request):
    """List all restaurant invoices with filtering"""
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    payment_method = request.GET.get('payment_method', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    invoices = RestaurantInvoice.objects.select_related('order').all()
    
    if search:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search) | 
            Q(customer_name__icontains=search) |
            Q(customer_email__icontains=search) |
            Q(order__order_number__icontains=search)
        )
    
    if status:
        invoices = invoices.filter(status=status)
    
    if payment_method:
        invoices = invoices.filter(payment_method=payment_method)
    
    if date_from:
        invoices = invoices.filter(invoice_date__gte=date_from)
    
    if date_to:
        invoices = invoices.filter(invoice_date__lte=date_to)
    
    # Show full list without pagination
    invoices = invoices.order_by('-created_at')
    
    context = {
        'invoices': invoices,
        'search': search,
        'status': status,
        'payment_method': payment_method,
        'date_from': date_from,
        'date_to': date_to,
        'status_choices': RestaurantInvoice.INVOICE_STATUS_CHOICES,
        'payment_method_choices': RestaurantInvoice.PAYMENT_METHOD_CHOICES,
    }
    return render(request, 'restaurant/invoice_list.html', context)


@restaurant_required
def restaurant_invoice_create(request):
    """Create a new restaurant invoice - simplified version"""
    if request.method == 'POST':
        try:
            order_id = request.POST.get('order')
            order = get_object_or_404(Order, id=order_id)
            
            # Get today's date for due date (simplified - no due date selection)
            from django.utils import timezone
            today = timezone.now().date()
            
            # Create invoice with simplified data
            invoice = RestaurantInvoice.objects.create(
                order=order,
                customer_name=request.POST.get('customer_name', order.customer_info),
                customer_email='',  # No email collection in simplified form
                customer_phone='',  # No phone collection in simplified form
                customer_address='',  # No address collection in simplified form
                subtotal=request.POST.get('subtotal', order.total_amount),
                tax_rate=0,  # No tax in simplified form
                discount_amount=0,  # No discount in simplified form
                due_date=today,  # Set due date to today (simplified)
                notes='',  # No notes in simplified form
                terms_conditions='',  # No terms in simplified form
                created_by=request.user
            )
            
            # Create invoice items from order items
            items_data = json.loads(request.POST.get('items_data', '[]'))
            if not items_data:
                # If no items data, get from order directly
                for order_item in order.items.all():
                    RestaurantInvoiceItem.objects.create(
                        invoice=invoice,
                        menu_item=order_item.menu_item,
                        description=order_item.menu_item.name,
                        quantity=order_item.quantity,
                        unit_price=order_item.unit_price
                    )
            else:
                # Use provided items data
                for item_data in items_data:
                    menu_item = MenuItem.objects.get(id=item_data['menu_item_id'])
                    RestaurantInvoiceItem.objects.create(
                        invoice=invoice,
                        menu_item=menu_item,
                        description=item_data['description'],
                        quantity=item_data['quantity'],
                        unit_price=item_data['unit_price']
                    )
            
            messages.success(request, f'Invoice {invoice.invoice_number} created successfully.')
            # Redirect directly to print page for immediate printing
            return redirect('restaurant:invoice_print', pk=invoice.pk)
        except Exception as e:
            messages.error(request, f'Error creating invoice: {str(e)}')
    
    # Show all restaurant orders (exclude cancelled and already invoiced) for selection
    orders = Order.objects.exclude(status='cancelled').exclude(invoices__isnull=False).select_related('table', 'guest', 'room').order_by('-created_at')
    
    context = {
        'orders': orders,
        'title': 'Create Restaurant Invoice'
    }
    return render(request, 'restaurant/invoice_form.html', context)


@restaurant_required
def restaurant_invoice_create_from_order(request, order_id):
    """Create a RestaurantInvoice from a specific Order and redirect to invoice details."""
    order = get_object_or_404(Order.objects.select_related('table', 'guest', 'room'), pk=order_id)
    # If an invoice already exists for this order, go to it
    existing = order.invoices.first()
    if existing:
        messages.info(request, f'Invoice {existing.invoice_number} already exists for this order.')
        return redirect('restaurant:invoice_detail', pk=existing.pk)

    from django.utils import timezone
    today = timezone.now().date()

    # Create a basic invoice using Order data
    invoice = RestaurantInvoice.objects.create(
        order=order,
        customer_name=getattr(order, 'customer_info', order.guest_name),
        customer_email='',
        customer_phone=order.guest_phone or '',
        customer_address='',
        subtotal=order.total_amount,
        tax_rate=0,
        discount_amount=0,
        due_date=today,
        notes=f'Generated from order {order.order_number}',
        terms_conditions='',
        created_by=request.user
    )

    # Copy order items into invoice items
    for order_item in order.items.all():
        RestaurantInvoiceItem.objects.create(
            invoice=invoice,
            menu_item=order_item.menu_item,
            description=order_item.menu_item.name,
            quantity=order_item.quantity,
            unit_price=order_item.unit_price
        )

    messages.success(request, f'Invoice {invoice.invoice_number} created from order {order.order_number}.')
    return redirect('restaurant:invoice_detail', pk=invoice.pk)

@restaurant_required
def restaurant_invoice_detail(request, pk):
    """View restaurant invoice details"""
    invoice = get_object_or_404(RestaurantInvoice, pk=pk)
    
    context = {
        'invoice': invoice,
    }
    return render(request, 'restaurant/invoice_detail.html', context)


@restaurant_required
def restaurant_invoice_edit(request, pk):
    """Edit restaurant invoice"""
    invoice = get_object_or_404(RestaurantInvoice, pk=pk)
    
    if request.method == 'POST':
        try:
            invoice.customer_name = request.POST.get('customer_name')
            invoice.customer_email = request.POST.get('customer_email', '')
            invoice.customer_phone = request.POST.get('customer_phone', '')
            invoice.customer_address = request.POST.get('customer_address', '')
            invoice.subtotal = request.POST.get('subtotal')
            invoice.tax_rate = request.POST.get('tax_rate', 0)
            invoice.discount_amount = request.POST.get('discount_amount', 0)
            invoice.due_date = request.POST.get('due_date')
            invoice.notes = request.POST.get('notes', '')
            invoice.terms_conditions = request.POST.get('terms_conditions', '')
            invoice.save()
            
            # Update invoice items
            invoice.items.all().delete()  # Remove existing items
            items_data = json.loads(request.POST.get('items_data', '[]'))
            for item_data in items_data:
                menu_item = MenuItem.objects.get(id=item_data['menu_item_id'])
                RestaurantInvoiceItem.objects.create(
                    invoice=invoice,
                    menu_item=menu_item,
                    description=item_data['description'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price']
                )
            
            messages.success(request, f'Invoice {invoice.invoice_number} updated successfully.')
            return redirect('restaurant:invoice_detail', pk=invoice.pk)
        except Exception as e:
            messages.error(request, f'Error updating invoice: {str(e)}')
    
    context = {
        'invoice': invoice,
        'title': 'Edit Restaurant Invoice'
    }
    return render(request, 'restaurant/invoice_form.html', context)


@restaurant_required
def restaurant_invoice_delete(request, pk):
    """Delete restaurant invoice"""
    invoice = get_object_or_404(RestaurantInvoice, pk=pk)
    
    if request.method == 'POST':
        try:
            invoice_number = invoice.invoice_number
            invoice.delete()
            messages.success(request, f'Invoice {invoice_number} deleted successfully.')
            return redirect('restaurant:invoice_list')
        except Exception as e:
            messages.error(request, f'Error deleting invoice: {str(e)}')
    
    context = {
        'invoice': invoice,
    }
    return render(request, 'restaurant/invoice_confirm_delete.html', context)


@restaurant_required
def restaurant_invoice_print(request, pk):
    """Print restaurant invoice"""
    invoice = get_object_or_404(RestaurantInvoice, pk=pk)
    
    context = {
        'invoice': invoice,
    }
    return render(request, 'restaurant/invoice_print.html', context)


@restaurant_required
def restaurant_invoice_receipt_print(request, pk):
    """Small-format 2.9in receipt view for printing/downloading."""
    invoice = get_object_or_404(RestaurantInvoice, pk=pk)
    context = { 'invoice': invoice }
    return render(request, 'restaurant/invoice_receipt_print.html', context)


@restaurant_required
def restaurant_invoice_receipt_pdf(request, pk):
    """Generate a 2.9-inch width small receipt PDF using ReportLab."""
    invoice = get_object_or_404(RestaurantInvoice, pk=pk)

    # 2.9 inch wide receipt. Height will be dynamic; start with a base and extend as we draw
    receipt_width_mm = 2.9 * 25.4  # inches to mm
    width = receipt_width_mm * mm_unit
    # Estimate height: header + items * rows + totals + footer
    num_rows = invoice.items.count()
    estimated_height_mm = 20 + (num_rows * 6) + 20 + 10
    height = estimated_height_mm * mm_unit

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Receipt_{invoice.invoice_number}.pdf"'

    pdf = canvas.Canvas(response, pagesize=(width, height))

    y = height - (5 * mm_unit)
    left_margin = 4 * mm_unit

    def draw_text(text, size=9, bold=False, align='left'):
        nonlocal y
        pdf.setFont('Helvetica-Bold' if bold else 'Helvetica', size)
        if align == 'center':
            pdf.drawCentredString(width / 2, y, str(text))
        else:
            pdf.drawString(left_margin, y, str(text))
        y -= (5 * mm_unit)

    # Header
    draw_text('Kabul Taj Hotel - Restaurant', size=10, bold=True, align='center')
    draw_text(f'Receipt: {invoice.invoice_number}', size=8, align='center')
    draw_text(f'Date: {invoice.invoice_date.strftime("%Y-%m-%d")}', size=8, align='center')
    y -= (2 * mm_unit)

    # Divider
    pdf.setStrokeColor(colors.grey)
    pdf.line(left_margin, y, width - left_margin, y)
    y -= (3 * mm_unit)

    # Customer / Order
    draw_text(f'Customer: {invoice.customer_name}', size=8)
    draw_text(f'Order: {invoice.order.order_number}', size=8)

    # Divider
    pdf.line(left_margin, y, width - left_margin, y)
    y -= (3 * mm_unit)

    # Table headers
    pdf.setFont('Helvetica-Bold', 8)
    pdf.drawString(left_margin, y, 'Item')
    pdf.drawRightString(width - (28 * mm_unit), y, 'Qty')
    pdf.drawRightString(width - (16 * mm_unit), y, 'Price')
    pdf.drawRightString(width - left_margin, y, 'Total')
    y -= (4 * mm_unit)
    pdf.setFont('Helvetica', 8)

    for item in invoice.items.all():
        if y < (15 * mm_unit):
            pdf.showPage()
            y = height - (5 * mm_unit)
        pdf.drawString(left_margin, y, str(item.description)[:22])
        pdf.drawRightString(width - (28 * mm_unit), y, str(item.quantity))
        pdf.drawRightString(width - (16 * mm_unit), y, f"{item.unit_price:.2f}")
        pdf.drawRightString(width - left_margin, y, f"{item.total_price:.2f}")
        y -= (4 * mm_unit)

    # Divider
    y -= (1 * mm_unit)
    pdf.line(left_margin, y, width - left_margin, y)
    y -= (3 * mm_unit)

    # Totals
    pdf.setFont('Helvetica-Bold', 9)
    pdf.drawRightString(width - (16 * mm_unit), y, 'Subtotal:')
    pdf.drawRightString(width - left_margin, y, f"{invoice.subtotal:.2f}")
    y -= (4 * mm_unit)
    if invoice.tax_amount and invoice.tax_amount > 0:
        pdf.setFont('Helvetica', 8)
        pdf.drawRightString(width - (16 * mm_unit), y, f"Tax ({invoice.tax_rate}%):")
        pdf.drawRightString(width - left_margin, y, f"{invoice.tax_amount:.2f}")
        y -= (4 * mm_unit)
    if invoice.discount_amount and invoice.discount_amount > 0:
        pdf.setFont('Helvetica', 8)
        pdf.drawRightString(width - (16 * mm_unit), y, 'Discount:')
        pdf.drawRightString(width - left_margin, y, f"-{invoice.discount_amount:.2f}")
        y -= (4 * mm_unit)
    pdf.setFont('Helvetica-Bold', 10)
    pdf.drawRightString(width - (16 * mm_unit), y, 'TOTAL:')
    pdf.drawRightString(width - left_margin, y, f"{invoice.total_amount:.2f}")
    y -= (6 * mm_unit)

    # Footer
    pdf.setFont('Helvetica', 8)
    draw_text('Thank you! No refunds without receipt.', size=8, align='center')

    pdf.showPage()
    pdf.save()
    return response


@restaurant_required
def restaurant_invoice_update_status(request, pk):
    """Update invoice status via AJAX"""
    if request.method == 'POST':
        invoice = get_object_or_404(RestaurantInvoice, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in dict(RestaurantInvoice.INVOICE_STATUS_CHOICES):
            invoice.status = new_status
            if new_status == 'paid':
                invoice.payment_due_date = timezone.now().date()
            invoice.save()
            
            return JsonResponse({'success': True, 'status': new_status})
    
    return JsonResponse({'success': False})


@restaurant_required
def get_order_details_for_invoice(request, order_id):
    """Get order details for invoice creation via AJAX"""
    try:
        order = Order.objects.select_related('table', 'guest', 'room').get(id=order_id)
        items_data = []
        
        for item in order.items.all():
            items_data.append({
                'menu_item_id': item.menu_item.id,
                'description': item.menu_item.name,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'total_price': float(item.total_price)
            })
        
        return JsonResponse({
            'success': True,
            'order': {
                'order_number': order.order_number,
                'customer_name': order.customer_info,
                'table_name': f"Table {order.table.table_number}",
                'order_date': order.created_at.strftime('%B %d, %Y'),
                'subtotal': float(order.total_amount),
                'items': items_data
            }
        })
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Order not found'})


@restaurant_required
def restaurant_invoice_process_payment(request, pk):
    """Restaurant-side payment processing page for a specific invoice."""
    invoice = get_object_or_404(RestaurantInvoice, pk=pk)

    if request.method == 'POST':
        try:
            payment_method = request.POST.get('payment_method')
            payment_reference = request.POST.get('payment_reference', '')

            if not payment_method:
                messages.error(request, 'Please choose a payment method.')
                return redirect('restaurant:invoice_process_payment', pk=invoice.pk)

            invoice.status = 'paid'
            invoice.payment_method = payment_method
            invoice.payment_reference = payment_reference
            invoice.payment_due_date = timezone.now().date()
            invoice.save()

            try:
                order = invoice.order
                order.payment_status = 'paid'
                order.status = 'billed'
                order.save()
                
                # Create transaction record
                Transaction.objects.create(
                    transaction_type='invoice',
                    invoice=invoice,
                    order=order,
                    customer_name=invoice.customer_name,
                    table_number=order.table.table_number,
                    amount=invoice.total_amount,
                    payment_method=payment_method,
                    created_by=request.user
                )
            except Exception:
                pass

            messages.success(request, f'Payment completed for {invoice.invoice_number}.')
            return redirect('restaurant:invoice_detail', pk=invoice.pk)
        except Exception as e:
            messages.error(request, f'Error processing payment: {str(e)}')
            return redirect('restaurant:invoice_process_payment', pk=invoice.pk)

    context = {
        'invoice': invoice,
        'payment_method_choices': RestaurantInvoice.PAYMENT_METHOD_CHOICES,
    }
    return render(request, 'restaurant/invoice_process_payment.html', context)


@restaurant_required
def restaurant_invoice_start_payment(request, order_id):
    """Ensure an invoice exists for the order then redirect to the payment page."""
    order = get_object_or_404(Order, pk=order_id)
    existing = order.invoices.first()
    if existing:
        return redirect('restaurant:invoice_process_payment', pk=existing.pk)

    # Create invoice then redirect
    today = timezone.now().date()
    invoice = RestaurantInvoice.objects.create(
        order=order,
        customer_name=getattr(order, 'customer_info', order.guest_name),
        customer_email='',
        customer_phone=order.guest_phone or '',
        customer_address='',
        subtotal=order.total_amount,
        tax_rate=0,
        discount_amount=0,
        due_date=today,
        notes=f'Generated from order {order.order_number}',
        terms_conditions='',
        created_by=request.user
    )
    for oi in order.items.all():
        RestaurantInvoiceItem.objects.create(
            invoice=invoice,
            menu_item=oi.menu_item,
            description=oi.menu_item.name,
            quantity=oi.quantity,
            unit_price=oi.unit_price
        )
    return redirect('restaurant:invoice_process_payment', pk=invoice.pk)
