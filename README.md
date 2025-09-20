# Kabul Taj Hotel Management System

A robust, fully server-rendered Django backend for managing hotel operations including rooms, guests, bookings, food services, inventory, conference rooms, billing, and staff.

## Features

- **Role-based Access Control**: Admin, Manager, Receptionist, Housekeeping, Restaurant Staff, Conference Staff
- **Comprehensive Hotel Management**: Rooms, Guests, Bookings, Restaurant, Conference Rooms, Billing
- **Audit Trail**: Complete history tracking with django-simple-history
- **Background Tasks**: Celery integration for scheduled jobs
- **PDF Generation**: ReportLab for invoices and reports
- **Image Handling**: Pillow for image uploads
- **Modern UI**: Tailwind CSS integration

## Technology Stack

- **Django 4.2+ (LTS)**
- **PostgreSQL** (Production)
- **SQLite** (Development)
- **Redis + Celery** (Background jobs)
- **Pillow** (Image uploads)
- **ReportLab** (PDF generation)
- **django-simple-history** (Audit trails)
- **Tailwind CSS** (Styling)

## Project Structure

```
hotel_project/
├── config/                 # Configuration files
├── apps/                   # Django applications
│   ├── users/             # Auth, role-based access
│   ├── staff/             # Basic staff profile management
│   ├── guests/            # Guest records
│   ├── rooms/             # Room types, status
│   ├── bookings/          # Bookings, check-in/out
│   ├── restaurant/        # Menu, tables, orders
│   ├── conference/        # Conference room bookings
│   ├── billing/           # Invoices and payment logging
├── templates/             # HTML templates
├── static/                # Static files (CSS, JS, images)
├── media/                 # User uploaded files
├── requirements.txt       # Python dependencies
└── .env                  # Environment variables
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd KabulTajHotelManagementSystem
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv henv
   source henv/bin/activate  # On Windows: henv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## Development Setup

### Prerequisites
- Python 3.9+
- Redis (for Celery)
- PostgreSQL (for production)

### Environment Variables
Create a `.env` file with the following variables:
```
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Usage

### Admin Panel
Access the admin panel at `http://localhost:8000/admin/`

### User Roles
- **Administrator**: Full access to all features
- **Manager**: Management-level access
- **Receptionist**: Booking and guest management
- **Housekeeping**: Room management
- **Restaurant Staff**: Restaurant operations
- **Conference Staff**: Conference room management

### Celery Tasks
Start Celery worker:
```bash
celery -A hotel_project worker -l info
```

Start Celery beat (for scheduled tasks):
```bash
celery -A hotel_project beat -l info
```

## Development Parts

This project is developed in 16 parts:

1. **Project Initialization** ✅
   - Django setup with environment-specific settings
   - PostgreSQL and Redis integration
   - Celery config for background jobs
   - Role-based user model (Admin, Receptionist, Manager)

2. **Staff Management** (Next)
   - Staff profiles and schedules
   - Department management
   - Performance tracking

3. **Guest Management**
   - Guest registration and profiles
   - Guest history and preferences
   - VIP guest handling

4. **Room Management**
   - Room types and categories
   - Room status tracking
   - Maintenance scheduling

5. **Booking System**
   - Reservation management
   - Check-in/check-out process
   - Booking calendar

6. **Restaurant Management**
   - Menu management
   - Table reservations
   - Order processing

7. **Conference Room Management**
   - Conference room bookings
   - Equipment management
   - Event planning

8. **Billing System**
   - Invoice generation
   - Payment processing
   - Financial reporting

9. **Inventory Management**
   - Stock tracking
   - Supplier management
   - Reorder alerts

10. **Reporting System**
    - Custom reports
    - PDF generation
    - Data analytics

11. **API Development**
    - RESTful API endpoints
    - API documentation
    - Authentication

12. **Frontend Integration**
    - Tailwind CSS setup
    - Responsive design
    - Modern UI components

13. **Security Implementation**
    - Role-based permissions
    - Data encryption
    - Audit logging

14. **Testing Suite**
    - Unit tests
    - Integration tests
    - Performance testing

15. **Deployment Configuration**
    - Production settings
    - Docker configuration
    - CI/CD pipeline

16. **Documentation & Training**
    - User manuals
    - API documentation
    - Training materials

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team. 