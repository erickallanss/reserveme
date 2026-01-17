"""
Repository para operações de Hotel.
"""
from typing import Optional, List
from reserveme.repositories.base import BaseRepository
from reserveme.models import Hotel


class HotelRepository(BaseRepository):
    """Repository para gerenciar operações de Hotel."""
    
    def __init__(self):
        super().__init__(Hotel)
    
    def get_by_nome(self, nome: str) -> Optional[Hotel]:
        """Busca hotel por nome."""
        return self.model.objects.filter(nome__iexact=nome).first()
    
    def get_by_email(self, email: str) -> Optional[Hotel]:
        """Busca hotel por email."""
        return self.model.objects.filter(email__iexact=email).first()
    
    def get_active_hotels(self) -> List[Hotel]:
        """Retorna todos os hotéis ativos."""
        return list(self.model.objects.filter(is_active=True))
    
    def nome_exists(self, nome: str, exclude_id: Optional[int] = None) -> bool:
        """Verifica se já existe um hotel com este nome."""
        queryset = self.model.objects.filter(nome__iexact=nome)
        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)
        return queryset.exists()
    
    def email_exists(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """Verifica se já existe um hotel com este email."""
        queryset = self.model.objects.filter(email__iexact=email)
        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)
        return queryset.exists()
