# 📝 TODO - ReserveMe

## 🔴 URGENTE - Core do Sistema

### 1. Modelo Room (Quarto)
- [ ] Criar model `Room` em `reserveme/models.py`
- [ ] Criar migration
- [ ] Criar `RoomRepository`
- [ ] Criar `RoomService`
- [ ] Criar serializers (RoomSerializer, RoomCreateSerializer, RoomUpdateSerializer)
- [ ] Criar views (RoomListCreateAPIView, RoomDetailAPIView)
- [ ] Adicionar URLs
- [ ] Criar factories para testes
- [ ] Escrever testes unitários
- [ ] Escrever testes de integração

### 2. Modelo Booking (Reserva)
- [ ] Criar model `Booking` em `reserveme/models.py`
- [ ] Criar migration
- [ ] Criar `BookingRepository` com métodos:
  - [ ] `check_room_availability(room_id, checkin, checkout)`
  - [ ] `get_user_bookings(user_id)`
  - [ ] `get_bookings_to_release()`
- [ ] Criar `BookingService` com métodos:
  - [ ] `create_booking()` - validar disponibilidade
  - [ ] `confirm_booking()`
  - [ ] `cancel_booking()`
  - [ ] `checkin()`
  - [ ] `checkout()`
  - [ ] `calculate_total_price()`
- [ ] Criar serializers
- [ ] Criar views:
  - [ ] `BookingListCreateAPIView`
  - [ ] `BookingDetailAPIView`
  - [ ] `MyBookingsAPIView`
- [ ] Adicionar URLs
- [ ] Criar factories para testes
- [ ] Escrever testes

### 3. Email de Confirmação de Reserva
- [ ] Criar template `emails/booking_confirmation.html`
- [ ] Criar template `emails/booking_confirmation.txt`
- [ ] Criar template `emails/booking_cancellation.html`
- [ ] Criar task `send_booking_confirmation_email_task()`
- [ ] Integrar no BookingService

### 4. Tarefa Agendada Celery Beat
- [ ] Criar arquivo `reserveme/tasks.py`
- [ ] Implementar `release_expired_bookings_task()`
- [ ] Configurar schedule no `core/celery.py`
- [ ] Testar task manualmente
- [ ] Escrever testes

---

## 🟡 MELHORIAS

### API
- [ ] Adicionar filtros de busca (django-filter)
- [ ] Adicionar paginação
- [ ] Buscar quartos disponíveis por data
- [ ] Relatórios e estatísticas

### Postman
- [ ] Atualizar collection com endpoints de Room
- [ ] Atualizar collection com endpoints de Booking
- [ ] Adicionar testes automatizados
- [ ] Atualizar README

### Documentação
- [ ] Atualizar ARCHITECTURE.md
- [ ] Criar diagramas ER
- [ ] Documentar regras de negócio
- [ ] Atualizar README principal

---

## ✅ CONCLUÍDO

- ✅ Dockerização completa
- ✅ Autenticação JWT com cookies
- ✅ 3 níveis de permissão (admin/staff/customer)
- ✅ Email assíncrono com Celery
- ✅ Celery Beat rodando
- ✅ Modelo User completo
- ✅ Modelo Hotel completo
- ✅ API de Hotels (CRUD)
- ✅ Postman collection básica
- ✅ Testes unitários e integração
- ✅ Repository + Service pattern
