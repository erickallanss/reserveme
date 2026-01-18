# 🌱 Script de Seed - Popular Banco de Dados

## 📝 Descrição

Script para popular o banco de dados com dados de teste prontos para uso.

## 🎯 O que é criado

### 👥 **Usuários (6 total)**

#### 1. Admin
- **Email**: `admin@reserveme.com`
- **Senha**: `admin123`
- **Role**: Admin (acesso total)

#### 2. Staff
- **Email**: `staff@reserveme.com`
- **Senha**: `staff123`
- **Role**: Staff (gerencia reservas)

#### 3-6. Clientes (4)
| Nome | Email | Senha | CPF |
|------|-------|-------|-----|
| João Silva | joao.silva@example.com | cliente123 | 12345678901 |
| Maria Santos | maria.santos@example.com | cliente123 | 23456789012 |
| Pedro Oliveira | pedro.oliveira@example.com | cliente123 | 34567890123 |
| Ana Costa | ana.costa@example.com | cliente123 | 45678901234 |

---

### 🏨 **Hotel (1)**

**Hotel Paradise Beach**
- 📍 Av. Atlântica, 1500 - Copacabana, Rio de Janeiro
- ☎️ (21) 3500-8000
- 📧 contato@paradisebeach.com.br
- ⏰ Check-in: 14:00 | Check-out: 12:00

---

### 🛏️ **Quartos (8)**

| Nº | Tipo | Capacidade | Preço/Dia | Comodidades |
|----|------|------------|-----------|-------------|
| 101 | Solteiro | 1 | R$ 150 | Básico |
| 102 | Casal | 2 | R$ 250 | + Varanda |
| 103 | Twin | 2 | R$ 240 | Básico |
| 201 | Casal Superior | 2 | R$ 300 | + Varanda |
| 202 | Triplo | 3 | R$ 350 | + Varanda |
| 301 | Suíte | 2 | R$ 500 | + Varanda + Banheira |
| 302 | Suíte Deluxe | 3 | R$ 750 | + Varanda + Banheira |
| 401 | Presidencial | 4 | R$ 1500 | + Varanda + Banheira |

**Comodidades padrão em todos**: Ar condicionado, Wi-Fi, TV, Frigobar

---

### 📅 **Reservas (7)**

| Código | Quarto | Cliente | Check-in | Check-out | Status | Diárias | Total |
|--------|--------|---------|----------|-----------|--------|---------|-------|
| RES-xxx-001 | 102 | João | Hoje +5d | Hoje +8d | ✅ Confirmada | 3 | R$ 750 |
| RES-xxx-002 | 301 | Maria | Hoje +10d | Hoje +15d | ✅ Confirmada | 5 | R$ 2.500 |
| RES-xxx-003 | 202 | Pedro | Hoje +7d | Hoje +10d | ⏳ Pendente | 3 | R$ 1.050 |
| RES-xxx-004 | 101 | Ana | Hoje -1d | Hoje +2d | 🔑 Check-in | 3 | R$ 450 |
| RES-xxx-005 | 201 | João | Hoje -10d | Hoje -7d | ✅ Concluída | 3 | R$ 900 |
| RES-xxx-006 | 302 | Maria | Hoje +20d | Hoje +25d | ⏳ Pendente | 5 | R$ 3.750 |
| RES-xxx-007 | 103 | Pedro | Hoje +15d | Hoje +18d | ✅ Confirmada | 3 | R$ 720 |

**Total de reservas**: R$ 10.120,00

---

## 🚀 Como Usar

### Opção 1: Docker (Recomendado)
```bash
docker compose exec web python seed_data.py
```

### Opção 2: Local
```bash
python seed_data.py
```

---

## ✅ Verificar Dados Criados

### 1. Via Django Admin
```
URL: http://localhost:8000/admin/
Login: admin@reserveme.com / admin123

Navegue por:
- Reserveme > Users (6 usuários)
- Reserveme > Hotels (1 hotel)
- Reserveme > Rooms (8 quartos)
- Reserveme > Bookings (7 reservas)
```

### 2. Via API (Swagger)
```
URL: http://localhost:8000/api/docs/

Endpoints para testar:
- GET /api/v1/hotels/ - Ver o hotel
- GET /api/v1/rooms/ - Ver os 8 quartos
- POST /api/v1/auth/login/ - Login como admin
- GET /api/v1/bookings/ - Ver suas reservas
```

