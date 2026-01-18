"""Integration tests for hotel delete operations."""
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from reserveme.tests.factories import AdminUserFactory, UserFactory
from reserveme.tests.hotel_factories import HotelFactory


@pytest.fixture
def api_client():
    """Fixture for API client."""
    return APIClient()


@pytest.mark.django_db
class TestHotelDelete:
    """Tests for hotel delete operations."""
    
    def test_delete_hotel_as_admin(self, api_client):
        """Test deleting hotel as admin."""
        admin = AdminUserFactory()
        api_client.force_authenticate(user=admin)
        hotel = HotelFactory(is_active=True)
        
        response = api_client.delete(f'/api/v1/hotels/{hotel.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        hotel.refresh_from_db()
        assert hotel.is_active is False
    
    def test_delete_hotel_unauthorized(self, api_client):
        """Test that non-admin cannot delete hotel."""
        customer = UserFactory()
        api_client.force_authenticate(user=customer)
        hotel = HotelFactory()
        
        response = api_client.delete(f'/api/v1/hotels/{hotel.id}/')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delete_hotel_not_found(self, api_client):
        """Test deleting non-existent hotel."""
        admin = AdminUserFactory()
        api_client.force_authenticate(user=admin)
        
        response = api_client.delete('/api/v1/hotels/99999/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
