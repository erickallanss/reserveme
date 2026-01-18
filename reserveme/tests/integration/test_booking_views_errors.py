"""Integration tests for booking view error handling."""
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from reserveme.tests.factories import UserFactory, StaffUserFactory
from reserveme.tests.booking_factories import BookingFactory, ConfirmedBookingFactory


@pytest.fixture
def api_client():
    """Fixture for API client."""
    return APIClient()


@pytest.mark.django_db
class TestBookingViewErrors:
    """Tests for booking view error handling."""
    
    def test_confirm_booking_not_found(self, api_client):
        """Test confirming non-existent booking."""
        staff = StaffUserFactory()
        api_client.force_authenticate(user=staff)
        
        response = api_client.post('/api/v1/bookings/99999/confirm/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_checkin_booking_not_found(self, api_client):
        """Test check-in of non-existent booking."""
        staff = StaffUserFactory()
        api_client.force_authenticate(user=staff)
        
        response = api_client.post('/api/v1/bookings/99999/checkin/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_checkout_booking_not_found(self, api_client):
        """Test check-out of non-existent booking."""
        staff = StaffUserFactory()
        api_client.force_authenticate(user=staff)
        
        response = api_client.post('/api/v1/bookings/99999/checkout/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_confirm_booking_invalid_status(self, api_client):
        """Test confirming booking with invalid status."""
        staff = StaffUserFactory()
        api_client.force_authenticate(user=staff)
        booking = ConfirmedBookingFactory()  # Already confirmed
        
        response = api_client.post(f'/api/v1/bookings/{booking.id}/confirm/')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
