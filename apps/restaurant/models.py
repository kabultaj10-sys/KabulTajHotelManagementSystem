from django.db import models
from django.conf import settings
from simple_history.models import HistoricalRecords


class MenuCategory(models.Model):
    """Menu categories (appetizers, main course, desserts, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Menu Category'
        verbose_name_plural = 'Menu Categories'
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    """Individual menu items"""
    CUISINE_CHOICES = [
        ('local', 'Local'),
        ('international', 'International'),
        ('continental', 'Continental'),
        ('asian', 'Asian'),
        ('mediterranean', 'Mediterranean'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name='items')
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    cuisine_type = models.CharField(max_length=20, choices=CUISINE_CHOICES, default='local')
    preparation_time = models.PositiveIntegerField(help_text='Preparation time in minutes')
    is_vegetarian = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    is_spicy = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu Items'
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} - {self.category.name}"


class Table(models.Model):
    """Restaurant tables"""
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('reserved', 'Reserved'),
        ('cleaning', 'Cleaning'),
        ('out_of_order', 'Out of Order'),
    ]
    
    table_number = models.CharField(max_length=10, unique=True)
    capacity = models.PositiveIntegerField()
    location = models.CharField(max_length=100, blank=True)  # e.g., "Garden View", "Window Side"
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Table'
        verbose_name_plural = 'Tables'
        ordering = ['table_number']

    def __str__(self):
        return f"Table {self.table_number} ({self.capacity} seats)"


class TableReservation(models.Model):
    """Table reservations"""
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='reservations')
    guest_name = models.CharField(max_length=200)
    guest_phone = models.CharField(max_length=15)
    guest_email = models.EmailField(blank=True)
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    party_size = models.PositiveIntegerField()
    special_requests = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='table_reservations_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Table Reservation'
        verbose_name_plural = 'Table Reservations'
        ordering = ['-reservation_date', '-reservation_time']

    def __str__(self):
        return f"Reservation for {self.guest_name} - Table {self.table.table_number}"


class Order(models.Model):
    """Restaurant orders"""
    STATUS_CHOICES = [
        ('placed', 'Placed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('served', 'Served'),
        ('billed', 'Billed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True)
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='orders')
    guest = models.ForeignKey('guests.Guest', on_delete=models.SET_NULL, null=True, blank=True, related_name='restaurant_orders')
    room = models.ForeignKey('rooms.Room', on_delete=models.SET_NULL, null=True, blank=True, related_name='restaurant_orders')
    guest_name = models.CharField(max_length=200)
    guest_phone = models.CharField(max_length=15, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='placed')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    special_instructions = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number} - {self.guest_name}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        """Generate unique order number"""
        import uuid
        return f"ORD-{uuid.uuid4().hex[:8].upper()}"

    @property
    def order_type(self):
        """Return whether order is for guest or room"""
        if self.guest:
            return "Guest"
        elif self.room:
            return "Room"
        else:
            return "Walk-in"

    @property
    def customer_info(self):
        """Return customer information"""
        if self.guest:
            return f"{self.guest.full_name} (Guest)"
        elif self.room:
            return f"Room {self.room.room_number}"
        else:
            return self.guest_name


class OrderItem(models.Model):
    """Individual items in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    special_instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name} - {self.order.order_number}"

    @property
    def total_price(self):
        return self.quantity * self.unit_price


class RestaurantInvoice(models.Model):
    """Restaurant invoices for customers"""
    INVOICE_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('other', 'Other'),
    ]
    
    invoice_number = models.CharField(max_length=20, unique=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='invoices')
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=15, blank=True)
    customer_address = models.TextField(blank=True)
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    invoice_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    payment_due_date = models.DateField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=INVOICE_STATUS_CHOICES, default='draft')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    
    notes = models.TextField(blank=True)
    terms_conditions = models.TextField(blank=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='restaurant_invoices_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Restaurant Invoice'
        verbose_name_plural = 'Restaurant Invoices'
        ordering = ['-invoice_date', '-created_at']

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.customer_name}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        
        # Calculate tax and total
        self.tax_amount = (self.subtotal * self.tax_rate) / 100
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        
        super().save(*args, **kwargs)

    def generate_invoice_number(self):
        """Generate unique invoice number"""
        import uuid
        return f"RINV-{uuid.uuid4().hex[:8].upper()}"

    @property
    def is_overdue(self):
        """Check if invoice is overdue"""
        from django.utils import timezone
        return self.status == 'sent' and self.due_date < timezone.now().date()

    @property
    def days_overdue(self):
        """Calculate days overdue"""
        from django.utils import timezone
        if self.is_overdue:
            return (timezone.now().date() - self.due_date).days
        return 0


class RestaurantInvoiceItem(models.Model):
    """Individual items in restaurant invoice"""
    invoice = models.ForeignKey(RestaurantInvoice, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Restaurant Invoice Item'
        verbose_name_plural = 'Restaurant Invoice Items'

    def __str__(self):
        return f"{self.quantity}x {self.description} - {self.invoice.invoice_number}"

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class Transaction(models.Model):
    """Track completed transactions for revenue calculation and history"""
    TRANSACTION_TYPE_CHOICES = [
        ('order', 'Order'),
        ('invoice', 'Invoice'),
    ]
    
    transaction_id = models.CharField(max_length=50, unique=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    invoice = models.ForeignKey(RestaurantInvoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    
    customer_name = models.CharField(max_length=200)
    table_number = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=RestaurantInvoice.PAYMENT_METHOD_CHOICES, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='transactions_created'
    )
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.customer_name} - ${self.amount}"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        super().save(*args, **kwargs)

    def generate_transaction_id(self):
        """Generate unique transaction ID"""
        import uuid
        return f"TXN-{uuid.uuid4().hex[:8].upper()}"
