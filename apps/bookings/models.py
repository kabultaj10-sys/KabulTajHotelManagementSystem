from django.db import models
from simple_history.models import HistoricalRecords
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid


def generate_booking_number():
    """Generate a unique booking number"""
    return f"BK{uuid.uuid4().hex[:8].upper()}"


class Booking(models.Model):
    """Advanced booking system with availability checking"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]

    # Booking Information
    booking_number = models.CharField(max_length=20, unique=True, default=generate_booking_number)
    guest = models.ForeignKey('guests.Guest', on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey('rooms.Room', on_delete=models.CASCADE, related_name='bookings')
    
    # Dates and Duration
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    check_in_time = models.TimeField(default='14:00')
    check_out_time = models.TimeField(default='11:00')
    
    # Guest Information
    number_of_guests = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    guest_names = models.TextField(blank=True, help_text="Names of all guests")
    
    # Pricing and Payment
    room_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status and Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Special Requirements
    special_requests = models.TextField(blank=True)
    dietary_restrictions = models.TextField(blank=True)
    room_preferences = models.TextField(blank=True)
    
    # Booking Details
    source = models.CharField(max_length=50, choices=[
        ('direct', 'Direct'),
        ('website', 'Website'),
        ('phone', 'Phone'),
        ('travel_agent', 'Travel Agent'),
        ('online_booking', 'Online Booking'),
        ('walk_in', 'Walk-in'),
    ], default='direct')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking {self.booking_number} - {self.guest.full_name}"

    @property
    def duration(self):
        """Calculate booking duration in days"""
        if self.check_in_date and self.check_out_date:
            return (self.check_out_date - self.check_in_date).days
        return 0

    @property
    def is_active(self):
        """Check if booking is currently active"""
        from datetime import date
        today = date.today()
        return (self.status == 'active' and 
                self.check_in_date <= today <= self.check_out_date)

    @property
    def is_overdue(self):
        """Check if guest has overstayed"""
        from datetime import date
        today = date.today()
        return (self.status == 'active' and 
                today > self.check_out_date)

    @property
    def remaining_balance(self):
        """Calculate remaining balance"""
        return self.total_amount - self.deposit_amount

    def calculate_total_amount(self):
        """Calculate total amount based on duration and rate"""
        self.total_amount = self.room_rate * self.duration
        self.balance_amount = self.total_amount - self.deposit_amount
        return self.total_amount

    def check_availability(self):
        """Check if room is available for the booking dates"""
        conflicting_bookings = Booking.objects.filter(
            room=self.room,
            status__in=['confirmed', 'active'],
            check_in_date__lt=self.check_out_date,
            check_out_date__gt=self.check_in_date
        ).exclude(pk=self.pk)
        
        return conflicting_bookings.count() == 0

    def confirm_booking(self):
        """Confirm the booking"""
        if self.check_availability():
            self.status = 'confirmed'
            self.confirmed_at = models.DateTimeField(auto_now=True)
            self.save()
            return True
        return False

    def cancel_booking(self):
        """Cancel the booking"""
        self.status = 'cancelled'
        self.cancelled_at = models.DateTimeField(auto_now=True)
        self.save()

    def save(self, *args, **kwargs):
        """Override save to calculate amounts"""
        if not self.total_amount:
            self.calculate_total_amount()
        super().save(*args, **kwargs)


class CheckIn(models.Model):
    """Check-in process and details"""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='check_in')
    check_in_datetime = models.DateTimeField(auto_now_add=True)
    checked_in_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='check_ins_processed')
    
    # Guest Verification
    id_verified = models.BooleanField(default=False)
    payment_verified = models.BooleanField(default=False)
    room_inspected = models.BooleanField(default=False)
    
    # Room Assignment
    actual_room = models.ForeignKey('rooms.Room', on_delete=models.SET_NULL, null=True, blank=True)
    room_key_issued = models.BooleanField(default=False)
    
    # Additional Information
    special_instructions = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Check In'
        verbose_name_plural = 'Check Ins'

    def __str__(self):
        return f"Check-in for {self.booking.guest.full_name}"

    def complete_check_in(self):
        """Complete the check-in process"""
        # Update booking status
        self.booking.status = 'active'
        self.booking.save()
        
        # Update room status
        if self.actual_room:
            self.actual_room.status = 'occupied'
            self.actual_room.save()
        else:
            self.booking.room.status = 'occupied'
            self.booking.room.save()


class CheckOut(models.Model):
    """Check-out process and details"""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='check_out')
    check_out_datetime = models.DateTimeField(auto_now_add=True)
    checked_out_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='check_outs_processed')
    
    # Check-out Process
    room_inspected = models.BooleanField(default=False)
    keys_returned = models.BooleanField(default=False)
    payment_completed = models.BooleanField(default=False)
    
    # Additional Charges
    additional_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    late_checkout = models.BooleanField(default=False)
    late_checkout_hours = models.PositiveIntegerField(default=0)
    
    # Guest Feedback
    guest_satisfaction = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    feedback = models.TextField(blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Check Out'
        verbose_name_plural = 'Check Outs'

    def __str__(self):
        return f"Check-out for {self.booking.guest.full_name}"

    def complete_check_out(self):
        """Complete the check-out process"""
        # Update booking status
        self.booking.status = 'completed'
        self.booking.save()
        
        # Update room status
        room = self.booking.room
        room.status = 'cleaning'
        room.save()
        
        # Calculate final amount
        final_amount = self.booking.total_amount + self.additional_charges
        return final_amount


class BookingPayment(models.Model):
    """Payment tracking for bookings"""
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('online', 'Online Payment'),
        ('check', 'Check'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_date = models.DateTimeField(auto_now_add=True)
    reference_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='payments_processed')
    notes = models.TextField(blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Booking Payment'
        verbose_name_plural = 'Booking Payments'
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment {self.reference_number} - {self.booking.guest.full_name}"

    def process_payment(self):
        """Process the payment"""
        if self.status == 'pending':
            self.status = 'completed'
            self.save()
            
            # Update booking payment status
            total_paid = self.booking.payments.filter(status='completed').aggregate(
                total=models.Sum('amount')
            )['total'] or 0
            
            if total_paid >= self.booking.total_amount:
                self.booking.payment_status = 'paid'
            else:
                self.booking.payment_status = 'partial'
            
            self.booking.save()
            return True
        return False
