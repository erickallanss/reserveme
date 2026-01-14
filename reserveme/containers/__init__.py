"""
Container de injeção de dependência.
Centraliza a criação e configuração de todas as dependências.
"""
from dependency_injector import containers, providers
from reserveme.repositories.example_repository import ExampleRepository
from reserveme.repositories.user_repository import UserRepository
from reserveme.services.example_service import ExampleService
from reserveme.services.auth_service import AuthService


class ApplicationContainer(containers.DeclarativeContainer):
    """
    Container principal da aplicação.
    Define todas as dependências e suas configurações.
    """
    
    # Configuração
    config = providers.Configuration()
    
    # Repositories (Singleton - uma instância compartilhada)
    example_repository = providers.Singleton(
        ExampleRepository,
    )
    
    user_repository = providers.Singleton(
        UserRepository,
    )
    
    # Services (Factory - nova instância a cada chamada)
    example_service = providers.Factory(
        ExampleService,
        repository=example_repository,
    )
    
    auth_service = providers.Factory(
        AuthService,
        repository=user_repository,
    )


# Instância global do container
container = ApplicationContainer()
