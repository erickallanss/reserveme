"""
Repository para ExampleModel.
Implementa o protocolo BaseRepositoryProtocol.
"""
from typing import Optional, List
from reserveme.models import ExampleModel
from reserveme.repositories.base import BaseRepository


class ExampleRepository(BaseRepository[ExampleModel]):
    """
    Repository para ExampleModel.
    Implementa operações de banco de dados específicas.
    """
    
    def __init__(self):
        super().__init__(ExampleModel)
    
    def get_by_name(self, name: str) -> Optional[ExampleModel]:
        """Busca uma instância pelo nome."""
        return self.get(name=name)
    
    def get_by_user(self, user_id: int) -> List[ExampleModel]:
        """Busca todos os exemplos criados por um usuário."""
        return list(self.filter(created_by_id=user_id))
