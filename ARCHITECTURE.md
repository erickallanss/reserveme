# ReserveMe Project Architecture

## Overview

This project follows a **layered architecture** with **dependency inversion** and **dependency injection**, following SOLID principles and Clean Architecture.

## Layer Structure

```
┌─────────────────────────────────────────┐
│          HTTP Request                    │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  Views (Presentation Layer)             │
│  - Thin, only input validation          │
│  - Delegate to Services                 │
│  - Return HTTP responses                │
│  - Handle caching                       │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  Services (Business Logic Layer)        │
│  - Contains ALL business logic          │
│  - Domain validations                   │
│  - Permission rules                     │
│  - Do NOT interact with DB directly     │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  Repositories (Data Access Layer)       │
│  - Interact ONLY with database          │
│  - NO business logic                    │
│  - Implement base protocols             │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│          Database (PostgreSQL)           │
└─────────────────────────────────────────┘
```

## Applied Principles

### 1. Dependency Inversion (DIP)
- Services depend on **abstractions** (Protocols), not concrete implementations
- Allows easy implementation swapping (e.g., PostgreSQL → MongoDB)

### 2. Dependency Injection (DI)
- Container manages dependency creation and configuration
- Facilitates testing (mock dependencies)
- Reduces coupling between components

### 3. Single Responsibility Principle (SRP)
- **Views**: Only HTTP request/response
- **Services**: Only business logic
- **Repositories**: Only data access

### 4. Protocol-First Design
- Contracts (Protocols) defined BEFORE implementations
- Base classes follow pattern: `Base` + domain name
- Ensures consistency and testability

## File Structure

```
reserveme/
├── models.py                    # Django Models
├── serializers.py               # DRF Serializers
├── urls.py                      # URL routing
├── permissions.py               # Custom permission classes
├── filters.py                   # Django Filter filtersets
├── cache_utils.py               # Cache utilities
├── signals.py                   # Django signals for cache invalidation
├── tasks.py                     # Celery tasks
│
├── repositories/                 # Data Access Layer
│   ├── __init__.py
│   ├── base.py                  # BaseRepository
│   ├── user_repository.py       # User operations
│   ├── hotel_repository.py      # Hotel operations
│   ├── room_repository.py       # Room operations
│   └── booking_repository.py    # Booking operations
│
├── services/                     # Business Logic Layer
│   ├── __init__.py
│   ├── auth_service.py          # Authentication logic
│   ├── hotel_service.py         # Hotel business logic
│   ├── room_service.py          # Room business logic
│   └── booking_service.py       # Booking business logic
│
├── views/                        # Presentation Layer
│   ├── __init__.py
│   ├── auth_views.py            # Authentication endpoints
│   ├── hotel_views.py           # Hotel endpoints
│   ├── room_views.py            # Room endpoints
│   └── booking_views.py         # Booking endpoints
│
├── containers/                   # Dependency Injection
│   └── __init__.py              # ApplicationContainer
│
└── tests/                        # Test Suite
    ├── factories.py             # Model factories
    ├── unit/                     # Unit tests
    │   ├── test_models.py
    │   ├── test_repositories/
    │   ├── test_services/
    │   ├── test_permissions.py
    │   ├── test_cache_utils.py
    │   ├── test_signals.py
    │   └── test_tasks.py
    └── integration/              # Integration tests
        ├── test_auth_api.py
        ├── test_hotel_api.py
        ├── test_room_api.py
        ├── test_booking_api.py
        └── test_permissions_comprehensive.py
```

## Usage Example

### 1. Define Protocol (Contract)

```python
# repositories/base.py
from typing import Generic, TypeVar, Optional, List
from django.db.models import Model

T = TypeVar('T', bound=Model)

class BaseRepository(Generic[T]):
    """Base repository with common operations."""
    
    def get_by_id(self, id: int) -> Optional[T]: ...
    def create(self, **kwargs) -> T: ...
    def update(self, instance: T, **kwargs) -> T: ...
    def delete(self, instance: T) -> None: ...
```

### 2. Implement Repository

```python
# repositories/room_repository.py
from reserveme.repositories.base import BaseRepository
from reserveme.models import Room

class RoomRepository(BaseRepository[Room]):
    """Room-specific data operations."""
    
    def __init__(self):
        super().__init__(Room)
    
    def get_by_numero(self, hotel_id: int, numero: str) -> Optional[Room]:
        return self.model.objects.filter(hotel_id=hotel_id, numero=numero).first()
```

### 3. Implement Service

