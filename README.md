# ReserveMe

Sistema de reservas desenvolvido com Django, Docker e uv.

## Requisitos

- Docker
- Docker Compose

## Configuração

1. Clone o repositório (se aplicável)

2. Copie o arquivo de exemplo de variáveis de ambiente:
   ```bash
   cp .env.example .env
   ```

3. Edite o arquivo `.env` com suas configurações (opcional, já há valores padrão)

## Executando o projeto

### Iniciar os serviços

```bash
docker-compose up --build
```

### Criar as migrações

```bash
docker-compose exec web python manage.py makemigrations
```

### Aplicar as migrações

```bash
docker-compose exec web python manage.py migrate
```

### Criar um superusuário

```bash
docker-compose exec web python manage.py createsuperuser
```

## Acessar a aplicação

- Aplicação: http://localhost:8000
- Admin: http://localhost:8000/admin

## Estrutura do projeto

```
reserveme/
├── core/              # Configurações principais do Django
├── manage.py          # Script de gerenciamento do Django
├── Dockerfile         # Configuração da imagem Docker
├── docker-compose.yml # Orquestração dos serviços
├── pyproject.toml     # Dependências do projeto (uv)
└── README.md          # Este arquivo
```

## Comandos úteis

### Parar os serviços
```bash
docker-compose down
```

### Ver logs
```bash
docker-compose logs -f web
```

### Executar comandos Django
```bash
docker-compose exec web python manage.py <comando>
```

### Acessar o shell do container
```bash
docker-compose exec web bash
```

## Serviços

O projeto inclui os seguintes serviços:

- **web**: Aplicação Django (porta 8000)
- **db**: PostgreSQL (porta 5432)
- **redis**: Redis para Celery (porta 6379)
- **celery**: Worker do Celery para processar tarefas assíncronas
- **celery-beat**: Scheduler do Celery para tarefas periódicas

### Ver logs dos serviços

```bash
# Logs de todos os serviços
docker-compose logs -f

# Logs de um serviço específico
docker-compose logs -f celery
docker-compose logs -f celery-beat
```

### Comandos Celery

```bash
# Executar worker manualmente
docker-compose exec celery celery -A core worker --loglevel=info

# Executar beat manualmente
docker-compose exec celery-beat celery -A core beat --loglevel=info

# Verificar status do Celery
docker-compose exec celery celery -A core inspect active
```

## Desenvolvimento

O projeto usa:
- **Django 5.x**: Framework web
- **PostgreSQL**: Banco de dados
- **Redis**: Broker e backend de resultados para Celery
- **Celery**: Processamento de tarefas assíncronas
- **Celery Beat**: Agendamento de tarefas periódicas
- **uv**: Gerenciador de pacotes Python
- **Docker**: Containerização

## Criando tarefas Celery

Para criar uma nova tarefa, crie um arquivo `tasks.py` em sua app Django:

```python
from celery import shared_task

@shared_task
def minha_tarefa(parametro):
    # Seu código aqui
    return resultado
```

Para agendar tarefas periódicas, edite `CELERY_BEAT_SCHEDULE` em `core/settings.py`.
