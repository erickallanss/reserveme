"""Repository para operações de Room."""
from typing import Optional, List
from reserveme.repositories.base import BaseRepository
from reserveme.models import Room


class RoomRepository(BaseRepository):
    """Repository para gerenciar operações de Room.
    
    Fornece métodos de acesso a dados para quartos, incluindo
    buscas por hotel, tipo, preço e capacidade.
    """
    
    def __init__(self):
        super().__init__(Room)
    
    def get_by_hotel(self, hotel_id: int) -> List[Room]:
        """Retorna todos os quartos de um hotel.
        
        Args:
            hotel_id: ID do hotel.
            
        Returns:
            Lista de quartos do hotel.
        """
        return list(self.model.objects.filter(hotel_id=hotel_id))
    
    def get_active_rooms(self, hotel_id: Optional[int] = None) -> List[Room]:
        """Retorna quartos ativos, opcionalmente filtrados por hotel.
        
        Args:
            hotel_id: ID do hotel (opcional).
            
        Returns:
            Lista de quartos ativos.
        """
        queryset = self.model.objects.filter(is_active=True)
        if hotel_id:
            queryset = queryset.filter(hotel_id=hotel_id)
        return list(queryset)
    
    def get_by_numero(self, hotel_id: int, numero: str) -> Optional[Room]:
        """Busca quarto por número dentro de um hotel.
        
        Args:
            hotel_id: ID do hotel.
            numero: Número do quarto.
            
        Returns:
            Quarto encontrado ou None.
        """
        return self.model.objects.filter(
            hotel_id=hotel_id,
            numero=numero
        ).first()
    
    def numero_exists(
        self, 
        hotel_id: int, 
        numero: str, 
        exclude_id: Optional[int] = None
    ) -> bool:
        """Verifica se já existe quarto com este número no hotel.
        
        Args:
            hotel_id: ID do hotel.
            numero: Número a verificar.
            exclude_id: ID a excluir da verificação (útil em updates).
            
        Returns:
            True se número já existe, False caso contrário.
        """
        queryset = self.model.objects.filter(
            hotel_id=hotel_id,
            numero=numero
        )
        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)
        return queryset.exists()
    
    def get_rooms_by_tipo(self, tipo: str, hotel_id: Optional[int] = None) -> List[Room]:
        """Retorna quartos filtrados por tipo.
        
        Args:
            tipo: Tipo do quarto (single, double, suite, etc).
            hotel_id: ID do hotel (opcional).
            
        Returns:
            Lista de quartos do tipo especificado.
        """
        queryset = self.model.objects.filter(tipo=tipo, is_active=True)
        if hotel_id:
            queryset = queryset.filter(hotel_id=hotel_id)
        return list(queryset)
    
    def get_rooms_by_price_range(
        self, 
        min_price: float, 
        max_price: float,
        hotel_id: Optional[int] = None
    ) -> List[Room]:
        """Retorna quartos dentro de uma faixa de preço.
        
        Args:
            min_price: Preço mínimo.
            max_price: Preço máximo.
            hotel_id: ID do hotel (opcional).
            
        Returns:
            Lista de quartos na faixa de preço.
        """
        queryset = self.model.objects.filter(
            preco_diaria__gte=min_price,
            preco_diaria__lte=max_price,
            is_active=True
        )
        if hotel_id:
            queryset = queryset.filter(hotel_id=hotel_id)
        return list(queryset)
    
    def get_rooms_by_capacidade(
        self, 
        capacidade: int,
        hotel_id: Optional[int] = None
    ) -> List[Room]:
        """Retorna quartos com capacidade mínima.
        
        Args:
            capacidade: Capacidade mínima desejada.
            hotel_id: ID do hotel (opcional).
            
        Returns:
            Lista de quartos com capacidade >= especificada.
        """
        queryset = self.model.objects.filter(
            capacidade__gte=capacidade,
            is_active=True
        )
        if hotel_id:
            queryset = queryset.filter(hotel_id=hotel_id)
        return list(queryset)
