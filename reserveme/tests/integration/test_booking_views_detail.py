"""Integration tests for booking detail view."""
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from reserveme.tests.factories import UserFactory, StaffUserFactory
from reserveme.tests.booking_factories import BookingFactory


@pytest.fixture
def api_client():
    """Fixture for API client."""
    return APIClient()


@pytest.mark.django_db
class TestBookingDetail:
    """Tests for booking detail view."""
    
    def test_get_booking_detail_unauthorized(self, api_client):
        """Test getting booking detail of another user."""
        customer1 = UserFactory()
        customer2 = UserFactory()
        api_client.force_authenticate(user=customer1)
        booking = BookingFactory(user=customer2)
        
        response = api_client.get(f'/api/v1/bookings/{booking.id}/')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_booking_detail_not_found(self, api_client):
        """Test getting non-existent booking."""
        customer = UserFactory()
        api_client.force_authenticate(user=customer)
        
        response = api_client.get('/api/v1/bookings/99999/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_booking_detail_as_staff(self, api_client):
        """Test getting booking detail as staff."""
        staff = StaffUserFactory()
        customer = UserFactory()
        api_client.force_authenticate(user=staff)
        booking = BookingFactory(user=customer)
        
        response = api_client.get(f'/api/v1/bookings/{booking.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == booking.id