### 3. Via Postman
```
1. Importe a collection atualizada
2. Selecione environment "ReserveMe - Local"
3. Login como admin:
   POST /api/v1/auth/login/
   {
     "email": "admin@reserveme.com",
     "password": "admin123"
   }
4. Liste os quartos:
   GET /api/v1/rooms/
5. Crie uma nova reserva:
   POST /api/v1/bookings/
```

---

## 📊 Cenários de Teste Cobertos

### ✅ Reservas Confirmadas (Futuras)
- Cliente pode visualizar
- Staff pode fazer check-in no dia

### ⏳ Reservas Pendentes
- Aguardando confirmação do staff
- Staff pode confirmar ou cancelar

### 🔑 Check-in Realizado
- Hóspede no hotel
- Staff pode fazer check-out

### ✅ Reservas Concluídas
- Histórico do cliente
- Já foi checkout

---

## 🎭 Perfis para Testar

### Como Admin
```bash
# Login
POST /api/v1/auth/login/
{
  "email": "admin@reserveme.com",
  "password": "admin123"
}

# Pode fazer:
- Criar/editar hotéis
- Criar/editar quartos
- Ver todas as reservas
- Confirmar reservas
- Check-in/out
```

### Como Staff
```bash
# Login
POST /api/v1/auth/login/
{
  "email": "staff@reserveme.com",
  "password": "staff123"
}

# Pode fazer:
- Criar/editar quartos
- Ver todas as reservas
- Confirmar reservas
- Check-in/out
```

### Como Cliente
```bash
# Login
POST /api/v1/auth/login/
{
  "email": "joao.silva@example.com",
  "password": "cliente123"
}

# Pode fazer:
- Ver hotéis e quartos
- Criar reservas
- Ver suas próprias reservas
- Cancelar suas reservas (pending/confirmed)
```

---

## 🧪 Testes Sugeridos

### 1. Criar Reserva Válida
```bash
POST /api/v1/bookings/
{
  "room": 1,
  "data_checkin": "2026-03-01",
  "data_checkout": "2026-03-05",
  "numero_hospedes": 2
}
```

### 2. Tentar Reserva Duplicada (deve falhar)
```bash
# Usar as mesmas datas de uma reserva ativa existente
POST /api/v1/bookings/
{
  "room": 2,  # Quarto 102
  "data_checkin": "Hoje +6d",  # Sobrepõe com reserva de João
  "data_checkout": "Hoje +7d",
  "numero_hospedes": 2
}
# Resposta: 400 - "Quarto não disponível"
```

### 3. Confirmar Reserva (como staff)
```bash
POST /api/v1/bookings/3/confirm/
# Reserva 3 (Pedro) muda de pending → confirmed
# Email enviado ao cliente
```

### 4. Cancelar Reserva (como cliente)
```bash
# Login como maria.santos@example.com
DELETE /api/v1/bookings/6/
# Reserva 6 cancelada
# Email enviado
```

---

## 🔄 Executar Novamente

O script é **idempotente**:
- Se os dados já existem, ele pula e não duplica
- Pode executar múltiplas vezes sem problemas

Para **limpar e recriar** do zero:
```bash
# Resetar banco (CUIDADO: apaga tudo!)
docker compose exec web python manage.py flush --no-input

# Popular novamente
docker compose exec web python seed_data.py
```

---

## 📧 Emails

Todos os emails são capturados pelo Mailpit:
- **URL**: http://localhost:8025
- Reservas criadas no seed não enviam email (criadas diretamente no banco)
- Para testar emails, crie novas reservas via API

---

## 💡 Dicas

1. **Explorar no Admin** - Veja todos os dados criados visualmente
2. **Testar Workflow** - pending → confirmed → checked_in → checked_out
3. **Testar Permissões** - Tente acessar endpoints com diferentes usuários
4. **Verificar Disponibilidade** - Tente criar reservas em datas ocupadas
5. **Celery Beat** - Aguarde 1 hora ou execute manualmente para ver cancelamento automático

---

**Dados prontos para começar a testar! 🎉**
