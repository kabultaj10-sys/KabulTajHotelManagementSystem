from django.db import models
from django.conf import settings
from simple_history.models import HistoricalRecords


class ConferenceRoom(models.Model):
    """Conference room information"""
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Maintenance'),
        ('cleaning', 'Cleaning'),
        ('out_of_order', 'Out of Order'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    capacity = models.PositiveIntegerField()
    floor = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2)
    daily_rate = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True)
    amenities = models.TextField(blank=True)
    # Room images
    image_1 = models.ImageField(upload_to='conference_rooms/', blank=True, null=True, help_text='Main room image')
    image_2 = models.ImageField(upload_to='conference_rooms/', blank=True, null=True, help_text='Secondary room image')
    image_3 = models.ImageField(upload_to='conference_rooms/', blank=True, null=True, help_text='Additional room image')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Conference Room'
        verbose_name_plural = 'Conference Rooms'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (Capacity: {self.capacity})"


class ConferenceEquipment(models.Model):
    """Conference room equipment"""
    EQUIPMENT_TYPES = [
        ('projector', 'Projector'),
        ('screen', 'Screen'),
        ('sound_system', 'Sound System'),
        ('microphone', 'Microphone'),
        ('video_conference', 'Video Conference'),
        ('whiteboard', 'Whiteboard'),
        ('flipchart', 'Flipchart'),
        ('computer', 'Computer'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    equipment_type = models.CharField(max_length=20, choices=EQUIPMENT_TYPES)
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    maintenance_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Conference Equipment'
        verbose_name_plural = 'Conference Equipment'
        ordering = ['equipment_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_equipment_type_display()})"


class ConferenceBooking(models.Model):
    """Conference room bookings"""
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    
    booking_number = models.CharField(max_length=20, unique=True)
    room = models.ForeignKey(ConferenceRoom, on_delete=models.CASCADE, related_name='bookings')
    client_name = models.CharField(max_length=200)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=15)
    event_title = models.CharField(max_length=200)
    event_description = models.TextField(blank=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    attendees_count = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    special_requirements = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='conference_bookings_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Conference Booking'
        verbose_name_plural = 'Conference Bookings'
        ordering = ['-start_datetime']

    def __str__(self):
        return f"Booking {self.booking_number} - {self.event_title}"

    @property
    def duration_hours(self):
        duration = self.end_datetime - self.start_datetime
        return duration.total_seconds() / 3600

    @property
    def remaining_amount(self):
        return self.total_amount - self.paid_amount


class ConferenceEvent(models.Model):
    """Conference events and meetings"""
    EVENT_TYPES = [
        ('meeting', 'Meeting'),
        ('conference', 'Conference'),
        ('seminar', 'Seminar'),
        ('workshop', 'Workshop'),
        ('presentation', 'Presentation'),
        ('training', 'Training'),
        ('other', 'Other'),
    ]
    
    booking = models.OneToOneField(ConferenceBooking, on_delete=models.CASCADE, related_name='event')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    organizer_name = models.CharField(max_length=200)
    organizer_phone = models.CharField(max_length=15, blank=True)
    agenda = models.TextField(blank=True)
    catering_required = models.BooleanField(default=False)
    catering_details = models.TextField(blank=True)
    technical_support_required = models.BooleanField(default=False)
    technical_requirements = models.TextField(blank=True)
    setup_time_required = models.PositiveIntegerField(default=0, help_text='Setup time in minutes')
    cleanup_time_required = models.PositiveIntegerField(default=0, help_text='Cleanup time in minutes')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Conference Event'
        verbose_name_plural = 'Conference Events'

    def __str__(self):
        return f"{self.event_type.title()} - {self.booking.event_title}"


class ConferencePayment(models.Model):
    """Payment records for conference bookings"""
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('online', 'Online Payment'),
        ('other', 'Other'),
    ]
    
    booking = models.ForeignKey(ConferenceBooking, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='conference_payments_processed'
    )
    notes = models.TextField(blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Conference Payment'
        verbose_name_plural = 'Conference Payments'
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.booking.booking_number}"
