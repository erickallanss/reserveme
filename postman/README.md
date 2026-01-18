# 📮 Postman Collection - ReserveMe API

Collection completa para testar a API ReserveMe com autenticação JWT via cookies HTTP-only, gerenciamento de hotéis e mais.

## 📁 Arquivos

- `ReserveMe_API.postman_collection.json` - Collection principal
- `ReserveMe_Local.postman_environment.json` - Environment para desenvolvimento local

## 🚀 Como Usar

### 1. Importar no Postman

1. Abra o Postman
2. Clique em **Import**
3. Selecione os dois arquivos JSON
4. Collection e Environment serão importados

### 2. Configurar Environment

1. No canto superior direito, selecione **"ReserveMe - Local"**
2. As variáveis serão preenchidas automaticamente durante os testes

### 3. Executar Fluxo Completo

#### Passo 1: Registrar Usuário
```
POST /api/v1/auth/register/
```
- Dados gerados automaticamente com Faker
- Email de verificação será enviado (ver Mailpit)
- `user_email` e `user_id` salvos automaticamente

#### Passo 2: Verificar Email
```
POST /api/v1/auth/verify-email/
```
- Copie o token do email no Mailpit (http://localhost:8025)
- Cole na variável `verification_token` do environment
- Ou edite o body do request

#### Passo 3: Aprovar Usuário (via Django Admin)
1. Acesse: http://localhost:8000/admin/
2. Crie um superuser se necessário:
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```
3. Login no admin
4. Vá em **Users** → encontre o usuário
5. Marque **Is approved** ✅
6. Salve

#### Passo 4: Fazer Login
```
POST /api/v1/auth/login/
```
- Use o email registrado
- Senha padrão: `TestPass123!@#`
- Cookies serão salvos automaticamente pelo Postman
- Tokens disponíveis nas variáveis de ambiente

#### Passo 5: Testar Endpoints Autenticados
- `GET /api/v1/auth/me/` - Ver perfil
- `PATCH /api/v1/auth/me/` - Atualizar perfil
- `POST /api/v1/auth/change-password/` - Mudar senha

#### Passo 6: Refresh Token
```
POST /api/v1/auth/refresh/
```
- Renova o access token automaticamente
- Usa o refresh token do cookie

#### Passo 7: Logout
```
POST /api/v1/auth/logout/
```
- Remove cookies
- Limpa variáveis de ambiente

### 4. Testar Endpoints de Hotéis

#### Listar Hotéis (Público)
```
GET /api/v1/hotels/
```
- Não requer autenticação
- Retorna apenas hotéis ativos para não-admins
- Retorna todos os hotéis para admins

#### Criar Hotel (Admin)
```
POST /api/v1/hotels/
```
- Requer autenticação de admin
- `hotel_id` salvo automaticamente
- Campos obrigatórios: nome, endereco, telefone, email, horario_checkin, horario_checkout
- Campos opcionais: descricao, logo (upload de imagem)
- **Nota**: Para upload de logo, use `form-data` ao invés de `raw JSON`

#### Ver Detalhes do Hotel
```
GET /api/v1/hotels/{hotel_id}/
```
- Público para hotéis ativos
- Admins podem ver hotéis inativos

#### Atualizar Hotel (Admin)
```
PUT /api/v1/hotels/{hotel_id}/    # Atualização completa
PATCH /api/v1/hotels/{hotel_id}/  # Atualização parcial
```
- Requer autenticação de admin
- PUT: todos os campos obrigatórios
- PATCH: apenas campos que deseja atualizar

#### Desativar Hotel (Admin)
```
DELETE /api/v1/hotels/{hotel_id}/
```
- Requer autenticação de admin
- Soft delete: hotel marcado como inativo
- Não remove do banco de dados

## 🔒 Autenticação via Cookies

### Como Funciona

Os tokens JWT são armazenados em **cookies HTTP-only**:
- ✅ **Seguro contra XSS** - JavaScript não pode acessar
- ✅ **Enviados automaticamente** - Postman gerencia cookies
- ✅ **SameSite protection** - Proteção CSRF

### Cookies Configurados

| Cookie | Lifetime | HttpOnly | Secure | SameSite |
|--------|----------|----------|--------|----------|
| `access_token` | 1 hora | ✅ | Dev: ❌ Prod: ✅ | Lax |
| `refresh_token` | 7 dias | ✅ | Dev: ❌ Prod: ✅ | Lax |

### Ver Cookies no Postman

1. Clique no ícone de **Cookies** (🍪) abaixo do botão Send
2. Selecione o domínio `localhost:8000`
3. Veja os cookies `access_token` e `refresh_token`

## 🧪 Testes Automatizados

Cada request tem testes automáticos que:
- ✅ Verificam status code
- ✅ Validam estrutura da resposta
- ✅ Salvam tokens e IDs automaticamente
- ✅ Gerenciam cookies

### Executar Todos os Testes

1. Clique na Collection **"ReserveMe API"**
2. Clique em **"Run"**
3. Selecione os requests
4. Clique em **"Run ReserveMe API"**

**Nota**: Alguns testes dependem de execução manual (aprovação de usuário)

## 📊 Variáveis de Environment

| Variável | Descrição | Auto-preenchida |
|----------|-----------|-----------------|
| `base_url` | URL base da API | Manual |
| `user_email` | Email do usuário registrado | ✅ Auto |
| `user_id` | ID do usuário | ✅ Auto |
| `access_token` | JWT access token | ✅ Auto |
| `refresh_token` | JWT refresh token | ✅ Auto |
| `verification_token` | Token de verificação de email | Manual |
| `hotel_id` | ID do hotel criado | ✅ Auto |

## 🔄 Fluxo de Autenticação

```
┌─────────────┐
│  Register   │ → Email enviado → Mailpit
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Verify Email│ → Token do email
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Admin Approves│ → Django Admin
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Login    │ → Cookies salvos ✅
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Use API     │ → Cookies automáticos
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Logout    │ → Cookies removidos
└─────────────┘
```

## 🛠️ Troubleshooting

### Cookies não funcionam
- ✅ Certifique-se que está usando **Postman Desktop App** (não web)
- ✅ Verifique se o domínio é `localhost:8000`
- ✅ Clique no ícone 🍪 para ver se os cookies estão salvos

### 401 Unauthorized
- ✅ Faça login novamente
- ✅ Verifique se os cookies estão presentes
- ✅ Token pode ter expirado (1 hora)

### Email não verificado / Não aprovado
- ✅ Verifique o email no Mailpit: http://localhost:8025
- ✅ Aprove o usuário no admin: http://localhost:8000/admin/

### 429 Too Many Requests
- ✅ Rate limiting ativado
- ✅ Aguarde alguns minutos
- ✅ Limites: Login (5/15min), Register (3/hour)

### 403 Forbidden (Endpoints Admin)
- ✅ Endpoint requer permissão de admin
- ✅ Crie um admin via Django admin ou use `POST /api/v1/internal/register/`
- ✅ Faça login com uma conta admin

### Como Criar um Admin
**Opção 1 - Via Django Shell:**
```bash
docker compose exec web python manage.py createsuperuser
```

**Opção 2 - Via Django Admin:**
1. Acesse: http://localhost:8000/admin/
2. Faça login com superuser
3. Vá em Users → seu usuário
4. Altere role para "admin"
5. Salve

**Opção 3 - Via Internal Register (se já é admin):**
Use o endpoint `POST /api/v1/internal/register/` autenticado como admin

## 📚 Documentação Adicional

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/
- **Mailpit UI**: http://localhost:8025

## 📝 Formatos de Dados

### Telefone
- Formato: `(99) 99999-9999` ou `(99) 9999-9999`
- Exemplo: `(11) 98765-4321`

### CPF
- Formato: `999.999.999-99` ou `99999999999`
- API aceita ambos, mas valida o CPF
- Exemplo: `123.456.789-00`

### Horários (Check-in/Check-out)
- Formato: `HH:MM:SS`
- Exemplo: `14:00:00` (2 PM)

### Data de Nascimento
- Formato: `YYYY-MM-DD`
- Exemplo: `1990-01-15`

## 💡 Dicas

### Gerar Dados Aleatórios

O Postman tem variáveis dinâmicas:
- `{{$randomEmail}}` - Email aleatório
- `{{$randomUserName}}` - Username aleatório
- `{{$randomFirstName}}` - Nome aleatório
- `{{$randomLastName}}` - Sobrenome aleatório
- `{{$randomPassword}}` - Senha aleatória

### Duplicar Usuário para Testes

Para criar múltiplos usuários:
1. Duplique o request "Register User"
2. Execute várias vezes
3. Cada execução cria um usuário diferente

### Testar Rate Limiting

Execute o mesmo request 10x seguidas para ver o rate limiting em ação.

### Testar Permissões de Admin

1. Crie um usuário normal via `POST /api/v1/auth/register/`
2. Tente criar um hotel com usuário comum → 403 Forbidden
3. Faça login com admin
4. Tente criar um hotel → Sucesso!

## 🏨 Fluxos Completos

### Fluxo 1: Usuário Cliente Visualiza Hotéis
```
1. GET /api/v1/hotels/ (sem autenticação)
2. GET /api/v1/hotels/{id}/ (sem autenticação)
```

### Fluxo 2: Admin Gerencia Hotéis
```
1. POST /api/v1/internal/register/ → Criar admin
2. POST /api/v1/auth/login/ → Login admin
3. POST /api/v1/hotels/ → Criar hotel
4. GET /api/v1/hotels/ → Listar todos (incluindo inativos)
5. PATCH /api/v1/hotels/{id}/ → Atualizar parcialmente
6. DELETE /api/v1/hotels/{id}/ → Desativar hotel
```

### Fluxo 3: Autenticação Completa
```
1. POST /api/v1/auth/register/
2. POST /api/v1/auth/verify-email/
3. Django Admin → Aprovar usuário
4. POST /api/v1/auth/login/
5. GET /api/v1/auth/me/
6. PATCH /api/v1/auth/me/
7. POST /api/v1/auth/change-password/
8. POST /api/v1/auth/refresh/
9. POST /api/v1/auth/logout/
```

## 🎯 Endpoints Disponíveis

### 🔐 Authentication
- ✅ `POST /api/v1/auth/register/` - Registro de cliente
- ✅ `POST /api/v1/auth/verify-email/` - Verificação de email
- ✅ `POST /api/v1/auth/login/` - Login
- ✅ `POST /api/v1/auth/logout/` - Logout
- ✅ `POST /api/v1/auth/refresh/` - Refresh token
- ✅ `GET /api/v1/auth/me/` - Ver perfil
- ✅ `PATCH /api/v1/auth/me/` - Atualizar perfil
- ✅ `POST /api/v1/auth/change-password/` - Mudar senha

### 🔒 Internal Management (Apenas Admin)
- ✅ `POST /api/v1/internal/register/` - Registrar usuário interno (admin/staff)

### 🏨 Hotels
- ✅ `GET /api/v1/hotels/` - Listar hotéis (público para ativos)
- ✅ `POST /api/v1/hotels/` - Criar hotel (🔒 admin)
- ✅ `GET /api/v1/hotels/{id}/` - Detalhes do hotel (público para ativos)
- ✅ `PUT /api/v1/hotels/{id}/` - Atualizar hotel completo (🔒 admin)
- ✅ `PATCH /api/v1/hotels/{id}/` - Atualizar hotel parcial (🔒 admin)
- ✅ `DELETE /api/v1/hotels/{id}/` - Desativar hotel (🔒 admin)

### 🛏️ Rooms ⭐ NOVO
- ✅ `GET /api/v1/rooms/` - Listar quartos (público para ativos)
- ✅ `POST /api/v1/rooms/` - Criar quarto (🔒 staff/admin)
- ✅ `GET /api/v1/rooms/{id}/` - Detalhes do quarto (público para ativos)
- ✅ `PUT /api/v1/rooms/{id}/` - Atualizar quarto completo (🔒 staff/admin)
- ✅ `PATCH /api/v1/rooms/{id}/` - Atualizar quarto parcial (🔒 staff/admin)
- ✅ `DELETE /api/v1/rooms/{id}/` - Desativar quarto (🔒 staff/admin)

### 📅 Bookings ⭐ NOVO
- ✅ `GET /api/v1/bookings/` - Listar minhas reservas (🔒 autenticado)
- ✅ `POST /api/v1/bookings/` - Criar reserva (🔒 autenticado)
- ✅ `GET /api/v1/bookings/{id}/` - Detalhes da reserva (🔒 dono ou staff)
- ✅ `DELETE /api/v1/bookings/{id}/` - Cancelar reserva (🔒 dono ou staff)
- ✅ `POST /api/v1/bookings/{id}/confirm/` - Confirmar reserva (🔒 staff/admin)
- ✅ `POST /api/v1/bookings/{id}/checkin/` - Check-in (🔒 staff/admin)
- ✅ `POST /api/v1/bookings/{id}/checkout/` - Check-out (🔒 staff/admin)
- ✅ `GET /api/v1/hotels/{id}/bookings/` - Reservas do hotel (🔒 staff/admin)

### 📚 API Documentation
- ✅ `GET /api/schema/` - OpenAPI Schema
- ✅ `GET /api/docs/` - Swagger UI
- ✅ `GET /api/redoc/` - ReDoc

**Total**: 26 endpoints

---

**Collection pronta para uso!** 🚀

Importe no Postman e comece a testar a API.
