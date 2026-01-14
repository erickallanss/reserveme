# Arquitetura do Projeto ReserveMe

## Visão Geral

Este projeto segue uma **arquitetura em camadas** com **inversão de dependência** e **injeção de dependência**, seguindo princípios SOLID e Clean Architecture.

## Estrutura de Camadas

```
┌─────────────────────────────────────────┐
│          HTTP Request                    │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  Views (Camada de Apresentação)         │
│  - Enxutas, apenas validação de entrada │
│  - Delegam para Services                │
│  - Retornam respostas HTTP               │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  Services (Camada de Negócio)           │
│  - Contêm TODA a lógica de negócio      │
│  - Validações de domínio                 │
│  - Regras de permissão                   │
│  - NÃO interagem com banco diretamente  │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  Repositories (Camada de Dados)         │
│  - Interagem APENAS com o banco         │
│  - SEM lógica de negócio                 │
│  - Implementam Protocols (contratos)    │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│          Database (PostgreSQL)           │
└──────────────────────────────────────────┘
```

## Princípios Aplicados

### 1. Inversão de Dependência (DIP)
- Services dependem de **abstrações** (Protocols), não de implementações concretas
- Permite substituir implementações facilmente (ex: PostgreSQL → MongoDB)

### 2. Injeção de Dependência (DI)
- Container gerencia criação e configuração de dependências
- Facilita testes (mock de dependências)
- Reduz acoplamento entre componentes

### 3. Single Responsibility Principle (SRP)
- **Views**: Apenas HTTP request/response
- **Services**: Apenas lógica de negócio
- **Repositories**: Apenas acesso a dados

### 4. Protocol-First Design
- Contratos (Protocols) definidos ANTES das implementações
- Classes base seguem padrão: `Base` + nome do domínio
- Garante consistência e testabilidade

## Estrutura de Arquivos

```
reserveme/
├── models.py                    # Django Models
├── serializers.py               # DRF Serializers
├── urls.py                      # URL routing
│
├── repositories/                # Camada de Dados
│   ├── __init__.py
│   ├── protocols.py            # Protocols (contratos)
│   ├── base.py                 # BaseRepository
│   └── example_repository.py   # Implementações específicas
│
├── services/                    # Camada de Negócio
│   ├── __init__.py
│   ├── base.py                 # BaseService
│   └── example_service.py      # Lógica de negócio
│
├── views/                       # Camada de Apresentação
│   ├── __init__.py
│   └── example_views.py        # Views enxutas
│
├── containers/                  # Injeção de Dependência
│   └── __init__.py             # ApplicationContainer
│
└── tests/                       # Testes
    ├── unit/
    │   ├── test_example_repository.py
    │   ├── test_example_service.py
    │   ├── test_example_views.py
    │   └── test_urls.py
    └── integration/
```

## Exemplo de Uso

### 1. Definir Protocol (Contrato)

```python
# repositories/protocols.py
from typing import Protocol, TypeVar, Optional, List
from django.db.models import Model

T = TypeVar('T', bound=Model)

class BaseRepositoryProtocol(Protocol[T]):
    """Define o contrato que todos os repositories devem seguir."""
    
    def get_by_id(self, id: int) -> Optional[T]: ...
    def create(self, **kwargs) -> T: ...
    # ... outros métodos
```

### 2. Implementar Repository

```python
# repositories/example_repository.py
from reserveme.repositories.base import BaseRepository
from reserveme.models import ExampleModel

class ExampleRepository(BaseRepository[ExampleModel]):
    """Implementa operações de banco específicas."""
    
    def __init__(self):
        super().__init__(ExampleModel)
    
    def get_by_name(self, name: str) -> Optional[ExampleModel]:
        return self.get(name=name)
```

### 3. Implementar Service

```python
# services/example_service.py
from reserveme.services.base import BaseService

class ExampleService(BaseService[ExampleModel]):
    """Contém lógica de negócio."""
    
    def __init__(self, repository: ExampleRepositoryProtocol):
        super().__init__(repository)
    
    def create_example(self, user: User, data: Dict) -> ExampleModel:
        # Validação de negócio
        validated_data = self.validate(data)
        
        # Lógica de negócio
        validated_data['created_by'] = user
        
        # Delega para repository
        return self.repository.create(**validated_data)
```

### 4. Configurar Container de DI

```python
# containers/__init__.py
from dependency_injector import containers, providers

class ApplicationContainer(containers.DeclarativeContainer):
    # Repositories (Singleton)
    example_repository = providers.Singleton(ExampleRepository)
    
    # Services (Factory)
    example_service = providers.Factory(
        ExampleService,
        repository=example_repository,
    )

container = ApplicationContainer()
```

### 5. Criar View Enxuta

```python
# views/example_views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from reserveme.containers import container

@api_view(['POST'])
def example_list_create(request):
    # Obter service do container
    service = container.example_service()
    
    # Validar entrada
    serializer = ExampleCreateSerializer(data=request.data)
    if serializer.is_valid():
        # Delegar para service
        example = service.create_example(
            user=request.user,
            data=serializer.validated_data
        )
        return Response(ExampleSerializer(example).data, status=201)
    
    return Response(serializer.errors, status=400)
```

## Testes

