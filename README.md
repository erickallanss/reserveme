# 🏨 ReserveMe API

Sistema completo de reservas de hotéis desenvolvido com Django REST Framework, Celery e Docker.

## ✨ Funcionalidades

- 🔐 **Autenticação JWT** com cookies HTTP-only
- 👥 **3 níveis de usuário**: Admin, Staff, Customer
- 🏨 **Gerenciamento de Hotéis** e Quartos
- 📅 **Sistema de Reservas** com verificação de disponibilidade
- 📧 **Emails assíncronos** com Celery
- ⏰ **Tarefas agendadas** com Celery Beat
- 🐳 **Totalmente dockerizado**
- 📚 **Documentação automática** com Swagger/ReDoc

---

## 🚀 Quick Start

### Opção 1: Comando Único (Recomendado)

```bash
make server
```

Este comando faz **TUDO automaticamente**:
- ✅ Build dos containers
- ✅ Sobe todos os serviços
- ✅ Cria e aplica migrations
- ✅ **Popula banco com dados de teste** (se vazio)
- ✅ Mostra credenciais de acesso

**Pronto!** Acesse:
- 🌐 **API**: http://localhost:8000
- 📚 **Swagger**: http://localhost:8000/api/docs/
- 🔐 **Admin**: http://localhost:8000/admin/
- 📧 **Mailpit**: http://localhost:8025

### Opção 2: Passo a Passo

```bash
# 1. Build e sobe containers
docker compose up --build -d

# 2. Aguarda containers iniciarem
sleep 5

# 3. Aplica migrations
docker compose exec web python manage.py migrate

# 4. Popula dados de teste
docker compose exec web python seed_data.py
```

---

## 👤 Credenciais Padrão

Após executar `make server` ou `seed_data.py`:

| Tipo | Email | Senha | Permissões |
|------|-------|-------|------------|
| **Admin** | admin@reserveme.com | admin123 | Acesso total |
| **Staff** | staff@reserveme.com | staff123 | Gerencia reservas |
| **Cliente** | joao.silva@example.com | cliente123 | Faz reservas |
| **Cliente** | maria.santos@example.com | cliente123 | Faz reservas |

---

## 📋 Comandos Make Disponíveis

### 🚀 Principais

```bash
make server          # Inicia tudo (build, migrate, seed se vazio)
make up              # Sobe containers
make down            # Para containers
make restart         # Reinicia containers
make logs            # Ver logs de todos os serviços
```

### 🗄️ Banco de Dados

```bash
make migrate         # Aplica migrations
make makemigrations  # Cria novas migrations
make seed            # Popula dados de teste (força)
make db-reset        # Reseta banco e popula novamente
make dbshell         # Acessa shell do PostgreSQL
```

### 🧪 Testes

```bash
make test            # Roda todos os testes
make test-cov        # Testes com cobertura
make test-unit       # Apenas testes unitários
make test-integration # Apenas testes de integração
```

### 🔧 Utilitários

```bash
make shell           # Django shell
make createsuperuser # Criar superusuário
make api-docs        # Abre Swagger no navegador
make mailpit         # Abre Mailpit no navegador
make help            # Lista todos os comandos
```

---

## 📊 Dados de Teste Criados

Ao executar `make server` ou `make seed`, são criados:

### 🏨 1 Hotel
- **Hotel Paradise Beach** (Copacabana, RJ)

### 🛏️ 8 Quartos
| Nº | Tipo | Preço/Dia |
|----|------|-----------|
| 101 | Solteiro | R$ 150 |
| 102 | Casal | R$ 250 |
| 103 | Twin | R$ 240 |
| 201 | Casal Superior | R$ 300 |
| 202 | Triplo | R$ 350 |
| 301 | Suíte | R$ 500 |
| 302 | Deluxe | R$ 750 |
| 401 | Presidencial | R$ 1.500 |

### 👥 6 Usuários
- 1 Admin, 1 Staff, 4 Clientes

### 📅 7 Reservas
- Confirmadas, Pendentes, Check-in, Concluídas

---

## 🌐 Endpoints da API

### 🔐 Authentication (8 endpoints)
```
POST   /api/v1/auth/register/
POST   /api/v1/auth/verify-email/
POST   /api/v1/auth/login/
POST   /api/v1/auth/logout/
GET    /api/v1/auth/me/
PATCH  /api/v1/auth/me/
POST   /api/v1/auth/change-password/
POST   /api/v1/auth/refresh/
```

### 🏨 Hotels (6 endpoints)
```
GET    /api/v1/hotels/
POST   /api/v1/hotels/          (admin)
GET    /api/v1/hotels/{id}/
PUT    /api/v1/hotels/{id}/     (admin)
PATCH  /api/v1/hotels/{id}/     (admin)
DELETE /api/v1/hotels/{id}/     (admin)
```

