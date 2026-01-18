# 🧪 Guia de Testes da API - ReserveMe

## 🚀 Quick Start

### 1. Rodar Migrations
```bash
docker compose exec web python manage.py migrate
```

### 2. Criar Superuser (Admin)
```bash
docker compose exec web python manage.py createsuperuser
# Email: admin@example.com
# Password: admin123
```

### 3. Acessar a API
- **API Base URL**: http://localhost:8000/api/v1/
- **Admin Panel**: http://localhost:8000/admin/
- **Swagger Docs**: http://localhost:8000/api/docs/
- **Mailpit**: http://localhost:8025/

---

## 📋 **ENDPOINTS IMPLEMENTADOS**

### 🏨 **Hotels** (já existiam)
```
GET    /api/v1/hotels/              - Listar hotéis
POST   /api/v1/hotels/              - Criar hotel (admin)
GET    /api/v1/hotels/{id}/         - Detalhes do hotel
PUT    /api/v1/hotels/{id}/         - Atualizar hotel (admin)
PATCH  /api/v1/hotels/{id}/         - Atualizar parcial (admin)
DELETE /api/v1/hotels/{id}/         - Desativar hotel (admin)
```

### 🛏️ **Rooms** ⭐ NOVO
```
GET    /api/v1/rooms/               - Listar quartos
POST   /api/v1/rooms/               - Criar quarto (staff/admin)
GET    /api/v1/rooms/{id}/          - Detalhes do quarto
PUT    /api/v1/rooms/{id}/          - Atualizar quarto (staff/admin)
PATCH  /api/v1/rooms/{id}/          - Atualizar parcial (staff/admin)
DELETE /api/v1/rooms/{id}/          - Desativar quarto (staff/admin)
```

### 📅 **Bookings** ⭐ NOVO
```
GET    /api/v1/bookings/                    - Listar minhas reservas
POST   /api/v1/bookings/                    - Criar reserva
GET    /api/v1/bookings/{id}/               - Detalhes da reserva
DELETE /api/v1/bookings/{id}/               - Cancelar reserva
POST   /api/v1/bookings/{id}/confirm/       - Confirmar (staff)
POST   /api/v1/bookings/{id}/checkin/       - Check-in (staff)
POST   /api/v1/bookings/{id}/checkout/      - Check-out (staff)
GET    /api/v1/hotels/{id}/bookings/        - Reservas do hotel (staff)
```

---

## 🧪 **FLUXO DE TESTE COMPLETO**

### Passo 1: Login como Admin
```bash
POST /api/v1/auth/login/
{
  "email": "admin@example.com",
  "password": "admin123"
}
```

### Passo 2: Criar um Hotel
```bash
POST /api/v1/hotels/
{
  "nome": "Hotel Paradise",
  "descricao": "Um hotel maravilhoso",
  "endereco": "Av. Atlântica, 1500 - Rio de Janeiro",
  "telefone": "(21) 98765-4321",
  "email": "contato@hotelparadise.com",
  "horario_checkin": "14:00:00",
  "horario_checkout": "12:00:00"
}
```
✅ **Salve o `id` do hotel**

### Passo 3: Criar Quartos
```bash
POST /api/v1/rooms/
{
  "hotel": 1,
  "numero": "101",
  "tipo": "double",
  "descricao": "Quarto duplo com vista para o mar",
  "capacidade": 2,
  "preco_diaria": "250.00",
  "tem_ar_condicionado": true,
  "tem_wifi": true,
  "tem_tv": true,
  "tem_frigobar": true,
  "tem_varanda": true
}
```

```bash
POST /api/v1/rooms/
{
  "hotel": 1,
  "numero": "102",
  "tipo": "suite",
  "descricao": "Suíte master com jacuzzi",
  "capacidade": 3,
  "preco_diaria": "450.00",
  "tem_ar_condicionado": true,
  "tem_wifi": true,
  "tem_tv": true,
  "tem_frigobar": true,
  "tem_banheira": true,
  "tem_varanda": true
}
```
✅ **Salve o `id` dos quartos**

