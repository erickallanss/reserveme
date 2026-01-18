"""Integration tests for room create error handling."""
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from reserveme.tests.factories import AdminUserFactory
from reserveme.tests.room_factories import RoomFactory
from reserveme.tests.hotel_factories import HotelFactory


@pytest.fixture
def api_client():
    """Fixture for API client."""
    return APIClient()


@pytest.mark.django_db
class TestRoomCreateErrors:
    """Tests for room create error handling."""
    
    def test_create_room_duplicate_number(self, api_client):
        """Test creating room with duplicate number."""
        admin = AdminUserFactory()
        api_client.force_authenticate(user=admin)
        hotel = HotelFactory()
        room = RoomFactory(hotel=hotel, numero='101')
        
        data = {
            'hotel': hotel.id,
            'numero': '101',
            'tipo': 'standard',
            'capacidade': 2,
            'preco_diaria': 100.0,
        }
        response = api_client.post('/api/v1/rooms/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