### Repository Tests (com banco)
```python
@pytest.mark.django_db
class TestExampleRepository:
    def test_create(self, repository, user):
        example = repository.create(name='Test', created_by=user)
        assert example.id is not None
```

### Service Tests (com mocks)
```python
class TestExampleService:
    def test_create(self, service, user, mock_repository):
        mock_repository.create.return_value = ExampleModel(id=1)
        result = service.create_example(user, {'name': 'Test'})
        assert result.id == 1
```

### View Tests (integração)
```python
@pytest.mark.django_db
class TestExampleViews:
    def test_create(self, authenticated_client):
        response = authenticated_client.post('/api/v1/examples/', data)
        assert response.status_code == 201
```

## Executar Testes

```bash
# Todos os testes
docker compose exec web pytest

# Apenas testes de repository
docker compose exec web pytest reserveme/tests/unit/test_example_repository.py

# Com cobertura
docker compose exec web pytest --cov=reserveme --cov-report=html

# Testes específicos
docker compose exec web pytest reserveme/tests/unit/ -v
docker compose exec web pytest reserveme/tests/integration/ -v
```

## API Endpoints

Base URL: `http://localhost:8000/api/v1/`

### Authentication (JWT)
- `POST /api/auth/token/` - Obter token
- `POST /api/auth/token/refresh/` - Refresh token
- `POST /api/auth/token/verify/` - Verificar token

### Examples
- `GET /api/v1/examples/` - Listar exemplos
- `POST /api/v1/examples/` - Criar exemplo
- `GET /api/v1/examples/{id}/` - Buscar exemplo
- `PUT/PATCH /api/v1/examples/{id}/` - Atualizar exemplo
- `DELETE /api/v1/examples/{id}/` - Deletar exemplo

### Documentation
- `GET /api/docs/` - Swagger UI
- `GET /api/redoc/` - ReDoc
- `GET /api/schema/` - OpenAPI Schema

## Boas Práticas Implementadas

### 1. Type Hints em todo código
```python
def create_example(self, user: User, data: Dict[str, Any]) -> ExampleModel:
    ...
```

### 2. Docstrings completos
```python
def create_example(self, user: User, data: Dict[str, Any]) -> ExampleModel:
    """
    Cria um novo exemplo.
    
    Args:
        user: Usuário que está criando
        data: Dados do exemplo
        
    Returns:
        Exemplo criado
        
    Raises:
        ValueError: Se os dados forem inválidos
    """
```

### 3. Separação de Serializers
- `ExampleSerializer` - Leitura (output)
- `ExampleCreateSerializer` - Criação (input)
- `ExampleUpdateSerializer` - Atualização (input)

### 4. Tratamento de Erros Apropriado
- `ValueError` → 400 Bad Request
- `PermissionError` → 403 Forbidden
- `NotFound` → 404 Not Found

### 5. Rate Limiting
- Anônimos: 100 req/hora
- Autenticados: 1000 req/hora

### 6. Documentação Automática
- Swagger/OpenAPI integrado
- Schemas automáticos com drf-spectacular

### 7. Versionamento de API
- URLs versionadas: `/api/v1/`
- Facilita evolução da API sem breaking changes

## Como Adicionar Nova Funcionalidade

### 1. Criar Model
```python
# models.py
class NewModel(models.Model):
    name = models.CharField(max_length=100)
    # ...
```

### 2. Criar Protocol e Repository
```python
# repositories/new_repository.py
class NewRepository(BaseRepository[NewModel]):
    def __init__(self):
        super().__init__(NewModel)
```

### 3. Criar Service
```python
# services/new_service.py
class NewService(BaseService[NewModel]):
    def __init__(self, repository):
        super().__init__(repository)
```

### 4. Registrar no Container
```python
# containers/__init__.py
new_repository = providers.Singleton(NewRepository)
new_service = providers.Factory(NewService, repository=new_repository)
```

### 5. Criar View
```python
# views/new_views.py
@api_view(['GET'])
def new_list(request):
    service = container.new_service()
    items = service.list_items()
    return Response(serializer.data)
```

### 6. Adicionar URL
```python
# urls.py
path('items/', new_list, name='new-list'),
```

### 7. Criar Testes
```python
# tests/unit/test_new_repository.py
# tests/unit/test_new_service.py
# tests/unit/test_new_views.py
```

## Comandos Úteis

```bash
# Criar superuser
docker compose exec web python manage.py createsuperuser

# Shell do Django
docker compose exec web python manage.py shell

# Ver logs
docker compose logs -f web

# Executar tests
docker compose exec web pytest -v

# Acessar banco
docker compose exec db psql -U reserveme

# Ver tasks do Celery
docker compose exec celery celery -A core inspect active
```

## Status

✅ Django 5.2 configurado  
✅ PostgreSQL configurado  
✅ Redis configurado  
✅ Celery + Celery Beat configurados  
✅ Django REST Framework configurado  
✅ JWT Authentication configurado  
✅ CORS configurado  
✅ API versionada (/api/v1/)  
✅ Documentação Swagger/ReDoc  
✅ Arquitetura em camadas implementada  
✅ Inversão/Injeção de dependência  
✅ Protocols para contratos  
✅ Testes configurados (pytest)  
✅ Email assíncrono com Celery  

**Pronto para desenvolvimento!**
