"""Unit tests for room activation."""
import pytest
from reserveme.services.room_service import RoomService, RoomNotFoundError
from reserveme.repositories.room_repository import RoomRepository
from reserveme.tests.room_factories import RoomFactory


@pytest.mark.django_db
class TestRoomActivation:
    """Tests for room activation."""
    
    @pytest.fixture
    def room_service(self):
        """Fixture that returns service instance."""
        return RoomService(RoomRepository())
    
    def test_activate_room(self, room_service):
        """Test activating a room."""
        room = RoomFactory(is_active=False)
        
        activated = room_service.activate_room(room.id)
        
        assert activated.is_active is True
        room.refresh_from_db()
        assert room.is_active is True
    
    def test_activate_room_already_active(self, room_service):
        """Test activating already active room."""
        room = RoomFactory(is_active=True)
        
        activated = room_service.activate_room(room.id)
        
        assert activated.is_active is True
        room.refresh_from_db()
        assert room.is_active is True
    
    def test_activate_room_not_found(self, room_service):
        """Test error when activating non-existent room."""
        with pytest.raises(RoomNotFoundError):
            room_service.activate_room(99999)
