"""
Service para lógica de negócio de Hotel.
"""
import logging
from typing import Optional, List, Dict, Any
from core.exceptions import (
    EmailAlreadyExistsError,
    UserNotFoundError
)
from reserveme.repositories.hotel_repository import HotelRepository
from reserveme.models import Hotel

logger = logging.getLogger(__name__)


class HotelAlreadyExistsError(Exception):
    """Exceção quando hotel já existe."""
    pass


class HotelNotFoundError(Exception):
    """Exceção quando hotel não é encontrado."""
    pass


class HotelService:
    """Service para gerenciar lógica de negócio de Hotel."""
    
    def __init__(self, hotel_repository: HotelRepository):
        self.hotel_repository = hotel_repository
    
    def create_hotel(self, hotel_data: Dict[str, Any]) -> Hotel:
        """
        Cria um novo hotel.
        
        Args:
            hotel_data: Dados do hotel
            
        Returns:
            Hotel criado
            
        Raises:
            HotelAlreadyExistsError: Se hotel com mesmo nome ou email já existe
        """
        nome = hotel_data.get('nome')
        email = hotel_data.get('email')
        
        if self.hotel_repository.nome_exists(nome):
            logger.warning(f"Tentativa de criar hotel com nome duplicado: {nome}")
            raise HotelAlreadyExistsError("Já existe um hotel com este nome.")
        
        if self.hotel_repository.email_exists(email):
            logger.warning(f"Tentativa de criar hotel com email duplicado: {email}")
            raise HotelAlreadyExistsError("Já existe um hotel com este email.")
        
        hotel = self.hotel_repository.create(**hotel_data)
        logger.info(f"Hotel criado com sucesso: {hotel.nome} (ID: {hotel.id})")
        
        return hotel
    
    def get_hotel(self, hotel_id: int) -> Hotel:
        """
        Busca hotel por ID.
        
        Args:
            hotel_id: ID do hotel
            
        Returns:
            Hotel encontrado
            
        Raises:
            HotelNotFoundError: Se hotel não for encontrado
        """
        hotel = self.hotel_repository.get_by_id(hotel_id)
        
        if not hotel:
            logger.warning(f"Hotel não encontrado: ID {hotel_id}")
            raise HotelNotFoundError("Hotel não encontrado.")
        
        return hotel
    
    def list_hotels(self, filters: Optional[Dict[str, Any]] = None) -> List[Hotel]:
        """
        Lista hotéis com filtros opcionais.
        
        Args:
            filters: Filtros para a listagem
            
        Returns:
            Lista de hotéis
        """
        if filters:
            return self.hotel_repository.list_with_filters(filters)
        return self.hotel_repository.get_all()
    
    def list_active_hotels(self) -> List[Hotel]:
        """
        Lista apenas hotéis ativos.
        
        Returns:
            Lista de hotéis ativos
        """
        return self.hotel_repository.get_active_hotels()
    
    def update_hotel(self, hotel_id: int, update_data: Dict[str, Any]) -> Hotel:
        """
        Atualiza dados do hotel.
        
        Args:
            hotel_id: ID do hotel
            update_data: Dados para atualizar
            
        Returns:
            Hotel atualizado
            
        Raises:
            HotelNotFoundError: Se hotel não for encontrado
            HotelAlreadyExistsError: Se nome ou email já existem
        """
        hotel = self.get_hotel(hotel_id)
        
        # Validar nome único se está sendo atualizado
        if 'nome' in update_data and update_data['nome'] != hotel.nome:
            if self.hotel_repository.nome_exists(update_data['nome'], exclude_id=hotel_id):
                raise HotelAlreadyExistsError("Já existe um hotel com este nome.")
        
        # Validar email único se está sendo atualizado
        if 'email' in update_data and update_data['email'] != hotel.email:
            if self.hotel_repository.email_exists(update_data['email'], exclude_id=hotel_id):
                raise HotelAlreadyExistsError("Já existe um hotel com este email.")
        
        updated_hotel = self.hotel_repository.update(hotel, **update_data)
        logger.info(f"Hotel atualizado: {updated_hotel.nome} (ID: {updated_hotel.id})")
        
        return updated_hotel
    
    def delete_hotel(self, hotel_id: int) -> bool:
        """
        Deleta um hotel (soft delete - marca como inativo).
        
        Args:
            hotel_id: ID do hotel
            
        Returns:
            True se deletado com sucesso
            
        Raises:
            HotelNotFoundError: Se hotel não for encontrado
        """
        hotel = self.get_hotel(hotel_id)
        hotel.is_active = False
        hotel.save()
        
        logger.info(f"Hotel desativado: {hotel.nome} (ID: {hotel.id})")
        return True
