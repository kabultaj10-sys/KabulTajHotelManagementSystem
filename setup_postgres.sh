#!/bin/bash

# PostgreSQL Setup Script for Kabul Taj Hotel Management System
echo "🚀 Setting up PostgreSQL for Kabul Taj Hotel Management System..."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew is not installed. Please install Homebrew first:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

# Install PostgreSQL
echo "📦 Installing PostgreSQL..."
brew install postgresql@15

# Start PostgreSQL service
echo "🔄 Starting PostgreSQL service..."
brew services start postgresql@15

# Wait a moment for the service to start
sleep 3

# Create database and user
echo "🗄️  Creating database and user..."

# Connect to PostgreSQL and create database and user
psql postgres << EOF
-- Create user
CREATE USER kabultaj_user WITH PASSWORD 'kabultaj_password';

-- Create database
CREATE DATABASE kabultaj_hotel OWNER kabultaj_user;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE kabultaj_hotel TO kabultaj_user;

-- Connect to the database and grant schema privileges
\c kabultaj_hotel;
GRANT ALL ON SCHEMA public TO kabultaj_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO kabultaj_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO kabultaj_user;

-- Exit
\q
EOF

echo "✅ PostgreSQL setup completed!"
echo ""
echo "📋 Database Configuration:"
echo "   Database Name: kabultaj_hotel"
echo "   Username: kabultaj_user"
echo "   Password: kabultaj_password"
echo "   Host: localhost"
echo "   Port: 5432"
echo ""
echo "🔧 Next steps:"
echo "   1. Create a .env file in your project root with the database credentials"
echo "   2. Run: python manage.py migrate"
echo "   3. Run: python manage.py createsuperuser"
echo "   4. Start your Django application"
echo ""
echo "📝 Create .env file with this content:"
echo "DB_NAME=kabultaj_hotel"
echo "DB_USER=kabultaj_user"
echo "DB_PASSWORD=kabultaj_password"
echo "DB_HOST=localhost"
echo "DB_PORT=5432"
echo "SECRET_KEY=your-secret-key-here"
echo "DEBUG=True"