```python
# services/room_service.py
from reserveme.repositories.room_repository import RoomRepository

class RoomService:
    """Room business logic."""
    
    def __init__(self, repository: RoomRepository):
        self.repository = repository
    
    def create_room(self, hotel_id: int, data: dict) -> Room:
        # Business validation
        if self.repository.get_by_numero(hotel_id, data['numero']):
            raise RoomAlreadyExistsError("Room number already exists")
        
        # Business logic
        data['hotel_id'] = hotel_id
        
        # Delegate to repository
        return self.repository.create(**data)
```

### 4. Configure DI Container

```python
# containers/__init__.py
from dependency_injector import containers, providers
from reserveme.repositories.room_repository import RoomRepository
from reserveme.services.room_service import RoomService

class ApplicationContainer(containers.DeclarativeContainer):
    # Repositories (Singleton)
    room_repository = providers.Singleton(RoomRepository)
    
    # Services (Factory)
    room_service = providers.Factory(
        RoomService,
        repository=room_repository,
    )

container = ApplicationContainer()
```

### 5. Create View

```python
# views/room_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from reserveme.containers import container

class RoomListCreateAPIView(APIView):
    def post(self, request):
        # Get service from container
        service = container.room_service()
        
        # Validate input
        serializer = RoomCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Delegate to service
        room = service.create_room(
            hotel_id=serializer.validated_data['hotel'],
            data=serializer.validated_data
        )
        
        return Response(RoomSerializer(room).data, status=201)
```

## Caching Architecture

### Cache Strategy

The system implements Redis caching with automatic invalidation:

1. **Cache Layer**: Between Views and Services
2. **Cache Backend**: Redis via `django-redis`
3. **Cache Keys**: Generated using `cache_utils.get_cache_key()`
4. **Invalidation**: Automatic via Django signals

### Cache Flow

```
Request → View → Check Cache → [Hit: Return] / [Miss: Service → DB → Cache → Return]
```

### Cache Invalidation

Django signals automatically invalidate cache on model changes:

```python
# signals.py
@receiver(post_save, sender=Hotel)
def invalidate_hotel_cache_on_save(sender, instance, **kwargs):
    invalidate_hotel_cache(instance.id)

@receiver(post_delete, sender=Hotel)
def invalidate_hotel_cache_on_delete(sender, instance, **kwargs):
    invalidate_hotel_cache(instance.id)
```

## Testing

### Repository Tests (with database)
```python
@pytest.mark.django_db
class TestRoomRepository:
    def test_create(self):
        repository = RoomRepository()
        room = repository.create(hotel_id=1, numero='101', tipo='double')
        assert room.id is not None
```

### Service Tests (with mocks)
```python
class TestRoomService:
    def test_create(self, mock_repository):
        mock_repository.get_by_numero.return_value = None
        mock_repository.create.return_value = Room(id=1)
        
        service = RoomService(mock_repository)
        result = service.create_room(1, {'numero': '101'})
        
        assert result.id == 1
```

### View Tests (integration)
```python
@pytest.mark.django_db
class TestRoomViews:
    def test_create(self, authenticated_client):
        response = authenticated_client.post('/api/v1/rooms/', data)
        assert response.status_code == 201
```

## Running Tests

```bash
# All tests
docker compose exec web pytest

# Only repository tests
docker compose exec web pytest reserveme/tests/unit/test_room_repository.py

# With coverage
docker compose exec web pytest --cov=reserveme --cov-report=html

# Specific tests
docker compose exec web pytest reserveme/tests/unit/ -v
docker compose exec web pytest reserveme/tests/integration/ -v
```

## API Endpoints

Base URL: `http://localhost:8000/api/v1/`

### Authentication (JWT)
- `POST /api/v1/auth/register/` - Register new user
- `POST /api/v1/auth/login/` - Login
- `POST /api/v1/auth/logout/` - Logout
- `POST /api/v1/auth/refresh/` - Refresh token
- `POST /api/v1/auth/verify-email/` - Verify email
- `GET /api/v1/auth/me/` - Get current user
- `PATCH /api/v1/auth/me/` - Update profile
- `POST /api/v1/auth/change-password/` - Change password

### Hotels
- `GET /api/v1/hotels/` - List hotels
- `POST /api/v1/hotels/` - Create hotel (admin)
- `GET /api/v1/hotels/{id}/` - Get hotel details
- `PATCH /api/v1/hotels/{id}/` - Update hotel (admin)
- `DELETE /api/v1/hotels/{id}/` - Delete hotel (admin)

