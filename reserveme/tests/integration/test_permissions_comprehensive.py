"""Comprehensive integration tests for permissions."""
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from reserveme.tests.factories import UserFactory, AdminUserFactory, StaffUserFactory
from reserveme.tests.hotel_factories import HotelFactory
from reserveme.tests.room_factories import RoomFactory
from reserveme.tests.booking_factories import BookingFactory, ConfirmedBookingFactory


@pytest.fixture
def api_client():
    """Fixture for API client."""
    return APIClient()


@pytest.mark.django_db
class TestPermissionsComprehensive:
    """Comprehensive tests for all permission scenarios."""
    
    # ========== HOTEL PERMISSIONS ==========
    
    def test_hotel_create_admin_allowed(self, api_client):
        """Admin can create hotels."""
        admin = AdminUserFactory()
        api_client.force_authenticate(user=admin)
        
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
        
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_hotel_create_staff_forbidden(self, api_client):
        """Staff cannot create hotels."""
        staff = StaffUserFactory()
        api_client.force_authenticate(user=staff)
        
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
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_hotel_create_customer_forbidden(self, api_client):
        """Customer cannot create hotels."""
        customer = UserFactory()
        api_client.force_authenticate(user=customer)
        
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
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_hotel_update_admin_allowed(self, api_client):
        """Admin can update hotels."""
        admin = AdminUserFactory()
        api_client.force_authenticate(user=admin)
        hotel = HotelFactory()
        
        data = {'nome': 'Updated Hotel'}
        response = api_client.patch(f'/api/v1/hotels/{hotel.id}/', data)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_hotel_update_customer_forbidden(self, api_client):
        """Customer cannot update hotels."""
        customer = UserFactory()
        api_client.force_authenticate(user=customer)
        hotel = HotelFactory()
        
        data = {'nome': 'Updated Hotel'}
        response = api_client.patch(f'/api/v1/hotels/{hotel.id}/', data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_hotel_delete_admin_allowed(self, api_client):
        """Admin can delete hotels."""
        admin = AdminUserFactory()
        api_client.force_authenticate(user=admin)
        hotel = HotelFactory()
        
        response = api_client.delete(f'/api/v1/hotels/{hotel.id}/')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_hotel_delete_customer_forbidden(self, api_client):
        """Customer cannot delete hotels."""
        customer = UserFactory()
        api_client.force_authenticate(user=customer)
        hotel = HotelFactory()
        
        response = api_client.delete(f'/api/v1/hotels/{hotel.id}/')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # ========== ROOM PERMISSIONS ==========
    
    def test_room_create_admin_allowed(self, api_client):
        """Admin can create rooms."""
        admin = AdminUserFactory()
        api_client.force_authenticate(user=admin)
        hotel = HotelFactory()
        
        data = {
            'hotel': hotel.id,
            'numero': '999',
            'tipo': 'double',
            'capacidade': 2,
            'preco_diaria': '250.00'
        }
        response = api_client.post('/api/v1/rooms/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_room_create_staff_allowed(self, api_client):
        """Staff can create rooms."""
        staff = StaffUserFactory()
        api_client.force_authenticate(user=staff)
        hotel = HotelFactory()
        
        data = {
            'hotel': hotel.id,
            'numero': '998',
            'tipo': 'double',
            'capacidade': 2,
            'preco_diaria': '250.00'
        }
        response = api_client.post('/api/v1/rooms/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_room_create_customer_forbidden(self, api_client):
        """Customer cannot create rooms."""
        customer = UserFactory()
        api_client.force_authenticate(user=customer)
        hotel = HotelFactory()
        
        data = {
            'hotel': hotel.id,
            'numero': '997',
            'tipo': 'double',
            'capacidade': 2,
            'preco_diaria': '250.00'
        }
        response = api_client.post('/api/v1/rooms/', data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_room_update_staff_allowed(self, api_client):
        """Staff can update rooms."""
        staff = StaffUserFactory()
        api_client.force_authenticate(user=staff)
        room = RoomFactory()
        
        data = {'preco_diaria': '300.00'}
        response = api_client.patch(f'/api/v1/rooms/{room.id}/', data)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_room_update_customer_forbidden(self, api_client):
        """Customer cannot update rooms."""
        customer = UserFactory()
        api_client.force_authenticate(user=customer)
        room = RoomFactory()
        
        data = {'preco_diaria': '300.00'}
        response = api_client.patch(f'/api/v1/rooms/{room.id}/', data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_room_delete_staff_allowed(self, api_client):
        """Staff can delete rooms."""
        staff = StaffUserFactory()
        api_client.force_authenticate(user=staff)
        room = RoomFactory()
        
        response = api_client.delete(f'/api/v1/rooms/{room.id}/')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_room_delete_customer_forbidden(self, api_client):
        """Customer cannot delete rooms."""
        customer = UserFactory()
        api_client.force_authenticate(user=customer)
        room = RoomFactory()
        
        response = api_client.delete(f'/api/v1/rooms/{room.id}/')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # ========== BOOKING PERMISSIONS ==========
    
    def test_booking_create_customer_allowed(self, api_client):
        """Customer can create bookings."""
        customer = UserFactory()
        api_client.force_authenticate(user=customer)
        room = RoomFactory()
        
        from datetime import date, timedelta
        data = {
            'room': room.id,
            'data_checkin': str(date.today() + timedelta(days=5)),
            'data_checkout': str(date.today() + timedelta(days=8)),
            'numero_hospedes': 2
        }
        response = api_client.post('/api/v1/bookings/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_booking_confirm_staff_allowed(self, api_client):
        """Staff can confirm bookings."""
        staff = StaffUserFactory()
        api_client.force_authenticate(user=staff)
        booking = BookingFactory(status='pending')
        
        response = api_client.post(f'/api/v1/bookings/{booking.id}/confirm/')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_booking_confirm_customer_forbidden(self, api_client):
        """Customer cannot confirm bookings."""
        customer = UserFactory()
        api_client.force_authenticate(user=customer)
        booking = BookingFactory(user=customer, status='pending')
        
        response = api_client.post(f'/api/v1/bookings/{booking.id}/confirm/')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_booking_checkin_staff_allowed(self, api_client):
        """Staff can do check-in."""
        staff = StaffUserFactory()
        api_client.force_authenticate(user=staff)
        booking = ConfirmedBookingFactory()
        
        response = api_client.post(f'/api/v1/bookings/{booking.id}/checkin/')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_booking_checkin_customer_forbidden(self, api_client):
        """Customer cannot do check-in."""
        customer = UserFactory()
        api_client.force_authenticate(user=customer)
        booking = ConfirmedBookingFactory(user=customer)
        
        response = api_client.post(f'/api/v1/bookings/{booking.id}/checkin/')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_booking_list_customer_sees_only_own(self, api_client):
        """Customer sees only their own bookings."""
        customer1 = UserFactory()
        customer2 = UserFactory()
        api_client.force_authenticate(user=customer1)
        
        booking1 = BookingFactory(user=customer1)
        booking2 = BookingFactory(user=customer2)
        
        response = api_client.get('/api/v1/bookings/')
        
        assert response.status_code == status.HTTP_200_OK
        booking_ids = [b['id'] for b in response.data['results']]
        assert booking1.id in booking_ids
        assert booking2.id not in booking_ids
    
    def test_booking_list_staff_sees_all(self, api_client):
        """Staff sees all bookings."""
        staff = StaffUserFactory()
        customer1 = UserFactory()
        customer2 = UserFactory()
        api_client.force_authenticate(user=staff)
        
        booking1 = BookingFactory(user=customer1)
        booking2 = BookingFactory(user=customer2)
        
        response = api_client.get('/api/v1/bookings/')
        
        assert response.status_code == status.HTTP_200_OK
        booking_ids = [b['id'] for b in response.data['results']]
        assert booking1.id in booking_ids
        assert booking2.id in booking_ids
    
    def test_booking_detail_owner_allowed(self, api_client):
        """Booking owner can see their booking."""
        customer = UserFactory()
        api_client.force_authenticate(user=customer)
        booking = BookingFactory(user=customer)
        
        response = api_client.get(f'/api/v1/bookings/{booking.id}/')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_booking_detail_other_customer_forbidden(self, api_client):
        """Other customer cannot see booking."""
        customer1 = UserFactory()
        customer2 = UserFactory()
        api_client.force_authenticate(user=customer1)
        booking = BookingFactory(user=customer2)
        
        response = api_client.get(f'/api/v1/bookings/{booking.id}/')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_booking_detail_staff_allowed(self, api_client):
        """Staff can see any booking."""
        staff = StaffUserFactory()
        customer = UserFactory()
        api_client.force_authenticate(user=staff)
        booking = BookingFactory(user=customer)
        
        response = api_client.get(f'/api/v1/bookings/{booking.id}/')
        
        assert response.status_code == status.HTTP_200_OK
