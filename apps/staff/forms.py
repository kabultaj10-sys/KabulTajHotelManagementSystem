from django import forms
from .models import StaffProfile, Department
from apps.users.models import User
from django.db import models


class StaffProfileForm(forms.ModelForm):
    """Form for creating and editing staff profiles"""
    class Meta:
        model = StaffProfile
        fields = ['user', 'employee_id', 'department', 'position', 'hire_date', 'salary', 'emergency_contact', 'emergency_phone', 'is_active']
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
            'salary': forms.NumberInput(attrs={'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show users who don't already have a staff profile
        if self.instance.pk:
            # For editing, include the current user
            self.fields['user'].queryset = User.objects.filter(
                models.Q(staff_profile__isnull=True) | models.Q(staff_profile=self.instance)
            )
        else:
            # For creating, only show users without staff profiles
            self.fields['user'].queryset = User.objects.filter(staff_profile__isnull=True)


class DepartmentForm(forms.ModelForm):
    """Form for creating and editing departments"""
    class Meta:
        model = Department
        fields = ['name', 'description', 'manager', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        } 