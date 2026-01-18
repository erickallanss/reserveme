"""Extended unit tests for RoomService."""
import pytest
from decimal import Decimal
from reserveme.services.room_service import (
    RoomService,
    RoomNotFoundError,
    RoomAlreadyExistsError
)
from reserveme.repositories.room_repository import RoomRepository
from reserveme.tests.room_factories import RoomFactory, SuiteRoomFactory
from reserveme.tests.hotel_factories import HotelFactory


@pytest.mark.django_db
class TestRoomServiceExtended:
    """Extended tests for RoomService."""
    
    @pytest.fixture
    def room_service(self):
        """Fixture that returns service instance."""
        return RoomService(RoomRepository())
    
    def test_list_rooms_all(self, room_service):
        """Test listing all rooms."""
        room1 = RoomFactory()
        room2 = RoomFactory()
        
        rooms = room_service.list_rooms()
        
        assert len(rooms) >= 2
        assert room1.id in [r.id for r in rooms]
        assert room2.id in [r.id for r in rooms]
    
    def test_list_rooms_by_hotel(self, room_service):
        """Test listing rooms filtered by hotel."""
        hotel = HotelFactory()
        room1 = RoomFactory(hotel=hotel)
        room2 = RoomFactory(hotel=hotel)
        other_room = RoomFactory()  # Different hotel
        
        rooms = room_service.list_rooms(hotel_id=hotel.id)
        
        room_ids = [r.id for r in rooms]
        assert room1.id in room_ids
        assert room2.id in room_ids
        assert other_room.id not in room_ids
    
    def test_update_room_change_number(self, room_service):
        """Test updating room number with validation."""
        room = RoomFactory(numero='101')
        
        # Try to change to existing number (should fail)
        room2 = RoomFactory(hotel=room.hotel, numero='202')
        
        with pytest.raises(RoomAlreadyExistsError):
            room_service.update_room(room.id, {'numero': '202'})
    
    def test_update_room_same_number(self, room_service):
        """Test updating room keeping same number."""
        room = RoomFactory(numero='101', preco_diaria=Decimal('250.00'))
        
        updated = room_service.update_room(room.id, {'preco_diaria': Decimal('300.00')})
        
        assert updated.preco_diaria == Decimal('300.00')
        assert updated.numero == '101'  # Number unchanged
    
    def test_activate_room(self, room_service):
        """Test activating a room."""
        room = RoomFactory(is_active=False)
        
        # Activate via update
        updated = room_service.update_room(room.id, {'is_active': True})
        
        assert updated.is_active is True
    
    def test_get_room_by_numero(self, room_service):
        """Test getting room by number."""
        hotel = HotelFactory()
        room = RoomFactory(hotel=hotel, numero='999')
        
        found = room_service.get_room_by_numero(hotel.id, '999')
        
        assert found.id == room.id
        assert found.numero == '999'
    
    def test_get_room_by_numero_not_found(self, room_service):
        """Test error when room number doesn't exist."""
        hotel = HotelFactory()
        
        with pytest.raises(RoomNotFoundError):
            room_service.get_room_by_numero(hotel.id, '999')
