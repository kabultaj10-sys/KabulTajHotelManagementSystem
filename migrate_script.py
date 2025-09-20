#!/usr/bin/env python
import os
import sys
import django
from django.core.management import execute_from_command_line

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel_project.settings')
django.setup()

# Run makemigrations with default answers
sys.argv = ['manage.py', 'makemigrations', '--noinput']
execute_from_command_line(sys.argv) 