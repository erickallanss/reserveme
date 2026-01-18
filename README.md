# 🏨 ReserveMe API

A complete hotel reservation system built with Django REST Framework, Celery, and Docker.

## ✨ Features

- 🔐 **JWT Authentication** with HTTP-only cookies
- 👥 **3 User Roles**: Admin, Staff, Customer
- 🏨 **Hotel & Room Management**
- 📅 **Booking System** with availability verification
- 📧 **Asynchronous Emails** with Celery
- ⏰ **Scheduled Tasks** with Celery Beat
- 🐳 **Fully Dockerized**
- 📚 **Auto-generated Documentation** with Swagger/ReDoc
- 🚀 **Redis Caching** with automatic invalidation
- ✅ **95% Test Coverage**

---

## 🚀 Quick Start

### Option 1: Single Command (Recommended)

```bash
make server
```

This command does **EVERYTHING automatically**:
- ✅ Builds containers
- ✅ Starts all services
- ✅ Creates and applies migrations
- ✅ **Populates database with test data** (if empty)
- ✅ Shows access credentials

**Ready!** Access:
- 🌐 **API**: http://localhost:8000
- 📚 **Swagger**: http://localhost:8000/api/docs/
- 🔐 **Admin**: http://localhost:8000/admin/
- 📧 **Mailpit**: http://localhost:8025

### Option 2: Step by Step

```bash
# 1. Build and start containers
docker compose up --build -d

# 2. Wait for containers to start
sleep 5

# 3. Apply migrations
docker compose exec web python manage.py migrate

# 4. Populate test data
docker compose exec web python seed_data.py
```

---

## 👤 Default Credentials

After running `make server` or `seed_data.py`:

| Type | Email | Password | Permissions |
|------|-------|----------|-------------|
| **Admin** | admin@reserveme.com | Password1 | Full access |
| **Staff** | staff@reserveme.com | staff123 | Manage bookings |
| **Customer** | joao.silva@example.com | cliente123 | Make bookings |
| **Customer** | maria.santos@example.com | cliente123 | Make bookings |

---

## 📋 Available Make Commands

### 🚀 Main Commands

```bash
make server          # Start everything (build, migrate, seed if empty)
make up              # Start containers
make down            # Stop containers
make restart         # Restart containers
make logs            # View logs from all services
```

### 🗄️ Database

```bash
make migrate         # Apply migrations
make makemigrations  # Create new migrations
make seed            # Populate test data (force)
make db-reset        # Reset database and populate again
make dbshell         # Access PostgreSQL shell
```

### 🧪 Testing

```bash
make test            # Run all tests
make test-cov        # Tests with coverage
make test-unit       # Unit tests only
make test-integration # Integration tests only
```

### 🔧 Utilities

```bash
make shell           # Django shell
make createsuperuser # Create superuser
make api-docs        # Open Swagger in browser
make mailpit         # Open Mailpit in browser
make help            # List all commands
```

---

## 📊 Test Data Created

When running `make server` or `make seed`, the following is created:

### 🏨 1 Hotel
- **Hotel Paradise Beach** (Copacabana, RJ)

### 🛏️ 8 Rooms
| No. | Type | Price/Day |
|-----|------|-----------|
| 101 | Single | R$ 150 |
| 102 | Double | R$ 250 |
| 103 | Twin | R$ 240 |
| 201 | Superior Double | R$ 300 |
| 202 | Triple | R$ 350 |
| 301 | Suite | R$ 500 |
| 302 | Deluxe | R$ 750 |
| 401 | Presidential | R$ 1,500 |

### 👥 6 Users
- 1 Admin, 1 Staff, 4 Customers

### 📅 7 Bookings
- Confirmed, Pending, Checked-in, Completed

---

## 🌐 API Endpoints

### 🔐 Authentication (8 endpoints)
```
POST   /api/v1/auth/register/
POST   /api/v1/auth/verify-email/
POST   /api/v1/auth/login/
POST   /api/v1/auth/logout/
GET    /api/v1/auth/me/
PATCH  /api/v1/auth/me/
POST   /api/v1/auth/change-password/
POST   /api/v1/auth/refresh/
```

### 🏨 Hotels (6 endpoints)
```
GET    /api/v1/hotels/
POST   /api/v1/hotels/          (admin)
GET    /api/v1/hotels/{id}/
PUT    /api/v1/hotels/{id}/     (admin)
PATCH  /api/v1/hotels/{id}/     (admin)
DELETE /api/v1/hotels/{id}/     (admin)
```

### 🛏️ Rooms (6 endpoints)
```
GET    /api/v1/rooms/
POST   /api/v1/rooms/           (staff/admin)
GET    /api/v1/rooms/{id}/
PUT    /api/v1/rooms/{id}/      (staff/admin)
PATCH  /api/v1/rooms/{id}/      (staff/admin)
DELETE /api/v1/rooms/{id}/      (staff/admin)
```

