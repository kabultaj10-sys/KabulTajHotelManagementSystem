#!/bin/bash

# Script to switch from PostgreSQL to SQLite
echo "🔄 Switching to SQLite database..."

# Backup .env file if it exists
if [ -f .env ]; then
    echo "📦 Backing up .env file to .env.backup..."
    cp .env .env.backup
fi

# Remove .env file to use SQLite
echo "🗑️  Removing .env file to use SQLite..."
rm -f .env

# Activate virtual environment and run migrations
echo "🔄 Activating virtual environment..."
source henv/bin/activate

echo "🔄 Running migrations..."
python manage.py migrate

echo "✅ Successfully switched to SQLite!"
echo ""
echo "🚀 You can now start the server:"
echo "   python manage.py runserver 8000"
echo ""
echo "💡 To switch back to PostgreSQL, run:"
echo "   ./switch_to_postgres.sh"