### Rooms
- `GET /api/v1/rooms/` - List rooms
- `POST /api/v1/rooms/` - Create room (staff/admin)
- `GET /api/v1/rooms/{id}/` - Get room details
- `PATCH /api/v1/rooms/{id}/` - Update room (staff/admin)
- `DELETE /api/v1/rooms/{id}/` - Delete room (staff/admin)

### Bookings
- `GET /api/v1/bookings/` - List bookings
- `POST /api/v1/bookings/` - Create booking
- `GET /api/v1/bookings/{id}/` - Get booking details
- `DELETE /api/v1/bookings/{id}/` - Cancel booking
- `POST /api/v1/bookings/{id}/confirm/` - Confirm booking (staff)
- `POST /api/v1/bookings/{id}/checkin/` - Check-in (staff)
- `POST /api/v1/bookings/{id}/checkout/` - Check-out (staff)
- `GET /api/v1/hotels/{id}/bookings/` - List hotel bookings (staff)

### Documentation
- `GET /api/docs/` - Swagger UI
- `GET /api/redoc/` - ReDoc
- `GET /api/schema/` - OpenAPI Schema

## Best Practices Implemented

### 1. Type Hints Throughout Code
```python
def create_room(self, hotel_id: int, data: Dict[str, Any]) -> Room:
    ...
```

### 2. Complete Docstrings
```python
def create_room(self, hotel_id: int, data: Dict[str, Any]) -> Room:
    """
    Creates a new room.
    
    Args:
        hotel_id: ID of the hotel
        data: Room data
        
    Returns:
        Created room
        
    Raises:
        RoomAlreadyExistsError: If room number already exists
    """
```

### 3. Serializer Separation
- `RoomSerializer` - Read (output)
- `RoomCreateSerializer` - Create (input)
- `RoomUpdateSerializer` - Update (input)

### 4. Appropriate Error Handling
- `ValueError` → 400 Bad Request
- `PermissionError` → 403 Forbidden
- `NotFound` → 404 Not Found

### 5. API Versioning
- Versioned URLs: `/api/v1/`
- Facilitates API evolution without breaking changes

### 6. Automatic Documentation
- Swagger/OpenAPI integrated
- Automatic schemas with drf-spectacular

### 7. Caching
- Redis cache backend
- Automatic invalidation via signals
- User-specific cache keys

## Adding New Functionality

### 1. Create Model
```python
# models.py
class NewModel(models.Model):
    name = models.CharField(max_length=100)
    # ...
```

### 2. Create Repository
```python
# repositories/new_repository.py
class NewRepository(BaseRepository[NewModel]):
    def __init__(self):
        super().__init__(NewModel)
```

### 3. Create Service
```python
# services/new_service.py
class NewService:
    def __init__(self, repository: NewRepository):
        self.repository = repository
```

### 4. Register in Container
```python
# containers/__init__.py
new_repository = providers.Singleton(NewRepository)
new_service = providers.Factory(NewService, repository=new_repository)
```

### 5. Create View
```python
# views/new_views.py
class NewListCreateAPIView(APIView):
    def get(self, request):
        service = container.new_service()
        items = service.list_items()
        return Response(serializer.data)
```

### 6. Add URL
```python
# urls.py
path('items/', NewListCreateAPIView.as_view(), name='new-list'),
```

### 7. Create Tests
```python
# tests/unit/test_new_repository.py
# tests/unit/test_new_service.py
# tests/integration/test_new_api.py
```

## Useful Commands

```bash
# Create superuser
docker compose exec web python manage.py createsuperuser

# Django shell
docker compose exec web python manage.py shell

# View logs
docker compose logs -f web

# Run tests
docker compose exec web pytest -v

# Access database
docker compose exec db psql -U reserveme

# View Celery tasks
docker compose exec celery celery -A core inspect active
```

## Status

✅ Django 5.2 configured  
✅ PostgreSQL configured  
✅ Redis configured (broker, result backend, cache)  
✅ Celery + Celery Beat configured  
✅ Django REST Framework configured  
✅ JWT Authentication configured  
✅ CORS configured  
✅ API versioned (/api/v1/)  
✅ Swagger/ReDoc documentation  
✅ Layered architecture implemented  
✅ Dependency inversion/injection  
✅ Protocols for contracts  
✅ Tests configured (pytest)  
✅ Async email with Celery  
✅ Redis caching with automatic invalidation  
✅ 95% test coverage  

---

**Last Updated**: 2026-01-18
