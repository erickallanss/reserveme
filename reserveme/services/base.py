"""
Classe base para services.
Services contêm lógica de negócio e não interagem diretamente com o banco.
"""
from abc import ABC
from typing import TypeVar, Generic

T = TypeVar('T')


class BaseService(ABC, Generic[T]):
    """
    Classe base abstrata para services.
    Services devem conter apenas lógica de negócio.
    """
    
    def __init__(self, repository):
        """Inicializa o service com um repository."""
        self.repository = repository
    
    def validate(self, data: dict) -> dict:
        """Valida dados antes de processar."""
        return data
    
    def _check_permissions(self, user, action: str) -> bool:
        """Verifica permissões do usuário."""
        return True
