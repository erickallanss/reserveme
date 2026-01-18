"""
Testes unitários para o service de Booking.
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from reserveme.services.booking_service import (
    BookingService,
    BookingNotFoundError,
    RoomNotAvailableError,
    InvalidBookingError
)
from reserveme.repositories.booking_repository import BookingRepository
from reserveme.repositories.room_repository import RoomRepository
from reserveme.tests.booking_factories import BookingFactory, ConfirmedBookingFactory
from reserveme.tests.room_factories import RoomFactory
from reserveme.tests.factories import UserFactory


@pytest.mark.django_db
class TestBookingService:
    """Testes para BookingService."""
    
    @pytest.fixture
    def booking_service(self):
        """Fixture que retorna instância do service."""
        return BookingService(
            BookingRepository(),
            RoomRepository()
        )
    
    def test_create_booking(self, booking_service):
        """Testa criação de reserva."""
        room = RoomFactory(capacidade=2)
        user = UserFactory()
        
        booking_data = {
            'room': room,
            'user': user,
            'data_checkin': date.today() + timedelta(days=5),
            'data_checkout': date.today() + timedelta(days=8),
            'numero_hospedes': 2
        }
        
        booking = booking_service.create_booking(booking_data)
        
        assert booking.id is not None
        assert booking.codigo_reserva is not None
        assert booking.status == 'pending'
        assert booking.numero_diarias == 3
        assert booking.preco_total == room.preco_diaria * 3
    
    def test_create_booking_invalid_dates(self, booking_service):
        """Testa erro ao criar reserva com datas inválidas."""
        room = RoomFactory()
        user = UserFactory()
        
        booking_data = {
            'room': room,
            'user': user,
            'data_checkin': date.today() + timedelta(days=5),
            'data_checkout': date.today() + timedelta(days=3),  # Antes do check-in
            'numero_hospedes': 2
        }
        
        with pytest.raises(InvalidBookingError):
            booking_service.create_booking(booking_data)
    
    def test_create_booking_exceeds_capacity(self, booking_service):
        """Testa erro ao criar reserva com mais hóspedes que capacidade."""
        room = RoomFactory(capacidade=2)
        user = UserFactory()
        
        booking_data = {
            'room': room,
            'user': user,
            'data_checkin': date.today() + timedelta(days=5),
            'data_checkout': date.today() + timedelta(days=8),
            'numero_hospedes': 5  # Mais que a capacidade
        }
        
        with pytest.raises(InvalidBookingError):
            booking_service.create_booking(booking_data)
    
    def test_create_booking_room_unavailable(self, booking_service):
        """Testa erro ao criar reserva em quarto ocupado."""
        room = RoomFactory()
        user = UserFactory()
        
        # Criar reserva que se sobrepõe
        BookingFactory(
            room=room,
            data_checkin=date.today() + timedelta(days=5),
            data_checkout=date.today() + timedelta(days=8),
            status='confirmed'
        )
        
        booking_data = {
            'room': room,
            'user': user,
            'data_checkin': date.today() + timedelta(days=6),
            'data_checkout': date.today() + timedelta(days=7),
            'numero_hospedes': 2
        }
        
        with pytest.raises(RoomNotAvailableError):
            booking_service.create_booking(booking_data)
    
    def test_confirm_booking(self, booking_service):
        """Testa confirmação de reserva."""
        booking = BookingFactory(status='pending')
        
        confirmed = booking_service.confirm_booking(booking.id)
        
        assert confirmed.status == 'confirmed'
    
    def test_confirm_booking_invalid_status(self, booking_service):
        """Testa erro ao confirmar reserva com status inválido."""
        booking = ConfirmedBookingFactory()
        
        with pytest.raises(InvalidBookingError):
            booking_service.confirm_booking(booking.id)
    
    def test_cancel_booking(self, booking_service):
        """Testa cancelamento de reserva."""
        booking = ConfirmedBookingFactory()
        
        cancelled = booking_service.cancel_booking(booking.id)
        
        assert cancelled.status == 'cancelled'
        assert cancelled.cancelled_at is not None
    
    def test_checkin(self, booking_service):
        """Testa check-in."""
        booking = ConfirmedBookingFactory()
        
        checked_in = booking_service.checkin(booking.id)
        
        assert checked_in.status == 'checked_in'
        assert checked_in.checked_in_at is not None
    
    def test_checkout(self, booking_service):
        """Testa check-out."""
        booking = BookingFactory(status='checked_in')
        
        checked_out = booking_service.checkout(booking.id)
        
        assert checked_out.status == 'checked_out'
        assert checked_out.checked_out_at is not None
