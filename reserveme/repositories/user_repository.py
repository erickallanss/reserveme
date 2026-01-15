"""
Repository para operações de User.
"""
from typing import Optional
from django.contrib.auth import get_user_model
from .base import BaseRepository

User = get_user_model()


class UserRepository(BaseRepository[User]):
    """
    Repository para User com operações específicas.
    """
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Busca usuário por email."""
        return self.get(email=email.lower())
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Busca usuário por username."""
        return self.get(username=username.lower())
    
    def get_by_cpf(self, cpf: str) -> Optional[User]:
        """Busca usuário por CPF."""
        return self.get(cpf=cpf)
    
    def get_by_verification_token(self, token: str) -> Optional[User]:
        """Busca usuário por token de verificação."""
        return self.get(email_verification_token=token)
    
    def email_exists(self, email: str) -> bool:
        """Verifica se email já existe."""
        return self.model.objects.filter(email=email.lower()).exists()
    
    def username_exists(self, username: str) -> bool:
        """Verifica se username já existe."""
        return self.model.objects.filter(username=username.lower()).exists()
    
    def cpf_exists(self, cpf: str) -> bool:
        """Verifica se CPF já existe."""
        return self.model.objects.filter(cpf=cpf).exists()
    
    def get_by_role(self, role: str):
        """Lista usuários por role."""
        return self.filter(role=role, is_active=True)
