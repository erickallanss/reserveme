"""Integration tests for room view error handling."""
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from reserveme.tests.factories import StaffUserFactory
from reserveme.tests.room_factories import RoomFactory


@pytest.fixture
def api_client():
    """Fixture for API client."""
    return APIClient()


@pytest.mark.django_db
class TestRoomViewErrors:
    """Tests for room view error handling."""
    
    def test_update_room_not_found(self, api_client):
        """Test updating non-existent room."""
        staff = StaffUserFactory()
        api_client.force_authenticate(user=staff)
        
        data = {'numero': '999'}
        response = api_client.patch('/api/v1/rooms/99999/', data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_room_not_found(self, api_client):
        """Test deleting non-existent room."""
        staff = StaffUserFactory()
        api_client.force_authenticate(user=staff)
        
        response = api_client.delete('/api/v1/rooms/99999/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
