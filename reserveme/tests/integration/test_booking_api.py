"""
Testes de integração para endpoints de Booking.
"""
import pytest
from datetime import date, timedelta
from rest_framework import status
from rest_framework.test import APIClient
from reserveme.tests.booking_factories import BookingFactory, ConfirmedBookingFactory
from reserveme.tests.room_factories import RoomFactory
from reserveme.tests.factories import UserFactory, StaffUserFactory


@pytest.fixture
def api_client():
    """Fixture do cliente API."""
    return APIClient()


@pytest.mark.django_db
class TestBookingAPI:
    """Testes de integração para API de Booking."""
    
    def test_create_booking_as_customer(self, api_client):
        """Testa criação de reserva como cliente."""
        customer = UserFactory()
        api_client.force_authenticate(user=customer)
        room = RoomFactory(capacidade=2)
        
        data = {
            'room': room.id,
            'data_checkin': str(date.today() + timedelta(days=5)),
            'data_checkout': str(date.today() + timedelta(days=8)),
            'numero_hospedes': 2
        }
        
        response = api_client.post('/api/v1/bookings/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'booking' in response.data
        assert response.data['booking']['status'] == 'pending'
    
    def test_create_booking_room_unavailable(self, api_client):
        """Testa erro ao criar reserva em quarto ocupado."""
        customer = UserFactory()
        api_client.force_authenticate(user=customer)
        room = RoomFactory()
        
        # Criar reserva que se sobrepõe
        BookingFactory(
            room=room,
            data_checkin=date.today() + timedelta(days=5),
            data_checkout=date.today() + timedelta(days=8),
            status='confirmed'
        )
        
        data = {
            'room': room.id,
            'data_checkin': str(date.today() + timedelta(days=6)),
            'data_checkout': str(date.today() + timedelta(days=7)),
            'numero_hospedes': 2
        }
        
        response = api_client.post('/api/v1/bookings/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_list_my_bookings_as_customer(self, api_client):
        """Testa listagem de reservas do próprio cliente."""
        customer = UserFactory()
        api_client.force_authenticate(user=customer)
        booking1 = BookingFactory(user=customer)
        booking2 = BookingFactory(user=customer)
        other_booking = BookingFactory()  # Outro cliente
        
        response = api_client.get('/api/v1/bookings/')
        
        assert response.status_code == status.HTTP_200_OK
        bookings = response.data['results']
        booking_ids = [b['id'] for b in bookings]
        assert booking1.id in booking_ids
        assert booking2.id in booking_ids
        assert other_booking.id not in booking_ids
    
    def test_list_all_bookings_as_staff(self, api_client):
        """Testa que staff vê todas as reservas."""
        staff = StaffUserFactory()
        api_client.force_authenticate(user=staff)
        booking1 = BookingFactory()
        booking2 = BookingFactory()
        
        response = api_client.get('/api/v1/bookings/')
        
        assert response.status_code == status.HTTP_200_OK
        bookings = response.data['results']
        booking_ids = [b['id'] for b in bookings]
        assert booking1.id in booking_ids
        assert booking2.id in booking_ids
    
    def test_confirm_booking_as_staff(self, api_client):
        """Testa confirmação de reserva como staff."""
        staff = StaffUserFactory()
        api_client.force_authenticate(user=staff)
        booking = BookingFactory(status='pending')
        
        response = api_client.post(f'/api/v1/bookings/{booking.id}/confirm/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['booking']['status'] == 'confirmed'
    
    def test_cancel_booking_as_owner(self, api_client):
        """Testa cancelamento de reserva pelo dono."""
        customer = UserFactory()
        api_client.force_authenticate(user=customer)
        booking = ConfirmedBookingFactory(user=customer)
        
        response = api_client.delete(f'/api/v1/bookings/{booking.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        booking.refresh_from_db()
        assert booking.status == 'cancelled'