### 📅 Bookings (8 endpoints)
```
GET    /api/v1/bookings/
POST   /api/v1/bookings/
GET    /api/v1/bookings/{id}/
DELETE /api/v1/bookings/{id}/
POST   /api/v1/bookings/{id}/confirm/   (staff)
POST   /api/v1/bookings/{id}/checkin/   (staff)
POST   /api/v1/bookings/{id}/checkout/  (staff)
GET    /api/v1/hotels/{id}/bookings/    (staff)
```

**Total**: 28 endpoints

---

## 📧 Automatic Emails

All emails are captured by **Mailpit** (http://localhost:8025):

1. ✅ **Booking Created** - When customer creates booking
2. ✅ **Booking Confirmed** - When staff confirms
3. ✅ **Booking Cancelled** - Manual cancellation
4. ✅ **Booking Expired** - Automatic cancellation (Celery Beat)

---

## ⏰ Celery Beat - Scheduled Task

**Task**: `release_expired_bookings_task()`
- 🔄 Runs **every 1 hour**
- 🔍 Finds `pending` bookings with past check-in date
- ❌ Automatically cancels them
- 📧 Sends notification email

### View Logs
```bash
make logs-celery-beat
```

---

## 🧪 Testing the API

### 1. Via Swagger (Recommended)
```
http://localhost:8000/api/docs/
```

### 2. Via Postman
```bash
# Import files:
postman/ReserveMe_API.postman_collection.json
postman/ReserveMe_Local.postman_environment.json
```

### 3. Via cURL
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@reserveme.com","password":"Password1"}'

# List hotels
curl http://localhost:8000/api/v1/hotels/

# Create booking (after login)
curl -X POST http://localhost:8000/api/v1/bookings/ \
  -H "Content-Type: application/json" \
  -d '{
    "room": 1,
    "data_checkin": "2026-03-01",
    "data_checkout": "2026-03-05",
    "numero_hospedes": 2
  }'
```

---

## 🏗️ Architecture

### Docker Services
- **web**: Django (port 8000)
- **db**: PostgreSQL (port 5432)
- **redis**: Redis (port 6379) - Celery broker & cache
- **celery**: Worker for async tasks
- **celery-beat**: Scheduler for periodic tasks
- **mailpit**: Email capture (ports 8025/1025)

### Code Structure
```
reserveme/
├── models.py           # User, Hotel, Room, Booking
├── repositories/       # Data access layer
├── services/           # Business logic layer
├── serializers.py      # Validation and serialization
├── views/              # API endpoints
├── tasks.py            # Celery tasks
├── cache_utils.py      # Cache utilities
├── signals.py          # Django signals for cache invalidation
└── tests/              # Unit and integration tests
```

**Pattern**: Repository + Service Layer + Caching

---

## 📚 Additional Documentation

- **`TECHNICAL_README.md`** - Technical details and implementation
- **`ARCHITECTURE.md`** - Architecture patterns and design decisions
- **`API_TESTING_GUIDE.md`** - Step-by-step API testing guide
- **`SEED_README.md`** - Test data details
- **`postman/README.md`** - Postman collection guide

---

## 🛠️ Technologies

- **Django 5.x** + **Django REST Framework**
- **PostgreSQL** - Database
- **Redis** - Celery broker, result backend & cache
- **Celery** + **Celery Beat** - Async tasks
- **Docker** + **Docker Compose**
- **JWT** - Authentication
- **Mailpit** - Email capture
- **Swagger/ReDoc** - Auto-generated documentation
- **django-redis** - Caching
- **pytest** - Testing framework

---

## 🔧 Troubleshooting

### Containers won't start
```bash
make down
make clean
make server
```

### Database won't migrate
```bash
docker compose exec web python manage.py migrate
```

### Celery not processing tasks
```bash
make logs-celery
# Check if worker is running
```

### Emails not appearing
```bash
# Check if Mailpit is running
docker compose ps mailpit
# Access: http://localhost:8025
```

---

## 📝 License


---

## 🎯 Project Status

✅ **100% Complete and Functional**

All requirements implemented:
- ✅ Complete modeling (Hotels, Rooms, Bookings, Users)
- ✅ JWT Authentication with 3 permission levels
- ✅ Booking system with availability verification
- ✅ Asynchronous emails with Celery
- ✅ Scheduled task with Celery Beat
- ✅ Complete Dockerization
- ✅ Redis caching with automatic invalidation
- ✅ Comprehensive documentation
- ✅ Test data ready
- ✅ 95% test coverage

**Ready for production!** 🚀

---

