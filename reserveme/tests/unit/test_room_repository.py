"""
Testes unitários para o repositório de Room.
"""
import pytest
from reserveme.repositories.room_repository import RoomRepository
from reserveme.tests.room_factories import RoomFactory
from reserveme.tests.hotel_factories import HotelFactory


@pytest.mark.django_db
class TestRoomRepository:
    """Testes para RoomRepository."""
    
    @pytest.fixture
    def room_repository(self):
        """Fixture que retorna instância do repositório."""
        return RoomRepository()
    
    def test_create_room(self, room_repository):
        """Testa criação de quarto."""
        hotel = HotelFactory()
        room_data = {
            'hotel': hotel,
            'numero': '101',
            'tipo': 'double',
            'capacidade': 2,
            'preco_diaria': '250.00'
        }
        
        room = room_repository.create(**room_data)
        
        assert room.id is not None
        assert room.numero == '101'
        assert room.hotel.id == hotel.id
    
    def test_get_by_id(self, room_repository):
        """Testa busca por ID."""
        room = RoomFactory()
        
        found_room = room_repository.get_by_id(room.id)
        
        assert found_room is not None
        assert found_room.id == room.id
    
    def test_get_by_hotel(self, room_repository):
        """Testa busca de quartos por hotel."""
        hotel = HotelFactory()
        room1 = RoomFactory(hotel=hotel)
        room2 = RoomFactory(hotel=hotel)
        other_room = RoomFactory()  # Outro hotel
        
        rooms = room_repository.get_by_hotel(hotel.id)
        
        assert len(rooms) == 2
        assert room1.id in [r.id for r in rooms]
        assert room2.id in [r.id for r in rooms]
        assert other_room.id not in [r.id for r in rooms]
    
    def test_get_active_rooms(self, room_repository):
        """Testa busca de quartos ativos."""
        active_room = RoomFactory(is_active=True)
        inactive_room = RoomFactory(is_active=False)
        
        active_rooms = room_repository.get_active_rooms()
        
        assert active_room.id in [r.id for r in active_rooms]
        assert inactive_room.id not in [r.id for r in active_rooms]
    
    def test_get_by_numero(self, room_repository):
        """Testa busca por número dentro de um hotel."""
        hotel = HotelFactory()
        room = RoomFactory(hotel=hotel, numero='202')
        
        found_room = room_repository.get_by_numero(hotel.id, '202')
        
        assert found_room is not None
        assert found_room.id == room.id
    
    def test_numero_exists(self, room_repository):
        """Testa verificação de existência de número."""
        hotel = HotelFactory()
        room = RoomFactory(hotel=hotel, numero='303')
        
        assert room_repository.numero_exists(hotel.id, '303') is True
        assert room_repository.numero_exists(hotel.id, '404') is False
    
    def test_get_rooms_by_tipo(self, room_repository):
        """Testa busca por tipo."""
        suite1 = RoomFactory(tipo='suite')
        suite2 = RoomFactory(tipo='suite')
        double = RoomFactory(tipo='double')
        
        suites = room_repository.get_rooms_by_tipo('suite')
        
        assert len(suites) >= 2
        assert suite1.id in [r.id for r in suites]
        assert suite2.id in [r.id for r in suites]
        assert double.id not in [r.id for r in suites]
    
    def test_get_rooms_by_price_range(self, room_repository):
        """Testa busca por faixa de preço."""
        cheap = RoomFactory(preco_diaria='150.00')
        medium = RoomFactory(preco_diaria='250.00')
        expensive = RoomFactory(preco_diaria='500.00')
        
        rooms = room_repository.get_rooms_by_price_range(200.0, 300.0)
        
        assert medium.id in [r.id for r in rooms]
        assert cheap.id not in [r.id for r in rooms]
        assert expensive.id not in [r.id for r in rooms]
