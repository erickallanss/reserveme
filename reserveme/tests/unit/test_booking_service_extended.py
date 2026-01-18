"""Extended unit tests for BookingService."""
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
from reserveme.tests.booking_factories import (
    BookingFactory,
    ConfirmedBookingFactory,
    CheckedInBookingFactory
)
from reserveme.tests.room_factories import RoomFactory
from reserveme.tests.factories import UserFactory


@pytest.mark.django_db
class TestBookingServiceExtended:
    """Extended tests for BookingService."""
    
    @pytest.fixture
    def booking_service(self):
        """Fixture that returns service instance."""
        return BookingService(
            BookingRepository(),
            RoomRepository()
        )
    
    def test_calculate_numero_diarias(self, booking_service):
        """Test calculating number of nights."""
        checkin = date.today() + timedelta(days=5)
        checkout = date.today() + timedelta(days=10)
        
        diarias = booking_service.calculate_numero_diarias(checkin, checkout)
        
        assert diarias == 5
    
    def test_calculate_total_price(self, booking_service):
        """Test calculating total price."""
        preco_diaria = Decimal('250.00')
        numero_diarias = 3
        
        total = booking_service.calculate_total_price(preco_diaria, numero_diarias)
        
        assert total == Decimal('750.00')
    
    def test_validate_dates_same_day(self, booking_service):
        """Test validation fails for same check-in and check-out."""
        same_date = date.today() + timedelta(days=5)
        
        with pytest.raises(InvalidBookingError):
            booking_service.validate_dates(same_date, same_date)
    
    def test_validate_dates_past_checkin(self, booking_service):
        """Test validation fails for past check-in."""
        past = date.today() - timedelta(days=1)
        future = date.today() + timedelta(days=5)
        
        with pytest.raises(InvalidBookingError):
            booking_service.validate_dates(past, future)
    
    def test_list_user_bookings_with_status(self, booking_service):
        """Test listing user bookings filtered by status."""
        user = UserFactory()
        pending = BookingFactory(user=user, status='pending')
        confirmed = ConfirmedBookingFactory(user=user)
        
        pending_bookings = booking_service.list_user_bookings(user.id, 'pending')
        
        booking_ids = [b.id for b in pending_bookings]
        assert pending.id in booking_ids
        assert confirmed.id not in booking_ids
    
    def test_list_hotel_bookings(self, booking_service):
        """Test listing bookings for a hotel."""
        room1 = RoomFactory()
        room2 = RoomFactory(hotel=room1.hotel)
        other_room = RoomFactory()  # Different hotel
        
        booking1 = BookingFactory(room=room1)
        booking2 = BookingFactory(room=room2)
        other_booking = BookingFactory(room=other_room)
        
        bookings = booking_service.list_hotel_bookings(room1.hotel.id)
        
        booking_ids = [b.id for b in bookings]
        assert booking1.id in booking_ids
        assert booking2.id in booking_ids
        assert other_booking.id not in booking_ids
    
    def test_list_hotel_bookings_with_status(self, booking_service):
        """Test listing hotel bookings filtered by status."""
        room = RoomFactory()
        pending = BookingFactory(room=room, status='pending')
        confirmed = ConfirmedBookingFactory(room=room)
        
        confirmed_bookings = booking_service.list_hotel_bookings(room.hotel.id, 'confirmed')
        
        booking_ids = [b.id for b in confirmed_bookings]
        assert confirmed.id in booking_ids
        assert pending.id not in booking_ids
    
    def test_check_availability_available(self, booking_service):
        """Test checking availability when room is available."""
        room = RoomFactory()
        checkin = date.today() + timedelta(days=10)
        checkout = date.today() + timedelta(days=13)
        
        is_available = booking_service.check_availability(room.id, checkin, checkout)
        
        assert is_available is True
    
    def test_check_availability_unavailable(self, booking_service):
        """Test checking availability when room is occupied."""
        room = RoomFactory()
        checkin = date.today() + timedelta(days=10)
        checkout = date.today() + timedelta(days=13)
        
        # Create overlapping booking
        BookingFactory(
            room=room,
            data_checkin=checkin + timedelta(days=1),
            data_checkout=checkout - timedelta(days=1),
            status='confirmed'
        )
        
        is_available = booking_service.check_availability(room.id, checkin, checkout)
        
        assert is_available is False
    
    def test_get_booking_by_codigo(self, booking_service):
        """Test getting booking by code."""
        booking = BookingFactory()
        
        found = booking_service.get_booking_by_codigo(booking.codigo_reserva)
        
        assert found.id == booking.id
    
    def test_get_booking_by_codigo_not_found(self, booking_service):
        """Test error when booking code doesn't exist."""
        with pytest.raises(BookingNotFoundError):
            booking_service.get_booking_by_codigo('INVALID-CODE')
