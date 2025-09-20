#!/bin/bash

# Navigate to Django project directory
cd Desktop/Computer_💻Programminng_😎/projects/KabulTajHotelManagementSystem

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn (replace with your actual project name)
gunicorn KabulTajHotelManagementSystem.wsgi:application --bind 0.0.0.0:$PORT