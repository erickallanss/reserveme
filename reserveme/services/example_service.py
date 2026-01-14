"""
Service para ExampleModel.
Contém lógica de negócio.
"""
from typing import Optional, List, Dict, Any
from django.contrib.auth.models import User
from reserveme.models import ExampleModel
from reserveme.services.base import BaseService


class ExampleService(BaseService[ExampleModel]):
    """
    Service para ExampleModel.
    Contém toda a lógica de negócio relacionada a exemplos.
    """
    
    def __init__(self, repository):
        """Inicializa o service com o repository."""
        super().__init__(repository)
    
    def create_example(self, user: User, data: Dict[str, Any]) -> ExampleModel:
        """Cria um novo exemplo."""
        validated_data = self.validate(data)
        validated_data['created_by'] = user
        return self.repository.create(**validated_data)
    
    def get_example(self, example_id: int) -> Optional[ExampleModel]:
        """Busca um exemplo pelo ID."""
        return self.repository.get_by_id(example_id)
    
    def list_examples(self, user: Optional[User] = None) -> List[ExampleModel]:
        """Lista exemplos."""
        if user:
            return self.repository.get_by_user(user.id)
        return self.repository.get_all()
    
    def update_example(
        self,
        example_id: int,
        data: Dict[str, Any],
        user: Optional[User] = None
    ) -> Optional[ExampleModel]:
        """Atualiza um exemplo."""
        example = self.repository.get_by_id(example_id)
        if not example:
            return None
        
        if user and example.created_by != user:
            raise PermissionError("Você não tem permissão para atualizar este exemplo")
        
        validated_data = self.validate(data)
        return self.repository.update(example, **validated_data)
    
    def delete_example(self, example_id: int, user: Optional[User] = None) -> bool:
        """Deleta um exemplo."""
        example = self.repository.get_by_id(example_id)
        if not example:
            return False
        
        if user and example.created_by != user:
            raise PermissionError("Você não tem permissão para deletar este exemplo")
        
        self.repository.delete(example)
        return True
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida dados do exemplo."""
        if 'name' not in data or not data['name'].strip():
            raise ValueError("O campo 'name' é obrigatório")
        
        if len(data['name']) > 100:
            raise ValueError("O campo 'name' deve ter no máximo 100 caracteres")
        
        return data
