from django.db import models
from django.conf import settings
from apps.bookings.models import Booking
from apps.restaurant.models import Order
from apps.conference.models import ConferenceBooking
from simple_history.models import HistoricalRecords


class Invoice(models.Model):
    """Invoice model for all hotel services"""
    INVOICE_TYPES = [
        ('custom', 'Custom Invoice'),
        ('gym', 'Gym'),
        ('swimming_pool', 'Swimming Pool'),
        ('booking', 'Booking Invoice'),
        ('conference', 'Conference Invoice'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    invoice_number = models.CharField(max_length=20, unique=True)
    invoice_type = models.CharField(max_length=20, choices=INVOICE_TYPES)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True, related_name='invoices')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True, related_name='billing_invoices')
    conference_booking = models.ForeignKey(ConferenceBooking, on_delete=models.CASCADE, null=True, blank=True, related_name='invoices')
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15, blank=True)
    customer_address = models.TextField(blank=True)
    invoice_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='invoices_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        ordering = ['-invoice_date']

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.customer_name}"

    @property
    def remaining_amount(self):
        return self.total_amount - self.paid_amount

    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.due_date < timezone.now().date() and self.status != 'paid'


class InvoiceItem(models.Model):
    """Individual items in an invoice"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Invoice Item'
        verbose_name_plural = 'Invoice Items'

    def __str__(self):
        return f"{self.description} - {self.invoice.invoice_number}"


class Payment(models.Model):
    """Payment records for invoices"""
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('online', 'Online Payment'),
        ('check', 'Check'),
        ('other', 'Other'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='billing_payments_processed'
    )
    notes = models.TextField(blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.invoice.invoice_number}"


class TaxRate(models.Model):
    """Tax rates for different services"""
    name = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=5, decimal_places=2, help_text='Tax rate as percentage')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Tax Rate'
        verbose_name_plural = 'Tax Rates'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.rate}%)"


class Discount(models.Model):
    """Discount rules and coupons"""
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed_amount', 'Fixed Amount'),
    ]
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    value = models.DecimalField(max_digits=8, decimal_places=2)
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    maximum_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valid_from = models.DateField()
    valid_until = models.DateField()
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Discount'
        verbose_name_plural = 'Discounts'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def is_valid(self):
        from django.utils import timezone
        today = timezone.now().date()
        return (
            self.is_active and
            self.valid_from <= today <= self.valid_until and
            (self.usage_limit is None or self.used_count < self.usage_limit)
        )