### Passo 4: Listar Quartos (Público)
```bash
GET /api/v1/rooms/

# Filtrar por hotel
GET /api/v1/rooms/?hotel_id=1

# Filtrar por tipo
GET /api/v1/rooms/?tipo=suite
```

### Passo 5: Registrar um Cliente
```bash
POST /api/v1/auth/register/
{
  "email": "cliente@example.com",
  "username": "cliente123",
  "password": "Cliente123!",
  "password_confirm": "Cliente123!",
  "first_name": "João",
  "last_name": "Silva",
  "cpf": "12345678900",
  "telefone": "(11) 98765-4321",
  "data_nascimento": "1990-01-15"
}
```

### Passo 6: Verificar Email (Mailpit)
1. Acesse: http://localhost:8025
2. Copie o token do email
3. Verifique:
```bash
POST /api/v1/auth/verify-email/
{
  "token": "TOKEN_AQUI"
}
```

### Passo 7: Login como Cliente
```bash
POST /api/v1/auth/login/
{
  "email": "cliente@example.com",
  "password": "Cliente123!"
}
```

### Passo 8: Criar uma Reserva 🎉
```bash
POST /api/v1/bookings/
{
  "room": 1,
  "data_checkin": "2026-02-15",
  "data_checkout": "2026-02-18",
  "numero_hospedes": 2,
  "observacoes": "Preferência por andar alto"
}
```

✅ **Verifique o email no Mailpit!**
✅ **Anote o `codigo_reserva`**

### Passo 9: Listar Reservas

#### Como Cliente
```bash
GET /api/v1/bookings/
```
- Retorna **apenas suas próprias reservas**

#### Como Staff/Admin
```bash
GET /api/v1/bookings/
```
- Retorna **todas as reservas** do sistema

#### Filtrar por Usuário (Staff/Admin)
```bash
GET /api/v1/bookings/?user_id=3
```
- Lista reservas de um usuário específico

#### Filtrar por Status
```bash
GET /api/v1/bookings/?status=confirmed
GET /api/v1/bookings/?status=pending
GET /api/v1/bookings/?status=cancelled
```

### Passo 10: Ver Detalhes da Reserva
```bash
GET /api/v1/bookings/1/
```

### Passo 11: Tentar Fazer Reserva Duplicada (Deve Falhar)
```bash
POST /api/v1/bookings/
{
  "room": 1,
  "data_checkin": "2026-02-16",
  "data_checkout": "2026-02-17",
  "numero_hospedes": 2
}
```
❌ **Deve retornar erro: "Quarto não disponível"**

### Passo 12: Login como Staff/Admin
```bash
POST /api/v1/auth/login/
{
  "email": "admin@example.com",
  "password": "admin123"
}
```

### Passo 13: Confirmar a Reserva
```bash
POST /api/v1/bookings/1/confirm/
```
✅ **Cliente recebe email de confirmação!**

### Passo 14: Fazer Check-in
```bash
POST /api/v1/bookings/1/checkin/
```

### Passo 15: Fazer Check-out
```bash
POST /api/v1/bookings/1/checkout/
```

### Passo 16: Listar Reservas do Hotel
```bash
GET /api/v1/hotels/1/bookings/

# Filtrar por status
GET /api/v1/hotels/1/bookings/?status=confirmed
```

### Passo 17: Cancelar uma Reserva (Cliente)
```bash
# Login como cliente novamente
POST /api/v1/auth/login/
{
  "email": "cliente@example.com",
  "password": "Cliente123!"
}

# Criar nova reserva
POST /api/v1/bookings/
{
  "room": 2,
  "data_checkin": "2026-03-01",
  "data_checkout": "2026-03-05",
  "numero_hospedes": 2
}

# Cancelar
DELETE /api/v1/bookings/2/
```
✅ **Email de cancelamento enviado!**

