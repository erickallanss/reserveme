"""
Service para operações de Room.
"""
import logging
from typing import Optional, List, Dict, Any
from reserveme.models import Room
from reserveme.repositories.room_repository import RoomRepository

logger = logging.getLogger(__name__)


class RoomNotFoundError(Exception):
    """Exceção quando quarto não é encontrado."""
    pass


class RoomAlreadyExistsError(Exception):
    """Exceção quando quarto já existe."""
    pass


class RoomService:
    """Service para gerenciar lógica de negócio de Room."""
    
    def __init__(self, room_repository: RoomRepository):
        self.room_repository = room_repository
    
    def create_room(self, data: Dict[str, Any]) -> Room:
        """
        Cria um novo quarto.
        
        Raises:
            RoomAlreadyExistsError: Se já existe quarto com este número no hotel
        """
        hotel_id = data.get('hotel').id if hasattr(data.get('hotel'), 'id') else data.get('hotel')
        numero = data.get('numero')
        
        # Verificar se já existe quarto com este número no hotel
        if self.room_repository.numero_exists(hotel_id, numero):
            raise RoomAlreadyExistsError(
                f"Já existe um quarto com o número '{numero}' neste hotel."
            )
        
        room = self.room_repository.create(data)
        logger.info(f"Quarto criado: {room.hotel.nome} - {room.numero}")
        
        return room
    
    def get_room(self, room_id: int) -> Room:
        """
        Busca quarto por ID.
        
        Raises:
            RoomNotFoundError: Se quarto não existe
        """
        room = self.room_repository.get_by_id(room_id)
        if not room:
            raise RoomNotFoundError(f"Quarto com ID {room_id} não encontrado.")
        return room
    
    def get_room_by_numero(self, hotel_id: int, numero: str) -> Room:
        """
        Busca quarto por número dentro de um hotel.
        
        Raises:
            RoomNotFoundError: Se quarto não existe
        """
        room = self.room_repository.get_by_numero(hotel_id, numero)
        if not room:
            raise RoomNotFoundError(
                f"Quarto '{numero}' não encontrado neste hotel."
            )
        return room
    
    def list_rooms(self, hotel_id: Optional[int] = None) -> List[Room]:
        """Lista todos os quartos, opcionalmente filtrados por hotel."""
        if hotel_id:
            return self.room_repository.get_by_hotel(hotel_id)
        return self.room_repository.get_all()
    
    def list_active_rooms(self, hotel_id: Optional[int] = None) -> List[Room]:
        """Lista quartos ativos."""
        return self.room_repository.get_active_rooms(hotel_id)
    
    def update_room(self, room_id: int, data: Dict[str, Any]) -> Room:
        """
        Atualiza um quarto.
        
        Raises:
            RoomNotFoundError: Se quarto não existe
            RoomAlreadyExistsError: Se novo número já existe
        """
        room = self.get_room(room_id)
        
        # Se está alterando o número, verificar se não existe outro quarto com esse número
        if 'numero' in data and data['numero'] != room.numero:
            hotel_id = data.get('hotel').id if 'hotel' in data else room.hotel_id
            if self.room_repository.numero_exists(hotel_id, data['numero'], exclude_id=room_id):
                raise RoomAlreadyExistsError(
                    f"Já existe um quarto com o número '{data['numero']}' neste hotel."
                )
        
        updated_room = self.room_repository.update(room_id, data)
        logger.info(f"Quarto atualizado: {updated_room.hotel.nome} - {updated_room.numero}")
        
        return updated_room
    
    def delete_room(self, room_id: int) -> None:
        """
        Desativa um quarto (soft delete).
        
        Raises:
            RoomNotFoundError: Se quarto não existe
        """
        room = self.get_room(room_id)
        
        self.room_repository.update(room_id, {'is_active': False})
        logger.info(f"Quarto desativado: {room.hotel.nome} - {room.numero}")
    
    def activate_room(self, room_id: int) -> Room:
        """
        Reativa um quarto.
        
        Raises:
            RoomNotFoundError: Se quarto não existe
        """
        room = self.get_room(room_id)
        
        updated_room = self.room_repository.update(room_id, {'is_active': True})
        logger.info(f"Quarto reativado: {room.hotel.nome} - {room.numero}")
        
        return updated_room
    
    def filter_rooms(
        self,
        hotel_id: Optional[int] = None,
        tipo: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        capacidade: Optional[int] = None
    ) -> List[Room]:
        """Filtra quartos por múltiplos critérios."""
        rooms = self.list_active_rooms(hotel_id)
        
        if tipo:
            rooms = [r for r in rooms if r.tipo == tipo]
        
        if min_price is not None:
            rooms = [r for r in rooms if r.preco_diaria >= min_price]
        
        if max_price is not None:
            rooms = [r for r in rooms if r.preco_diaria <= max_price]
        
        if capacidade is not None:
            rooms = [r for r in rooms if r.capacidade >= capacidade]
        
        return rooms
