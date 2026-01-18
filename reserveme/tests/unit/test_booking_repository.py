"""
Testes unitários para o repositório de Booking.
"""
import pytest
from datetime import date, timedelta
from reserveme.repositories.booking_repository import BookingRepository
from reserveme.tests.booking_factories import (
    BookingFactory,
    ConfirmedBookingFactory,
    CancelledBookingFactory
)
from reserveme.tests.room_factories import RoomFactory


@pytest.mark.django_db
class TestBookingRepository:
    """Testes para BookingRepository."""
    
    @pytest.fixture
    def booking_repository(self):
        """Fixture que retorna instância do repositório."""
        return BookingRepository()
    
    def test_create_booking(self, booking_repository):
        """Testa criação de reserva."""
        room = RoomFactory()
        from reserveme.tests.factories import UserFactory
        user = UserFactory()
        
        booking_data = {
            'room': room,
            'user': user,
            'data_checkin': date.today() + timedelta(days=5),
            'data_checkout': date.today() + timedelta(days=8),
            'numero_hospedes': 2,
            'numero_diarias': 3,
            'preco_diaria': '250.00',
            'preco_total': '750.00',
            'status': 'pending'
        }
        
        booking = booking_repository.create(**booking_data)
        
        assert booking.id is not None
        assert booking.codigo_reserva is not None
        assert booking.room.id == room.id
        assert booking.user.id == user.id
    
    def test_get_by_codigo(self, booking_repository):
        """Testa busca por código de reserva."""
        booking = BookingFactory()
        
        found_booking = booking_repository.get_by_codigo(booking.codigo_reserva)
        
        assert found_booking is not None
        assert found_booking.id == booking.id
    
    def test_get_user_bookings(self, booking_repository):
        """Testa busca de reservas de um usuário."""
        from reserveme.tests.factories import UserFactory
        user = UserFactory()
        booking1 = BookingFactory(user=user)
        booking2 = BookingFactory(user=user)
        other_booking = BookingFactory()  # Outro usuário
        
        bookings = booking_repository.get_user_bookings(user.id)
        
        assert len(bookings) == 2
        assert booking1.id in [b.id for b in bookings]
        assert booking2.id in [b.id for b in bookings]
        assert other_booking.id not in [b.id for b in bookings]
    
    def test_get_user_bookings_filtered_by_status(self, booking_repository):
        """Testa busca de reservas filtradas por status."""
        from reserveme.tests.factories import UserFactory
        user = UserFactory()
        pending = BookingFactory(user=user, status='pending')
        confirmed = ConfirmedBookingFactory(user=user)
        
        pending_bookings = booking_repository.get_user_bookings(user.id, 'pending')
        
        assert pending.id in [b.id for b in pending_bookings]
        assert confirmed.id not in [b.id for b in pending_bookings]
    
    def test_check_room_availability_available(self, booking_repository):
        """Testa verificação de disponibilidade quando quarto está livre."""
        room = RoomFactory()
        checkin = date.today() + timedelta(days=10)
        checkout = date.today() + timedelta(days=13)
        
        is_available = booking_repository.check_room_availability(
            room.id, checkin, checkout
        )
        
        assert is_available is True
    
    def test_check_room_availability_unavailable(self, booking_repository):
        """Testa verificação de disponibilidade quando quarto está ocupado."""
        room = RoomFactory()
        checkin = date.today() + timedelta(days=10)
        checkout = date.today() + timedelta(days=13)
        
        # Criar reserva que se sobrepõe
        BookingFactory(
            room=room,
            data_checkin=checkin + timedelta(days=1),
            data_checkout=checkout - timedelta(days=1),
            status='confirmed'
        )
        
        is_available = booking_repository.check_room_availability(
            room.id, checkin, checkout
        )
        
        assert is_available is False
    
    def test_get_bookings_to_release(self, booking_repository):
        """Testa busca de reservas para liberar (expiradas)."""
        room = RoomFactory()
        from reserveme.tests.factories import UserFactory
        user = UserFactory()
        
        # Reserva expirada (check-in passou)
        expired = BookingFactory(
            room=room,
            user=user,
            data_checkin=date.today() - timedelta(days=2),
            status='pending'
        )
        
        # Reserva futura (não expirada)
        future = BookingFactory(
            room=room,
            user=user,
            data_checkin=date.today() + timedelta(days=5),
            status='pending'
        )
        
        to_release = booking_repository.get_bookings_to_release()
        
        assert expired.id in [b.id for b in to_release]
        assert future.id not in [b.id for b in to_release]
