"""
Container de injeção de dependência.
Centraliza a criação e configuração de todas as dependências.
"""
from dependency_injector import containers, providers
from reserveme.repositories.user_repository import UserRepository
from reserveme.services.auth_service import AuthService


class ApplicationContainer(containers.DeclarativeContainer):
    """
    Container principal da aplicação.
    Define todas as dependências e suas configurações.
    """
    
    config = providers.Configuration()
    
    user_repository = providers.Singleton(
        UserRepository,
    )
    
    auth_service = providers.Factory(
        AuthService,
        repository=user_repository,
    )


container = ApplicationContainer()
