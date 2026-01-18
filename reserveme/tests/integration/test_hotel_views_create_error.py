"""Integration tests for hotel create error handling."""
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from reserveme.tests.factories import AdminUserFactory
from reserveme.tests.hotel_factories import HotelFactory


@pytest.fixture
def api_client():
    """Fixture for API client."""
    return APIClient()


@pytest.mark.django_db
class TestHotelCreateErrors:
    """Tests for hotel create error handling."""
    
    def test_create_hotel_duplicate_name(self, api_client):
        """Test creating hotel with duplicate name."""
        admin = AdminUserFactory()
        api_client.force_authenticate(user=admin)
        hotel = HotelFactory(nome='Test Hotel')
        
        data = {
            'nome': 'Test Hotel',
            'descricao': 'Test',
            'endereco': 'Test Address',
            'telefone': '(11) 98765-4321',
            'email': 'test@hotel.com',
            'horario_checkin': '14:00:00',
            'horario_checkout': '12:00:00',
        }
        response = api_client.post('/api/v1/hotels/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
