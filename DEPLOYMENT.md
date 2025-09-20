# Railway Deployment Guide

## Environment Variables Required

Set these environment variables in your Railway project:

### Required Variables:
```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-railway-app.railway.app,localhost,127.0.0.1
```

### Database Variables (Railway will provide these):
```
DB_NAME=railway
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=containers-us-west-xxx.railway.app
DB_PORT=5432
```

### Optional Variables:
```
STATIC_URL=/static/
MEDIA_URL=/media/
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

## Deployment Steps

1. **Connect to Railway**: Link your GitHub repository to Railway
2. **Add PostgreSQL**: Add a PostgreSQL database service
3. **Set Environment Variables**: Add the required environment variables
4. **Deploy**: Railway will automatically deploy your Django application

## Features Included

- ✅ Django 4.2.7
- ✅ PostgreSQL database
- ✅ Static file serving with WhiteNoise
- ✅ Gunicorn WSGI server
- ✅ Automatic migrations
- ✅ Static file collection
- ✅ Production-ready configuration

## Post-Deployment

1. Create a superuser: `python manage.py createsuperuser`
2. Access admin panel at: `https://your-app.railway.app/admin/`
3. Your hotel management system will be live!
