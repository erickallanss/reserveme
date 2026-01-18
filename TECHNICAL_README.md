# Technical Documentation - ReserveMe API

This document provides detailed technical information about the ReserveMe API implementation.

## Table of Contents

1. [Technology Stack](#technology-stack)
2. [Architecture Overview](#architecture-overview)
3. [Project Structure](#project-structure)
4. [Authentication & Authorization](#authentication--authorization)
5. [Database Models](#database-models)
6. [API Design](#api-design)
7. [Caching Strategy](#caching-strategy)
8. [Background Tasks](#background-tasks)
9. [Testing Strategy](#testing-strategy)
10. [Deployment](#deployment)
11. [Performance Considerations](#performance-considerations)

---

## Technology Stack

### Core Framework
- **Django 5.2.10** - Web framework
- **Django REST Framework 3.14+** - API framework
- **Python 3.11+** - Programming language

### Database
- **PostgreSQL 15** - Primary database
- **Redis 7** - Cache backend and Celery broker

### Task Queue
- **Celery 5.3+** - Distributed task queue
- **Celery Beat** - Periodic task scheduler

### Authentication
- **djangorestframework-simplejwt 5.3+** - JWT authentication

### Documentation
- **drf-spectacular 0.27+** - OpenAPI 3.0 schema generation

### Testing
- **pytest 7.4+** - Testing framework
- **pytest-django** - Django integration
- **pytest-cov** - Coverage reporting
- **factory-boy** - Test data factories
- **faker** - Fake data generation

### Other
- **django-cors-headers** - CORS handling
- **django-filter** - Advanced filtering
- **django-redis** - Redis cache backend
- **Pillow** - Image processing
- **dependency-injector** - Dependency injection

---

## Architecture Overview

The project follows a **layered architecture** with **dependency inversion** and **dependency injection**, following SOLID principles and Clean Architecture.

### Layer Structure

```
┌─────────────────────────────────────────┐
│          HTTP Request                    │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  Views (Presentation Layer)             │
│  - Thin, only input validation         │
│  - Delegate to Services                │
│  - Return HTTP responses               │
│  - Handle caching                      │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  Services (Business Logic Layer)       │
│  - Contains ALL business logic         │
│  - Domain validations                  │
│  - Permission rules                    │
│  - Do NOT interact with DB directly    │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  Repositories (Data Access Layer)      │
│  - Interact ONLY with database         │
│  - NO business logic                   │
│  - Implement base protocols           │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│          Database (PostgreSQL)          │
└─────────────────────────────────────────┘
```

### Design Principles

1. **Dependency Inversion (DIP)**
   - Services depend on abstractions (Protocols), not concrete implementations
   - Easy to swap implementations (e.g., PostgreSQL → MongoDB)

2. **Dependency Injection (DI)**
   - Container manages dependency creation and configuration
   - Facilitates testing (mock dependencies)
   - Reduces coupling between components

3. **Single Responsibility Principle (SRP)**
   - **Views**: Only HTTP request/response
   - **Services**: Only business logic
   - **Repositories**: Only data access

4. **Separation of Concerns**
   - Clear boundaries between layers
   - Each layer has a single responsibility

---

## Project Structure

```
reserveme/
├── models.py                    # Django Models (User, Hotel, Room, Booking)
├── serializers.py               # DRF Serializers
├── urls.py                      # URL routing
├── permissions.py               # Custom permission classes
├── filters.py                   # Django Filter filtersets
├── cache_utils.py              # Cache key generation and invalidation
├── signals.py                   # Django signals for cache invalidation
├── tasks.py                     # Celery tasks
│
├── repositories/                # Data Access Layer
│   ├── __init__.py
│   ├── base.py                 # BaseRepository with common operations
│   ├── user_repository.py      # User data operations
│   ├── hotel_repository.py     # Hotel data operations
│   ├── room_repository.py      # Room data operations
│   └── booking_repository.py   # Booking data operations
│
├── services/                    # Business Logic Layer
│   ├── __init__.py
│   ├── auth_service.py         # Authentication logic
│   ├── hotel_service.py        # Hotel business logic
│   ├── room_service.py         # Room business logic
│   └── booking_service.py      # Booking business logic
│
├── views/                       # Presentation Layer
│   ├── __init__.py
│   ├── auth_views.py          # Authentication endpoints
│   ├── hotel_views.py          # Hotel endpoints
│   ├── room_views.py           # Room endpoints
│   └── booking_views.py        # Booking endpoints
│
├── containers/                  # Dependency Injection
│   └── __init__.py             # ApplicationContainer
│
└── tests/                       # Test Suite
    ├── factories.py            # Model factories
    ├── unit/                   # Unit tests
    │   ├── test_models.py
    │   ├── test_repositories/
    │   ├── test_services/
    │   ├── test_permissions.py
    │   ├── test_cache_utils.py
    │   ├── test_signals.py
    │   └── test_tasks.py
    └── integration/            # Integration tests
        ├── test_auth_api.py
        ├── test_hotel_api.py
        ├── test_room_api.py
        ├── test_booking_api.py
        └── test_permissions_comprehensive.py
```

---

## Authentication & Authorization

### JWT Authentication

The system uses **JWT (JSON Web Tokens)** with HTTP-only cookies for security.

#### Token Storage
- **Access Token**: Stored in HTTP-only cookie (`access_token`)
- **Refresh Token**: Stored in HTTP-only cookie (`refresh_token`)
- **Lifetime**: Access token (15 minutes), Refresh token (7 days)

#### Authentication Flow

1. **Registration**
   - User registers with email, password, CPF, etc.
   - Email verification token is generated
   - Verification email sent asynchronously via Celery

2. **Email Verification**
   - User clicks verification link
   - Email is marked as verified
   - User can now login

3. **Login**
   - User provides email and password
   - System validates credentials
   - JWT tokens generated and set as HTTP-only cookies
   - User information included in token payload

4. **Token Refresh**
   - Client requests refresh using refresh token
   - New access token generated
   - Cookies updated automatically

### Authorization Levels

#### 1. Admin (`role='admin'`)
- Full system access
- Can create/update/delete hotels
- Can create/update/delete rooms
- Can view all bookings
- Can manage users (internal register)

#### 2. Staff (`role='staff'`)
- Can create/update/delete rooms
- Can view all bookings
- Can confirm bookings
- Can perform check-in/check-out
- Cannot manage hotels

#### 3. Customer (`role='customer'`)
- Can create bookings
- Can view only their own bookings
- Can cancel their own bookings
- Cannot access admin/staff operations

### Permission Classes

```python
# reserveme/permissions.py

class IsAdmin(BasePermission):
    """Only admin users have access."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin

class IsStaffOrAdmin(BasePermission):
    """Staff and admin users have access."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff_member
```

### Custom User Model

The system uses a custom User model extending Django's `AbstractUser`:

```python
class User(AbstractUser):
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=11, unique=True)
    telefone = models.CharField(max_length=20)
    data_nascimento = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/%Y/%m/')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True)
```

---

## Database Models

### User Model
- **Fields**: email, cpf, telefone, data_nascimento, avatar, role, email_verified
- **Relationships**: One-to-many with Booking
- **Indexes**: email (unique), cpf (unique)

### Hotel Model
- **Fields**: nome, descricao, logo, endereco, telefone, email, horario_checkin, horario_checkout, is_active
- **Relationships**: One-to-many with Room
- **Soft Delete**: `is_active` flag

### Room Model
- **Fields**: hotel, numero, tipo, descricao, capacidade, preco_diaria, amenities, is_active
- **Relationships**: Many-to-one with Hotel, One-to-many with Booking
- **Constraints**: Unique (hotel, numero)
- **Soft Delete**: `is_active` flag

### Booking Model
- **Fields**: user, room, codigo_reserva, data_checkin, data_checkout, numero_hospedes, status, preco_total
- **Relationships**: Many-to-one with User and Room
- **Status**: pending, confirmed, checked_in, checked_out, cancelled
- **Auto-generated**: codigo_reserva (RES-YYYYMMDD-XXXX)

---

## API Design

### RESTful Principles

The API follows RESTful conventions:

- **GET** - Retrieve resources
- **POST** - Create resources
- **PUT/PATCH** - Update resources
- **DELETE** - Delete resources (soft delete)

### API Versioning

- Base URL: `/api/v1/`
- Versioned to allow future breaking changes

### Response Format

#### Success Response
```json
{
  "message": "Operation successful",
  "data": { ... }
}
```

#### Error Response
```json
{
  "error": "Error message",
  "details": { ... }
}
```

### Pagination

All list endpoints support pagination:
- Default page size: 20
- Configurable via `page_size` query parameter
- Response includes: `count`, `next`, `previous`, `results`

### Filtering & Search

- **Django Filter**: Advanced filtering via query parameters
- **Search**: Full-text search on relevant fields
- **Ordering**: Sortable via `ordering` parameter

Example:
```
GET /api/v1/rooms/?hotel=1&tipo=double&ordering=preco_diaria&search=luxo
```

### Serializers

- **Read Serializers**: Full model representation
- **Write Serializers**: Input validation and transformation
- **Nested Serializers**: Related object representation

---

## Caching Strategy

### Cache Backend

- **Redis** as cache backend via `django-redis`
- **Key Prefix**: `reserveme`
- **Default TTL**: 5 minutes (300 seconds)

### Cache Keys

Cache keys are generated using a utility function:

```python
def get_cache_key(resource: str, action: str, **kwargs) -> str:
    """
    Generate cache key.
    
    Examples:
    - hotels:list
    - hotels:list:admin:True
    - hotel:1
    - rooms:list:staff:True
    - bookings:list:user:123
    """
```

### Cached Endpoints

1. **Hotel List** (`GET /api/v1/hotels/`)
   - Cached for 5 minutes
   - Separate cache for admin (sees all) vs public (sees only active)

2. **Hotel Detail** (`GET /api/v1/hotels/{id}/`)
   - Cached per hotel ID
   - Invalidated on update/delete

3. **Room List** (`GET /api/v1/rooms/`)
   - Cached for 5 minutes
   - Separate cache for staff (sees all) vs public (sees only active)
   - Cache key includes filter parameters

4. **Room Detail** (`GET /api/v1/rooms/{id}/`)
   - Cached per room ID
   - Invalidated on update/delete

5. **Booking List** (`GET /api/v1/bookings/`)
   - Cached for 5 minutes
   - Separate cache per user (customers see only their bookings)
   - Staff/admin cache includes all bookings

### Cache Invalidation

Cache invalidation is handled automatically via Django signals:

```python
# reserveme/signals.py

@receiver(post_save, sender=Hotel)
def invalidate_hotel_cache(sender, instance, **kwargs):
    """Invalidate hotel-related cache on save."""
    invalidate_hotel_cache(instance.id)

@receiver(post_delete, sender=Hotel)
def invalidate_hotel_cache_on_delete(sender, instance, **kwargs):
    """Invalidate hotel-related cache on delete."""
    invalidate_hotel_cache(instance.id)
```

Signals are registered for:
- Hotel create/update/delete
- Room create/update/delete
- Booking create/update/delete

---

## Background Tasks

### Celery Configuration

- **Broker**: Redis
- **Result Backend**: Redis
- **Timezone**: America/Sao_Paulo

### Async Tasks

#### 1. Email Tasks

```python
@shared_task
def send_template_email_async(
    subject: str,
    template_name: str,
    context: dict,
    recipient_list: list
):
    """Send email with template asynchronously."""
```

**Used for**:
- Email verification
- Booking confirmation
- Booking cancellation
- Booking expiration notification

#### 2. Scheduled Tasks (Celery Beat)

**Release Expired Bookings**
- **Schedule**: Every hour (`crontab(minute='0', hour='*/1')`)
- **Task**: `reserveme.tasks.release_expired_bookings_task`
- **Action**: 
  - Finds pending bookings with past check-in date
  - Cancels them automatically
  - Sends notification email

### Task Retry

- **Max Retries**: 3
- **Retry Delay**: Exponential backoff
- **Retry on**: Connection errors, SMTP errors

---

## Testing Strategy

### Test Coverage

- **Current Coverage**: 95%
- **Target**: Maintain above 90%

### Test Structure

#### Unit Tests
- **Location**: `reserveme/tests/unit/`
- **Scope**: Individual components (models, services, repositories)
- **Mocks**: Used for external dependencies

#### Integration Tests
- **Location**: `reserveme/tests/integration/`
- **Scope**: Full request/response cycle
- **Database**: Uses test database

### Test Categories

1. **Model Tests**
   - Field validations
   - Methods and properties
   - Relationships

2. **Repository Tests**
   - CRUD operations
   - Query methods
   - Edge cases

3. **Service Tests**
   - Business logic
   - Validations
   - Error handling

4. **View Tests**
   - HTTP status codes
   - Response format
   - Permissions
   - Cache behavior

5. **Permission Tests**
   - Role-based access
   - Unauthorized access
   - Owner-only access

### Running Tests

```bash
# All tests
make test

# With coverage
make test-cov

# Unit tests only
make test-unit

# Integration tests only
make test-integration

# Specific test file
docker compose exec web pytest reserveme/tests/unit/test_booking_service.py -v
```

### Test Factories

Using `factory-boy` for test data generation:

```python
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    cpf = factory.Sequence(lambda n: f'{n:011d}')
```

---

## Deployment

### Docker Configuration

#### Services

1. **web** (Django)
   - Port: 8000
   - Command: `python manage.py runserver 0.0.0.0:8000`
   - Depends on: db, redis, mailpit

2. **db** (PostgreSQL)
   - Port: 5432
   - Volume: `postgres_data`
   - Health check: `pg_isready`

3. **redis** (Redis)
   - Port: 6379
   - Health check: `redis-cli ping`

4. **celery** (Celery Worker)
   - Command: `celery -A core worker --loglevel=info`
   - Depends on: db, redis, web, mailpit

5. **celery-beat** (Celery Beat)
   - Command: `celery -A core beat --loglevel=info`
   - Depends on: db, redis, web, mailpit

6. **mailpit** (Email Testing)
   - Ports: 8025 (Web UI), 1025 (SMTP)
   - Volume: `mailpit_data`

### Environment Variables

```bash
DEBUG=1
DATABASE_URL=postgresql://reserveme:reserveme@db:5432/reserveme
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
CACHE_URL=redis://redis:6379/1
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=mailpit
EMAIL_PORT=1025
SECRET_KEY=your-secret-key
```

### Production Considerations

1. **Security**
   - Set `DEBUG=0`
   - Use strong `SECRET_KEY`
   - Configure `ALLOWED_HOSTS`
   - Use HTTPS
   - Secure database credentials

2. **Performance**
   - Use production WSGI server (Gunicorn/uWSGI)
   - Configure Redis for production
   - Set up database connection pooling
   - Enable static file serving (Nginx/CDN)

3. **Monitoring**
   - Set up logging
   - Monitor Celery tasks
   - Database query monitoring
   - Cache hit/miss metrics

4. **Email**
   - Replace Mailpit with production SMTP
   - Configure email templates
   - Set up email queue monitoring

---

## Performance Considerations

### Database Optimization

1. **Indexes**
   - Email (unique)
   - CPF (unique)
   - Hotel-Room number (unique together)
   - Booking dates (for availability queries)

2. **Query Optimization**
   - Use `select_related()` for foreign keys
   - Use `prefetch_related()` for many-to-many
   - Avoid N+1 queries

3. **Pagination**
   - All list endpoints paginated
   - Default page size: 20

### Caching

1. **Cache Strategy**
   - Cache frequently accessed data
   - Invalidate on updates
   - Use appropriate TTL

2. **Cache Keys**
   - Include user context (for personalized data)
   - Include filter parameters
   - Keep keys consistent

### Async Processing

1. **Email Sending**
   - All emails sent asynchronously
   - Prevents blocking HTTP requests

2. **Scheduled Tasks**
   - Heavy operations run in background
   - Scheduled during off-peak hours

---

## Additional Resources

- **Architecture Documentation**: See `ARCHITECTURE.md`
- **API Testing Guide**: See `API_TESTING_GUIDE.md`
- **Postman Collection**: See `postman/README.md`

---

**Last Updated**: 2026-01-18
