"""
Testes unitários para o service de Room.
"""
import pytest
from decimal import Decimal
from reserveme.services.room_service import (
    RoomService,
    RoomNotFoundError,
    RoomAlreadyExistsError
)
from reserveme.repositories.room_repository import RoomRepository
from reserveme.tests.room_factories import RoomFactory
from reserveme.tests.hotel_factories import HotelFactory


@pytest.mark.django_db
class TestRoomService:
    """Testes para RoomService."""
    
    @pytest.fixture
    def room_service(self):
        """Fixture que retorna instância do service."""
        return RoomService(RoomRepository())
    
    def test_create_room(self, room_service):
        """Testa criação de quarto."""
        hotel = HotelFactory()
        room_data = {
            'hotel': hotel,
            'numero': '101',
            'tipo': 'double',
            'capacidade': 2,
            'preco_diaria': Decimal('250.00')
        }
        
        room = room_service.create_room(room_data)
        
        assert room.id is not None
        assert room.numero == '101'
    
    def test_create_room_duplicate_number(self, room_service):
        """Testa erro ao criar quarto com número duplicado."""
        hotel = HotelFactory()
        RoomFactory(hotel=hotel, numero='101')
        
        room_data = {
            'hotel': hotel,
            'numero': '101',
            'tipo': 'double',
            'capacidade': 2,
            'preco_diaria': Decimal('250.00')
        }
        
        with pytest.raises(RoomAlreadyExistsError):
            room_service.create_room(room_data)
    
    def test_get_room(self, room_service):
        """Testa busca de quarto por ID."""
        room = RoomFactory()
        
        found_room = room_service.get_room(room.id)
        
        assert found_room.id == room.id
    
    def test_get_room_not_found(self, room_service):
        """Testa erro ao buscar quarto inexistente."""
        with pytest.raises(RoomNotFoundError):
            room_service.get_room(99999)
    
    def test_list_active_rooms(self, room_service):
        """Testa listagem de quartos ativos."""
        active = RoomFactory(is_active=True)
        inactive = RoomFactory(is_active=False)
        
        rooms = room_service.list_active_rooms()
        
        assert active.id in [r.id for r in rooms]
        assert inactive.id not in [r.id for r in rooms]
    
    def test_update_room(self, room_service):
        """Testa atualização de quarto."""
        room = RoomFactory()
        
        updated_room = room_service.update_room(
            room.id,
            {'preco_diaria': Decimal('300.00')}
        )
        
        assert updated_room.preco_diaria == Decimal('300.00')
    
    def test_delete_room(self, room_service):
        """Testa desativação de quarto."""
        room = RoomFactory(is_active=True)
        
        room_service.delete_room(room.id)
        
        updated_room = room_service.get_room(room.id)
        assert updated_room.is_active is False
