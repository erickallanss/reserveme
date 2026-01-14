# Quick Start - ReserveMe API

## Status dos Containers

Todos os serviços estão rodando:

```bash
✅ PostgreSQL   - Porta 5432
✅ Redis        - Porta 6379  
✅ Django API   - Porta 8000
✅ Celery       - Worker em execução
✅ Celery Beat  - Scheduler em execução
```

## Acessar a API

### Documentação
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Admin**: http://localhost:8000/admin/

### Endpoints Disponíveis

#### Autenticação JWT
```bash
# Obter token
POST http://localhost:8000/api/auth/token/
Body: {"username": "user", "password": "pass"}

# Refresh token
POST http://localhost:8000/api/auth/token/refresh/
Body: {"refresh": "token"}

# Verificar token
POST http://localhost:8000/api/auth/token/verify/
Body: {"token": "token"}
```

#### Examples API (v1)
```bash
# Listar (requer autenticação)
GET http://localhost:8000/api/v1/examples/
Header: Authorization: Bearer <token>

# Criar
POST http://localhost:8000/api/v1/examples/
Header: Authorization: Bearer <token>
Body: {"name": "Exemplo", "description": "Descrição"}

# Buscar
GET http://localhost:8000/api/v1/examples/1/

# Atualizar
PATCH http://localhost:8000/api/v1/examples/1/
Body: {"name": "Novo nome"}

# Deletar
DELETE http://localhost:8000/api/v1/examples/1/
```

## Criar Superuser

```bash
docker compose exec web python manage.py createsuperuser
```

## Testar Email Assíncrono

```python
# No Django shell
docker compose exec web python manage.py shell

from core.utils.helpers import send_email_async

# Enviar email (será impresso no console)
send_email_async(
    subject='Teste',
    message='Mensagem de teste',
    recipient_list=['test@example.com']
)

# Verificar logs do Celery
# docker compose logs celery -f
```

## Executar Testes

```bash
# Todos os testes
docker compose exec web pytest

# Apenas repository
docker compose exec web pytest reserveme/tests/unit/test_example_repository.py -v

# Apenas service
docker compose exec web pytest reserveme/tests/unit/test_example_service.py -v

# Apenas views
docker compose exec web pytest reserveme/tests/unit/test_example_views.py -v

# Com cobertura
docker compose exec web pytest --cov=reserveme --cov-report=term-missing
```

## Estrutura da Arquitetura

```
Request → View (enxuta)
            ↓
         Service (lógica de negócio)
            ↓
         Repository (acesso ao banco)
            ↓
         Database
```

### Exemplo de Uso

```python
# 1. View recebe request
@api_view(['POST'])
def example_create(request):
    service = container.example_service()  # DI
    return service.create_example(request.user, request.data)

# 2. Service valida e processa
class ExampleService:
    def create_example(self, user, data):
        validated = self.validate(data)  # Lógica de negócio
        return self.repository.create(**validated)  # Delega para repository

# 3. Repository acessa banco
class ExampleRepository:
    def create(self, **kwargs):
        return self.model.objects.create(**kwargs)  # Apenas DB
```

## Próximos Passos

1. **Criar suas próprias funcionalidades** seguindo o padrão do ExampleModel
2. **Adicionar autenticação customizada** se necessário
3. **Configurar SMTP real** para envio de emails (atualmente usa console)
4. **Adicionar mais testes** para suas funcionalidades
5. **Deploy** quando estiver pronto

## Comandos Docker Compose

```bash
# Ver status
docker compose ps

# Ver logs
docker compose logs -f web
docker compose logs -f celery
docker compose logs -f celery-beat

# Parar tudo
docker compose down

# Reconstruir
docker compose up -d --build

# Executar comandos Django
docker compose exec web python manage.py <comando>

# Acessar shell do container
docker compose exec web bash

# Reiniciar um serviço
docker compose restart web
```

## Troubleshooting

### Container não inicia
```bash
docker compose logs web
docker compose ps
```

### Migração falhou
```bash
docker compose exec web python manage.py showmigrations
docker compose exec web python manage.py migrate --fake <app> <migration>
```

### Celery não está processando
```bash
docker compose logs celery
docker compose exec celery celery -A core inspect ping
```

### Banco de dados
```bash
# Acessar
docker compose exec db psql -U reserveme

# Resetar
docker compose down -v  # Remove volumes
docker compose up -d --build
```

## Tudo Pronto!

A API está rodando em: **http://localhost:8000**

Acesse a documentação: **http://localhost:8000/api/docs/**
