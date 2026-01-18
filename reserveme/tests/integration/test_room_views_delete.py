"""Integration tests for room delete operations."""
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from reserveme.tests.factories import StaffUserFactory, AdminUserFactory
from reserveme.tests.room_factories import RoomFactory


@pytest.fixture
def api_client():
    """Fixture for API client."""
    return APIClient()


@pytest.mark.django_db
class TestRoomDelete:
    """Tests for room delete operations."""
    
    def test_delete_room_as_staff(self, api_client):
        """Test deleting room as staff."""
        staff = StaffUserFactory()
        api_client.force_authenticate(user=staff)
        room = RoomFactory(is_active=True)
        
        response = api_client.delete(f'/api/v1/rooms/{room.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        room.refresh_from_db()
        assert room.is_active is False
    
    def test_delete_room_as_admin(self, api_client):
        """Test deleting room as admin."""
        admin = AdminUserFactory()
        api_client.force_authenticate(user=admin)
        room = RoomFactory(is_active=True)
        
        response = api_client.delete(f'/api/v1/rooms/{room.id}/')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_delete_room_unauthorized(self, api_client):
        """Test that customer cannot delete room."""
        from reserveme.tests.factories import UserFactory
        customer = UserFactory()
        api_client.force_authenticate(user=customer)
        room = RoomFactory()
        
        response = api_client.delete(f'/api/v1/rooms/{room.id}/')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
