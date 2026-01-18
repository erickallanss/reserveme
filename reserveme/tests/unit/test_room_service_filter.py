"""Unit tests for room filtering."""
import pytest
from reserveme.services.room_service import RoomService
from reserveme.repositories.room_repository import RoomRepository
from reserveme.tests.room_factories import RoomFactory


@pytest.mark.django_db
class TestRoomFiltering:
    """Tests for room filtering."""
    
    @pytest.fixture
    def room_service(self):
        """Fixture that returns service instance."""
        return RoomService(RoomRepository())
    
    def test_filter_rooms_by_tipo(self, room_service):
        """Test filtering rooms by tipo."""
        room1 = RoomFactory(tipo='standard', is_active=True)
        room2 = RoomFactory(tipo='luxo', is_active=True, hotel=room1.hotel)
        
        filtered = room_service.filter_rooms(hotel_id=room1.hotel.id, tipo='standard')
        
        assert len(filtered) == 1
        assert filtered[0].id == room1.id
    
    def test_filter_rooms_by_price_range(self, room_service):
        """Test filtering rooms by price range."""
        room1 = RoomFactory(preco_diaria=100.0, is_active=True)
        room2 = RoomFactory(preco_diaria=200.0, is_active=True, hotel=room1.hotel)
        room3 = RoomFactory(preco_diaria=300.0, is_active=True, hotel=room1.hotel)
        
        filtered = room_service.filter_rooms(
            hotel_id=room1.hotel.id,
            min_price=150.0,
            max_price=250.0
        )
        
        assert len(filtered) == 1
        assert filtered[0].id == room2.id
    
    def test_filter_rooms_by_capacidade(self, room_service):
        """Test filtering rooms by capacidade."""
        room1 = RoomFactory(capacidade=2, is_active=True)
        room2 = RoomFactory(capacidade=4, is_active=True, hotel=room1.hotel)
        
        filtered = room_service.filter_rooms(
            hotel_id=room1.hotel.id,
            capacidade=3
        )
        
        assert len(filtered) == 1
        assert filtered[0].id == room2.id
