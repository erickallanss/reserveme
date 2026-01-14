"""
Protocols (contratos) para repositories.
Define a interface que todos os repositories devem seguir.
"""
from typing import Protocol, TypeVar, Generic, Optional, List
from django.db.models import Model

T = TypeVar('T', bound=Model)


class BaseRepositoryProtocol(Protocol[T]):
    """
    Protocol base para todos os repositories.
    Define o contrato mínimo que um repository deve implementar.
    """
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Busca uma instância pelo ID."""
        ...
    
    def get_all(self) -> List[T]:
        """Retorna todas as instâncias."""
        ...
    
    def create(self, **kwargs) -> T:
        """Cria uma nova instância."""
        ...
    
    def update(self, instance: T, **kwargs) -> T:
        """Atualiza uma instância existente."""
        ...
    
    def delete(self, instance: T) -> None:
        """Deleta uma instância."""
        ...
    
    def exists(self, id: int) -> bool:
        """Verifica se uma instância existe pelo ID."""
        ...
