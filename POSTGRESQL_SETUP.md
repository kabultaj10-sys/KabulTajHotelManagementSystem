# PostgreSQL Setup Guide for Kabul Taj Hotel Management System

## Prerequisites

Before setting up PostgreSQL, you need to:

1. **Update Xcode Command Line Tools** (Required for macOS):
   ```bash
   sudo rm -rf /Library/Developer/CommandLineTools
   sudo xcode-select --install
   ```
   Then restart your terminal and wait for the installation to complete.

2. **Install Homebrew** (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

## Step 1: Install PostgreSQL

```bash
# Install PostgreSQL 15
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15

# Add PostgreSQL to your PATH (add this to your ~/.zshrc or ~/.bash_profile)
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

## Step 2: Create Database and User

```bash
# Connect to PostgreSQL
psql postgres

# In the PostgreSQL prompt, run these commands:
CREATE USER kabultaj_user WITH PASSWORD 'kabultaj_password';
CREATE DATABASE kabultaj_hotel OWNER kabultaj_user;
GRANT ALL PRIVILEGES ON DATABASE kabultaj_hotel TO kabultaj_user;

# Connect to the database and grant schema privileges
\c kabultaj_hotel;
GRANT ALL ON SCHEMA public TO kabultaj_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO kabultaj_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO kabultaj_user;

# Exit PostgreSQL
\q
```

## Step 3: Install Python Dependencies

```bash
# Activate your virtual environment
source henv/bin/activate

# Install psycopg2-binary (PostgreSQL adapter for Python)
pip install psycopg2-binary
```

## Step 4: Create Environment File

Create a `.env` file in your project root with the following content:

```env
# Database Configuration
DB_NAME=kabultaj_hotel
DB_USER=kabultaj_user
DB_PASSWORD=kabultaj_password
DB_HOST=localhost
DB_PORT=5432

# Django Configuration
SECRET_KEY=your-secret-key-here-change-in-production
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
```

## Step 5: Update Django Settings

The Django settings are already configured to use PostgreSQL when the environment variables are set. The current configuration will:

- Use PostgreSQL if environment variables are provided
- Fall back to SQLite if environment variables are not set

## Step 6: Run Migrations

```bash
# Activate virtual environment
source henv/bin/activate

# Run migrations to create tables in PostgreSQL
python manage.py migrate

# Create a superuser
python manage.py createsuperuser
```

## Step 7: Test the Application

```bash
# Start the development server
python manage.py runserver 8000
```

## Database Configuration Details

### Current Settings Structure:
- **Database Engine**: Automatically switches between PostgreSQL and SQLite
- **PostgreSQL**: Used when environment variables are set
- **SQLite**: Used as fallback when environment variables are not set

### Environment Variables:
- `DB_NAME`: Database name (default: kabultaj_hotel)
- `DB_USER`: Database user (default: kabultaj_user)
- `DB_PASSWORD`: Database password (default: kabultaj_password)
- `DB_HOST`: Database host (default: localhost)
- `DB_PORT`: Database port (default: 5432)

## Troubleshooting

### Common Issues:

1. **pg_config not found**:
   - Make sure PostgreSQL is installed and in your PATH
   - Restart your terminal after installation

2. **Permission denied**:
   - Make sure the database user has proper privileges
   - Check that the database exists

3. **Connection refused**:
   - Make sure PostgreSQL service is running: `brew services start postgresql@15`
   - Check if the port 5432 is available

4. **Xcode Command Line Tools error**:
   - Update Command Line Tools as shown in Prerequisites
   - Restart terminal after installation

### Useful Commands:

```bash
# Check PostgreSQL status
brew services list | grep postgresql

# Start PostgreSQL
brew services start postgresql@15

# Stop PostgreSQL
brew services stop postgresql@15

# Connect to PostgreSQL
psql -U kabultaj_user -d kabultaj_hotel

# List databases
psql -U kabultaj_user -l
```

## Migration from SQLite to PostgreSQL

If you have existing data in SQLite and want to migrate to PostgreSQL:

1. **Export data from SQLite**:
   ```bash
   python manage.py dumpdata --natural-foreign --natural-primary > data.json
   ```

2. **Switch to PostgreSQL** (follow steps above)

3. **Import data to PostgreSQL**:
   ```bash
   python manage.py loaddata data.json
   ```

## Production Considerations

For production deployment:

1. **Change default passwords**
2. **Use environment variables for sensitive data**
3. **Configure proper database permissions**
4. **Set up database backups**
5. **Use connection pooling**
6. **Enable SSL connections**

## Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are met
3. Ensure PostgreSQL service is running
4. Check database user permissions
