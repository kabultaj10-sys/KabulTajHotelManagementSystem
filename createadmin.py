#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yourproject.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_superuser():
    User = get_user_model()
    username = "admin"
    
    # Check if superuser already exists
    if User.objects.filter(is_superuser=True).exists():
        print("Superuser already exists. Skipping creation.")
        return True
    
    # Only create if doesn't exist
    password = "KabulTaj@ByteRender@2025"
    email = "kabultaj10@gmail.com"
    
    if not password:
        print("No password set. Skipping superuser creation.")
        return True
    
    try:
        User.objects.create_superuser(username, email, password)
        print(f"Superuser '{username}' created successfully!")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    create_superuser()
