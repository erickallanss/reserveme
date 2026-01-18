"""Extended integration tests for Booking views."""
import pytest
from datetime import date, timedelta
from rest_framework import status
from rest_framework.test import APIClient
from reserveme.tests.factories import UserFactory, StaffUserFactory
from reserveme.tests.booking_factories import BookingFactory, ConfirmedBookingFactory
from reserveme.tests.room_factories import RoomFactory


@pytest.fixture
def api_client():
    """Fixture for API client."""
    return APIClient()


@pytest.mark.django_db
class TestBookingViewsExtended:
    """Extended tests for booking views."""
    
    def test_booking_detail_get(self, api_client):
        """Test getting booking details."""
        customer = UserFactory()
        api_client.force_authenticate(user=customer)
        booking = BookingFactory(user=customer)
        
        response = api_client.get(f'/api/v1/bookings/{booking.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == booking.id
    
    def test_booking_detail_delete(self, api_client):
        """Test deleting (canceling) booking."""
        customer = UserFactory()
        api_client.force_authenticate(user=customer)
        booking = BookingFactory(user=customer, status='pending')
        
        response = api_client.delete(f'/api/v1/bookings/{booking.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        booking.refresh_from_db()
        assert booking.status == 'cancelled'
    
    def test_booking_checkin_as_staff(self, api_client):
        """Test check-in as staff."""
        staff = StaffUserFactory()
        api_client.force_authenticate(user=staff)
        booking = ConfirmedBookingFactory()
        
        response = api_client.post(f'/api/v1/bookings/{booking.id}/checkin/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['booking']['status'] == 'checked_in'
    
    def test_booking_checkout_as_staff(self, api_client):
        """Test check-out as staff."""
        staff = StaffUserFactory()
        api_client.force_authenticate(user=staff)
        booking = BookingFactory(status='checked_in')
        
        response = api_client.post(f'/api/v1/bookings/{booking.id}/checkout/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['booking']['status'] == 'checked_out'
    
    def test_hotel_bookings_list(self, api_client):
        """Test listing hotel bookings."""
        staff = StaffUserFactory()
        api_client.force_authenticate(user=staff)
        from reserveme.tests.hotel_factories import HotelFactory
        hotel = HotelFactory()
        room1 = RoomFactory(hotel=hotel)
        room2 = RoomFactory(hotel=hotel)
        booking1 = BookingFactory(room=room1)
        booking2 = BookingFactory(room=room2)
        
        response = api_client.get(f'/api/v1/hotels/{hotel.id}/bookings/')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'bookings' in response.data
        booking_ids = [b['id'] for b in response.data['bookings']]
        assert booking1.id in booking_ids
        assert booking2.id in booking_ids
