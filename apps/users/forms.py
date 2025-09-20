from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserForm(forms.ModelForm):
    """Form for creating and editing users"""
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'phone_number', 'address', 'date_of_birth', 'is_active']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        # On create, require a password
        if self.instance.pk is None and not password:
            raise forms.ValidationError("Password is required when creating a new user")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])

        # Align staff/superuser flags with chosen role
        if user.role == 'admin':
            user.is_staff = True
            user.is_superuser = True
        else:
            # App staff should access admin if needed, but not superuser
            user.is_staff = True
            user.is_superuser = False
        if commit:
            user.save()
        return user


class UserCreationForm(UserCreationForm):
    """Form for creating new users"""
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'phone_number', 'address', 'date_of_birth']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        } 


class SignUpForm(UserCreationForm):
    """Restricted signup form for admin to create users"""
    ALLOWED_ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('receptionist', 'Receptionist'),
        ('restaurant', 'Restaurant Manager'),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'role' in self.fields:
            self.fields['role'].choices = self.ALLOWED_ROLE_CHOICES

    def save(self, commit=True):
        user = super().save(commit=False)
        # Align staff/superuser flags with chosen role
        if user.role == 'admin':
            user.is_staff = True
            user.is_superuser = True
        else:
            user.is_staff = True
            user.is_superuser = False
        if commit:
            user.save()
        return user


class UserSettingsForm(forms.ModelForm):
    """Form for editing the current user's profile (excluding role/permissions)"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'date_of_birth']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }