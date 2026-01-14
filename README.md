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

## Desenvolvimento

O projeto usa:
- **Django 5.x**: Framework web
- **PostgreSQL**: Banco de dados
- **uv**: Gerenciador de pacotes Python
- **Docker**: Containerização
