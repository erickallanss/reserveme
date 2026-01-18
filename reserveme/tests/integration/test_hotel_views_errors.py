"""Integration tests for hotel view error handling."""
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
class TestHotelViewErrors:
    """Tests for hotel view error handling."""
    
    def test_update_hotel_not_found(self, api_client):
        """Test updating non-existent hotel."""
        admin = AdminUserFactory()
        api_client.force_authenticate(user=admin)
        
        data = {'nome': 'Updated Hotel'}
        response = api_client.patch('/api/v1/hotels/99999/', data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_hotel_not_found(self, api_client):
        """Test deleting non-existent hotel."""
        admin = AdminUserFactory()
        api_client.force_authenticate(user=admin)
        
        response = api_client.delete('/api/v1/hotels/99999/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