---

## ⏰ **Testar Celery Beat (Liberação Automática)**

### 1. Criar Reserva com Data Passada (via Django Shell)
```bash
docker compose exec web python manage.py shell
```

```python
from reserveme.models import Booking, Room, User
from datetime import date, timedelta

# Buscar quarto e usuário
room = Room.objects.first()
user = User.objects.filter(role='customer').first()

# Criar reserva com data passada
booking = Booking.objects.create(
    room=room,
    user=user,
    data_checkin=date.today() - timedelta(days=2),
    data_checkout=date.today() - timedelta(days=1),
    numero_hospedes=2,
    numero_diarias=1,
    preco_diaria=room.preco_diaria,
    preco_total=room.preco_diaria,
    status='pending'
)

print(f"Reserva criada: {booking.codigo_reserva}")
```

### 2. Executar Task Manualmente
```bash
docker compose exec celery python manage.py shell
```

```python
from reserveme.tasks import release_expired_bookings_task

result = release_expired_bookings_task()
print(result)
```

### 3. Verificar Logs do Celery Beat
```bash
docker compose logs -f celery-beat
docker compose logs -f celery
```

### 4. Verificar Email no Mailpit
- Acesse: http://localhost:8025
- Deve ter email de "Reserva Expirada"

---

## 📊 **Verificar Status via Django Admin**

1. Acesse: http://localhost:8000/admin/
2. Login: admin@example.com / admin123
3. Navegue por:
   - **Reserveme > Rooms** - Ver todos os quartos
   - **Reserveme > Bookings** - Ver todas as reservas
   - **Reserveme > Users** - Gerenciar usuários

---

## 🐛 **Troubleshooting**

### Erro: "Quarto não disponível"
✅ Verifique se as datas não se sobrepõem com outra reserva ativa

### Email não enviado
✅ Verifique se Celery está rodando:
```bash
docker compose ps
docker compose logs celery
```

### Task não executando
✅ Verifique Celery Beat:
```bash
docker compose logs celery-beat
```

### Erro de permissão
✅ Verifique se está autenticado e com role correto

---

## 📦 **Dados de Teste Rápido**

### Tipos de Quarto Disponíveis:
- `single` - Solteiro
- `double` - Casal
- `twin` - Twin (2 Solteiros)
- `triple` - Triplo
- `suite` - Suíte
- `deluxe` - Suíte Deluxe
- `presidential` - Suíte Presidencial

### Status de Reserva:
- `pending` - Pendente (criada, aguardando confirmação)
- `confirmed` - Confirmada (pelo staff)
- `checked_in` - Check-in realizado
- `checked_out` - Check-out realizado
- `cancelled` - Cancelada

### Roles de Usuário:
- `customer` - Cliente (pode fazer reservas)
- `staff` - Staff (pode gerenciar reservas)
- `admin` - Admin (acesso total)

---

## 🎯 **Validações Implementadas**

✅ Data de check-out > data de check-in
✅ Data de check-in não pode ser no passado
✅ Número de hóspedes ≤ capacidade do quarto
✅ Quarto deve estar disponível (sem reservas ativas sobrepostas)
✅ Preço calculado automaticamente
✅ Código de reserva único gerado automaticamente
✅ Número de quarto único por hotel
✅ Soft delete (is_active) em quartos e hotéis
✅ Permissões por role em cada endpoint

---

## 📧 **Emails Enviados Automaticamente**

1. ✅ **Reserva Criada** - Cliente cria reserva (pending)
2. ✅ **Reserva Confirmada** - Staff confirma reserva
3. ✅ **Reserva Cancelada** - Cliente/Staff cancela
4. ✅ **Reserva Expirada** - Celery Beat cancela automaticamente

---

**Pronto para testar! 🚀**

Explore a API através do Swagger UI: http://localhost:8000/api/docs/