### 🛏️ Rooms (6 endpoints)
```
GET    /api/v1/rooms/
POST   /api/v1/rooms/           (staff/admin)
GET    /api/v1/rooms/{id}/
PUT    /api/v1/rooms/{id}/      (staff/admin)
PATCH  /api/v1/rooms/{id}/      (staff/admin)
DELETE /api/v1/rooms/{id}/      (staff/admin)
```

### 📅 Bookings (8 endpoints)
```
GET    /api/v1/bookings/
POST   /api/v1/bookings/
GET    /api/v1/bookings/{id}/
DELETE /api/v1/bookings/{id}/
POST   /api/v1/bookings/{id}/confirm/   (staff)
POST   /api/v1/bookings/{id}/checkin/   (staff)
POST   /api/v1/bookings/{id}/checkout/  (staff)
GET    /api/v1/hotels/{id}/bookings/    (staff)
```

**Total**: 26 endpoints

---

## 📧 Emails Automáticos

Todos os emails são capturados pelo **Mailpit** (http://localhost:8025):

1. ✅ **Reserva Criada** - Quando cliente cria reserva
2. ✅ **Reserva Confirmada** - Quando staff confirma
3. ✅ **Reserva Cancelada** - Cancelamento manual
4. ✅ **Reserva Expirada** - Cancelamento automático (Celery Beat)

---

## ⏰ Celery Beat - Tarefa Agendada

**Task**: `release_expired_bookings_task()`
- 🔄 Executa **a cada 1 hora**
- 🔍 Busca reservas `pending` com check-in passado
- ❌ Cancela automaticamente
- 📧 Envia email de notificação

### Ver Logs
```bash
make logs-celery-beat
```

---

## 🧪 Testando a API

### 1. Via Swagger (Recomendado)
```
http://localhost:8000/api/docs/
```

### 2. Via Postman
```bash
# Importe os arquivos:
postman/ReserveMe_API.postman_collection.json
postman/ReserveMe_Local.postman_environment.json
```

### 3. Via cURL
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@reserveme.com","password":"admin123"}'

# Listar hotéis
curl http://localhost:8000/api/v1/hotels/

# Criar reserva (após login)
curl -X POST http://localhost:8000/api/v1/bookings/ \
  -H "Content-Type: application/json" \
  -d '{
    "room": 1,
    "data_checkin": "2026-03-01",
    "data_checkout": "2026-03-05",
    "numero_hospedes": 2
  }'
```

---

## 🏗️ Arquitetura

### Serviços Docker
- **web**: Django (porta 8000)
- **db**: PostgreSQL (porta 5432)
- **redis**: Redis (porta 6379)
- **celery**: Worker para tarefas assíncronas
- **celery-beat**: Scheduler para tarefas periódicas
- **mailpit**: Captura de emails (portas 8025/1025)

### Estrutura do Código
```
reserveme/
├── models.py           # User, Hotel, Room, Booking
├── repositories/       # Acesso a dados
├── services/           # Lógica de negócio
├── serializers.py      # Validação e serialização
├── views/              # API endpoints
├── tasks.py            # Tarefas Celery
└── tests/              # Testes unitários e integração
```

**Padrão**: Repository + Service Layer

---

## 📚 Documentação Adicional

- **`IMPLEMENTATION_SUMMARY.md`** - Detalhes técnicos completos
- **`API_TESTING_GUIDE.md`** - Guia de testes passo a passo
- **`SEED_README.md`** - Detalhes dos dados de teste
- **`FINAL_DELIVERY.md`** - Resumo da entrega
- **`postman/README.md`** - Guia do Postman

---

## 🛠️ Tecnologias

- **Django 5.x** + **Django REST Framework**
- **PostgreSQL** - Banco de dados
- **Redis** - Broker Celery
- **Celery** + **Celery Beat** - Tasks assíncronas
- **Docker** + **Docker Compose**
- **JWT** - Autenticação
- **Mailpit** - Captura de emails
- **Swagger/ReDoc** - Documentação automática

---

## 🔧 Troubleshooting

### Containers não sobem
```bash
make down
make clean
make server
```

### Banco não migra
```bash
docker compose exec web python manage.py migrate
```

### Celery não processa tasks
```bash
make logs-celery
# Verificar se o worker está rodando
```

### Emails não aparecem
```bash
# Verificar se Mailpit está rodando
docker compose ps mailpit
# Acessar: http://localhost:8025
```

---

## 📝 Licença

Este projeto foi desenvolvido como parte de um desafio técnico.

---

## 🎯 Status do Projeto

✅ **100% Completo e Funcional**

Todos os requisitos implementados:
- ✅ Modelagem completa (Hotels, Rooms, Bookings, Users)
- ✅ Autenticação JWT com 3 níveis de permissão
- ✅ Sistema de reservas com verificação de disponibilidade
- ✅ Emails assíncronos com Celery
- ✅ Tarefa agendada com Celery Beat
- ✅ Dockerização completa
- ✅ Documentação completa
- ✅ Dados de seed prontos

**Pronto para produção!** 🚀

---

**Desenvolvido com** ❤️ **usando Django REST Framework**
