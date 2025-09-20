from django.contrib.auth.models import AbstractUser
from django.db import models
from simple_history.models import HistoricalRecords


class User(AbstractUser):
    """
    Custom User model with role-based access control
    """
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('receptionist', 'Receptionist'),
        ('restaurant', 'Restaurant Manager'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='receptionist'
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    hire_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        # Treat Django superusers as admins regardless of stored role
        return self.is_superuser or self.role == 'admin'
    
    @property
    def is_receptionist(self):
        return self.role == 'receptionist'
    
    @property
    def is_restaurant(self):
        return self.role == 'restaurant'
    
    @property
    def can_manage_bookings(self):
        return self.role in ['admin', 'receptionist']
    
    @property
    def can_manage_guests(self):
        return self.role in ['admin', 'receptionist']
    
    @property
    def can_manage_rooms(self):
        return self.role in ['admin', 'receptionist']
    
    @property
    def can_manage_restaurant(self):
        return self.role in ['admin', 'restaurant']
    
    @property
    def can_manage_billing(self):
        return self.role in ['admin', 'receptionist']
    
    @property
    def can_manage_users(self):
        return self.role == 'admin'
    
    @property
    def can_access_dashboard(self):
        return self.role in ['admin', 'receptionist', 'restaurant']
