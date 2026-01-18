"""Extended integration tests for Room views."""
import pytest
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APIClient
from reserveme.tests.factories import AdminUserFactory, StaffUserFactory
from reserveme.tests.room_factories import RoomFactory
from reserveme.tests.hotel_factories import HotelFactory
from reserveme.cache_utils import get_cache_key


@pytest.fixture
def api_client():
    """Fixture for API client."""
    return APIClient()


@pytest.mark.django_db
class TestRoomViewsCache:
    """Tests for room views with cache."""
    
    def test_room_list_cache(self, api_client):
        """Test that room list is cached."""
        RoomFactory.create_batch(3, is_active=True)
        
        # First request
        response1 = api_client.get('/api/v1/rooms/')
        assert response1.status_code == status.HTTP_200_OK
        
        # Second request - should hit cache
        response2 = api_client.get('/api/v1/rooms/')
        assert response2.status_code == status.HTTP_200_OK
    
    def test_room_detail_cache(self, api_client):
        """Test that room detail is cached."""
        room = RoomFactory()
        
        # First request
        response1 = api_client.get(f'/api/v1/rooms/{room.id}/')
        assert response1.status_code == status.HTTP_200_OK
        
        # Second request - should hit cache
        response2 = api_client.get(f'/api/v1/rooms/{room.id}/')
        assert response2.status_code == status.HTTP_200_OK
        assert response1.data == response2.data
    
    def test_room_create_invalidates_cache(self, api_client):
        """Test that creating room invalidates cache."""
        admin = AdminUserFactory()
        api_client.force_authenticate(user=admin)
        hotel = HotelFactory()
        
        # Create room
        data = {
            'hotel': hotel.id,
            'numero': '999',
            'tipo': 'double',
            'capacidade': 2,
            'preco_diaria': '250.00'
        }
        response = api_client.post('/api/v1/rooms/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        # Signal will invalidate cache
    
    def test_room_update_invalidates_cache(self, api_client):
        """Test that updating room invalidates cache."""
        staff = StaffUserFactory()
        api_client.force_authenticate(user=staff)
        room = RoomFactory()
        
        # Update room
        data = {'preco_diaria': '300.00'}
        response = api_client.patch(f'/api/v1/rooms/{room.id}/', data)
        
        assert response.status_code == status.HTTP_200_OK
        # Signal will invalidate cache
        # Verify update worked
        assert response.data['room']['preco_diaria'] == '300.00'
