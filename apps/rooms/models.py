from django.db import models
from simple_history.models import HistoricalRecords
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class RoomType(models.Model):
    """Room types with pricing and amenities"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField(default=2)
    amenities = models.TextField(blank=True, help_text="Comma-separated list of amenities")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Room Type'
        verbose_name_plural = 'Room Types'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - ${self.base_price}"

    @property
    def amenities_list(self):
        """Return amenities as a list"""
        if self.amenities:
            return [amenity.strip() for amenity in self.amenities.split(',')]
        return []


class Room(models.Model):
    """Hotel rooms with status and pricing"""
    FLOOR_CHOICES = [
        (1, '1st Floor'), (2, '2nd Floor'), (3, '3rd Floor'), (4, '4th Floor'),
        (5, '5th Floor'), (6, '6th Floor'), (7, '7th Floor'), (8, '8th Floor'),
        (9, '9th Floor'), (10, '10th Floor'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Maintenance'),
        ('cleaning', 'Cleaning'),
        ('reserved', 'Reserved'),
        ('out_of_order', 'Out of Order'),
    ]

    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='rooms')
    floor = models.PositiveIntegerField(choices=FLOOR_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'
        ordering = ['room_number']

    def __str__(self):
        return f"Room {self.room_number} - {self.room_type.name}"

    @property
    def effective_price(self):
        """Return current price or base price if not set"""
        return self.current_price or self.room_type.base_price

    @property
    def is_available(self):
        """Check if room is available for booking"""
        return self.status == 'available' and self.is_active

    @property
    def current_booking(self):
        """Get current active booking for this room"""
        return self.bookings.filter(status='active').first()

    def update_status(self, new_status):
        """Update room status with validation"""
        if new_status in dict(self.STATUS_CHOICES):
            self.status = new_status
            self.save()
            return True
        return False


class RoomMaintenance(models.Model):
    """Room maintenance records"""
    MAINTENANCE_TYPE_CHOICES = [
        ('routine', 'Routine'),
        ('repair', 'Repair'),
        ('emergency', 'Emergency'),
        ('upgrade', 'Upgrade'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='maintenance_records')
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPE_CHOICES)
    description = models.TextField()
    scheduled_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Room Maintenance'
        verbose_name_plural = 'Room Maintenance'
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"Maintenance - Room {self.room.room_number} - {self.get_maintenance_type_display()}"


class RoomAmenity(models.Model):
    """Individual room amenities"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Room Amenity'
        verbose_name_plural = 'Room Amenities'
        ordering = ['name']

    def __str__(self):
        return self.name
