from django.db import models
from simple_history.models import HistoricalRecords
from django.core.validators import RegexValidator
from decimal import Decimal
from django.conf import settings


class Guest(models.Model):
    """Guest profiles with comprehensive information"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    VIP_STATUS_CHOICES = [
        ('regular', 'Regular'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ]
    
    ID_TYPE_CHOICES = [
        ('passport', 'Passport'),
        ('national_id', 'National ID'),
        ('driving_license', 'Driving License'),
        ('other', 'Other'),
    ]

    # Basic Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    # Email optional per request; keep unique if provided
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, validators=[
        RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be valid")
    ])
    # Guest type: booking (full data), gym, swimming
    GUEST_TYPE_CHOICES = [
        ('booking', 'Booking Guest'),
        ('gym', 'Gym Guest'),
        ('swimming', 'Swimming Pool Guest'),
    ]
    guest_type = models.CharField(max_length=20, choices=GUEST_TYPE_CHOICES, default='booking')
    # Guest source (e.g., travel agency) replaces special requests for booking context
    guest_source = models.CharField(max_length=200, blank=True)
    # Explicit age for simplified gym/swimming entries
    age = models.PositiveIntegerField(null=True, blank=True)
    
    # Personal Details
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    passport_number = models.CharField(max_length=50, blank=True)
    id_type = models.CharField(max_length=20, choices=ID_TYPE_CHOICES, blank=True)
    id_number = models.CharField(max_length=50, blank=True)
    id_picture = models.ImageField(upload_to='guest_id_pictures/', blank=True, null=True, help_text="Upload passport or identity document picture")
    
    # Address Information
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    
    # VIP and Preferences
    vip_status = models.CharField(max_length=20, choices=VIP_STATUS_CHOICES, default='regular')
    special_requests = models.TextField(blank=True)
    dietary_restrictions = models.TextField(blank=True)
    room_preferences = models.TextField(blank=True)
    
    # Business Information
    company = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    business_phone = models.CharField(max_length=20, blank=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_relationship = models.CharField(max_length=100, blank=True)
    
    # Status and Tracking
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Guest'
        verbose_name_plural = 'Guests'
        ordering = ['-created_at']

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        """Return full name"""
        return f"{self.first_name} {self.last_name}".strip()

    def calculated_age(self):
        """Calculate age from date of birth (does not use stored age field)"""
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

    @property
    def total_stays(self):
        """Get total number of stays"""
        return self.bookings.filter(status='completed').count()

    @property
    def total_nights(self):
        """Get total number of nights stayed"""
        total = 0
        for booking in self.bookings.filter(status='completed'):
            if booking.check_in_date and booking.check_out_date:
                total += (booking.check_out_date - booking.check_in_date).days
        return total

    @property
    def total_spent(self):
        """Get total amount spent"""
        return self.bookings.filter(status='completed').aggregate(
            total=models.Sum('total_amount')
        )['total'] or Decimal('0.00')

    def get_vip_benefits(self):
        """Get VIP benefits based on status"""
        benefits = {
            'regular': ['Standard service'],
            'silver': ['Standard service', '10% discount', 'Priority check-in'],
            'gold': ['Standard service', '15% discount', 'Priority check-in', 'Room upgrade'],
            'platinum': ['Standard service', '20% discount', 'Priority check-in', 'Room upgrade', 'Concierge service']
        }
        return benefits.get(self.vip_status, [])


class GuestPreference(models.Model):
    """Guest preferences and special requirements"""
    guest = models.OneToOneField(Guest, on_delete=models.CASCADE, related_name='preferences')
    
    # Room Preferences
    preferred_floor = models.PositiveIntegerField(null=True, blank=True)
    preferred_room_type = models.ForeignKey('rooms.RoomType', on_delete=models.SET_NULL, null=True, blank=True)
    smoking_preference = models.BooleanField(default=False)
    accessibility_requirements = models.TextField(blank=True)
    
    # Service Preferences
    housekeeping_frequency = models.CharField(max_length=20, choices=[
        ('daily', 'Daily'),
        ('on_request', 'On Request'),
        ('do_not_disturb', 'Do Not Disturb'),
    ], default='daily')
    
    # Communication Preferences
    preferred_language = models.CharField(max_length=50, default='English')
    communication_method = models.CharField(max_length=20, choices=[
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('sms', 'SMS'),
    ], default='email')
    
    # Additional Preferences
    special_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Guest Preference'
        verbose_name_plural = 'Guest Preferences'

    def __str__(self):
        return f"Preferences for {self.guest.full_name}"


class GuestDocument(models.Model):
    """Guest documents and identification"""
    DOCUMENT_TYPE_CHOICES = [
        ('passport', 'Passport'),
        ('national_id', 'National ID'),
        ('driving_license', 'Driving License'),
        ('visa', 'Visa'),
        ('other', 'Other'),
    ]

    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    document_number = models.CharField(max_length=100)
    issuing_country = models.CharField(max_length=100, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    document_file = models.FileField(upload_to='guest_documents/', blank=True)
    is_verified = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Guest Document'
        verbose_name_plural = 'Guest Documents'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.document_number}"

    @property
    def is_expired(self):
        """Check if document is expired"""
        if self.expiry_date:
            from datetime import date
            return date.today() > self.expiry_date
        return False


class GuestProfileSummary(models.Model):
    """Immutable summary snapshot for a Guest used for history views and analytics."""
    guest = models.OneToOneField(Guest, on_delete=models.PROTECT, related_name='summary')
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    total_bookings = models.PositiveIntegerField(default=0)
    completed_bookings = models.PositiveIntegerField(default=0)
    total_nights = models.PositiveIntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Guest Profile Summary'
        verbose_name_plural = 'Guest Profile Summaries'

    def delete(self, *args, **kwargs):  # make undeletable
        raise models.ProtectedError('GuestProfileSummary cannot be deleted', self)

    def __str__(self):
        return f"Summary for {self.guest.full_name}"
