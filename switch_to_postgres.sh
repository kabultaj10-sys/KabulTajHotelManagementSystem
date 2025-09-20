#!/bin/bash

# Script to switch from SQLite to PostgreSQL
echo "🔄 Switching to PostgreSQL database..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Database Configuration
DB_NAME=kabultaj_hotel
DB_USER=kabultaj_user
DB_PASSWORD=kabultaj_password
DB_HOST=localhost
DB_PORT=5432

# Django Configuration
SECRET_KEY=django-insecure-your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Static and Media URLs
STATIC_URL=/static/
MEDIA_URL=/media/

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EOF
    echo "✅ .env file created!"
else
    echo "✅ .env file already exists!"
fi

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "❌ PostgreSQL is not running. Please start it first:"
    echo "   brew services start postgresql@15"
    exit 1
fi

# Check if database exists
if ! psql -h localhost -U kabultaj_user -d kabultaj_hotel -c "SELECT 1;" > /dev/null 2>&1; then
    echo "❌ Database 'kabultaj_hotel' or user 'kabultaj_user' does not exist."
    echo "   Please run the PostgreSQL setup first:"
    echo "   ./setup_postgres.sh"
    exit 1
fi

# Activate virtual environment and run migrations
echo "🔄 Activating virtual environment..."
source henv/bin/activate

echo "🔄 Running migrations..."
python manage.py migrate

echo "✅ Successfully switched to PostgreSQL!"
echo ""
echo "🚀 You can now start the server:"
echo "   python manage.py runserver 8000"
