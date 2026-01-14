# 📮 Postman Collection - ReserveMe API

Collection completa para testar a API ReserveMe com autenticação JWT via cookies HTTP-only.

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

## 📚 Documentação Adicional

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/
- **Mailpit UI**: http://localhost:8025

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

## 🎯 Endpoints Disponíveis

### Authentication
- ✅ `POST /api/v1/auth/register/` - Registro
- ✅ `POST /api/v1/auth/verify-email/` - Verificação de email
- ✅ `POST /api/v1/auth/login/` - Login
- ✅ `POST /api/v1/auth/logout/` - Logout
- ✅ `POST /api/v1/auth/refresh/` - Refresh token
- ✅ `GET /api/v1/auth/me/` - Ver perfil
- ✅ `PATCH /api/v1/auth/me/` - Atualizar perfil
- ✅ `POST /api/v1/auth/change-password/` - Mudar senha

---

**Collection pronta para uso!** 🚀

Importe no Postman e comece a testar a API.
