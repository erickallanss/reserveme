# Email Utilities - Guia Completo

## Visão Geral

Este módulo fornece utilities para envio de emails **assíncronos** usando Celery, integrado com Mailpit para desenvolvimento.

## Arquitetura

```
┌─────────────┐
│   View/     │
│  Service    │
└──────┬──────┘
       │ send_email_async()
       ▼
┌─────────────┐
│   Helper    │ ← Interface simples
└──────┬──────┘
       │ .delay()
       ▼
┌─────────────┐
│ Celery Task │ ← Task assíncrona
└──────┬──────┘
       │ send_mail()
       ▼
┌─────────────┐
│   Django    │
│    Mail     │
└──────┬──────┘
       │ SMTP
       ▼
┌─────────────┐
│   Mailpit   │ ← Captura emails
│  (Dev only) │   localhost:8025
└─────────────┘
```

## Configuração Automática

### Desenvolvimento (Docker Compose)
✅ **Mailpit já configurado!**
- **SMTP**: `mailpit:1025` (interno aos containers)
- **Web UI**: http://localhost:8025
- Emails são capturados automaticamente
- Não envia emails reais

### Produção (.env)
Configure variáveis de ambiente:
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
DEFAULT_FROM_EMAIL=noreply@seudominio.com
```

## Uso Básico

### 1. Email Simples (Texto)

```python
from core.utils.helpers import send_email_async

# Enviar email assíncrono
result = send_email_async(
    subject='Bem-vindo ao ReserveMe!',
    message='Obrigado por se cadastrar.',
    recipient_list=['user@example.com']
)

# Opcional: Verificar status
print(f"Task ID: {result.id}")
print(f"Completou: {result.ready()}")
```

### 2. Email com HTML

```python
from core.utils.helpers import send_email_async

html_content = """
<html>
    <body>
        <h1>Bem-vindo!</h1>
        <p>Obrigado por se cadastrar no <strong>ReserveMe</strong>.</p>
    </body>
</html>
"""

result = send_email_async(
    subject='Bem-vindo!',
    message='Obrigado por se cadastrar.',  # Fallback texto
    recipient_list=['user@example.com'],
    html_message=html_content
)
```

### 3. Email com Template Django

```python
from core.utils.helpers import send_template_email_async

result = send_template_email_async(
    subject='Confirmação de Reserva',
    template_name='emails/reservation_confirmation.html',
    context={
        'user_name': 'João Silva',
        'reservation_id': 12345,
        'date': '2024-01-20',
        'time': '14:00',
    },
    recipient_list=['user@example.com']
)
```

### 4. Múltiplos Emails Diferentes

```python
from core.utils.helpers import send_mass_email_async

emails = [
    ('Welcome', 'Welcome message', 'from@example.com', ['user1@example.com']),
    ('Reminder', 'Reminder message', 'from@example.com', ['user2@example.com']),
    ('Confirmation', 'Confirmation message', 'from@example.com', ['user3@example.com']),
]

result = send_mass_email_async(emails)
```

## Uso em Services

### Exemplo: Service de Autenticação

```python
# reserveme/services/auth_service.py
from core.utils.helpers import send_template_email_async
from django.contrib.auth.models import User

class AuthService:
    def register_user(self, email: str, username: str, password: str) -> User:
        # Criar usuário
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Enviar email de boas-vindas (assíncrono)
        send_template_email_async(
            subject='Bem-vindo ao ReserveMe!',
            template_name='emails/welcome.html',
            context={
                'user_name': user.username,
                'activation_link': f'https://app.com/activate/{user.id}',
            },
            recipient_list=[user.email]
        )
        
        return user
```

### Exemplo: Service de Reserva

```python
# reserveme/services/reservation_service.py
from core.utils.helpers import send_template_email_async

class ReservationService:
    def create_reservation(self, user, data):
        # Criar reserva
        reservation = self.repository.create(**data)
        
        # Notificar usuário (assíncrono)
        send_template_email_async(
            subject=f'Reserva #{reservation.id} Confirmada',
            template_name='emails/reservation_confirmed.html',
            context={
                'user_name': user.first_name,
                'reservation': reservation,
                'cancel_link': f'https://app.com/cancel/{reservation.id}',
            },
            recipient_list=[user.email]
        )
        
        # Notificar admin
        send_template_email_async(
            subject=f'Nova Reserva: {user.username}',
            template_name='emails/admin_new_reservation.html',
            context={'reservation': reservation},
            recipient_list=['admin@reserveme.com']
        )
        
        return reservation
```

## Templates de Email

### Estrutura de Diretórios

```
reserveme/
└── templates/
    └── emails/
        ├── base.html              # Template base
        ├── welcome.html           # Boas-vindas
        ├── welcome.txt            # Versão texto
        ├── reservation_confirmed.html
        ├── reservation_confirmed.txt
        └── password_reset.html
```

### Template Base (base.html)

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; }
        .header { background: #007bff; color: white; padding: 20px; }
        .content { padding: 20px; }
        .footer { background: #f4f4f4; padding: 10px; text-align: center; }
    </style>
</head>
<body>
    <div class="header">
        <h1>ReserveMe</h1>
    </div>
    <div class="content">
        {% block content %}{% endblock %}
    </div>
    <div class="footer">
        <p>&copy; 2024 ReserveMe. Todos os direitos reservados.</p>
    </div>
</body>
</html>
```

### Template Welcome (welcome.html)

```html
{% extends "emails/base.html" %}

{% block content %}
    <h2>Bem-vindo, {{ user_name }}!</h2>
    <p>Obrigado por se cadastrar no ReserveMe.</p>
    <p>
        <a href="{{ activation_link }}" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none;">
            Ativar Conta
        </a>
    </p>
{% endblock %}
```

### Versão Texto (welcome.txt)

```
Bem-vindo, {{ user_name }}!

Obrigado por se cadastrar no ReserveMe.

Ative sua conta acessando: {{ activation_link }}

---
ReserveMe - Sistema de Reservas
```

## Monitoramento com Mailpit

### Acessar Interface Web
http://localhost:8025

### Recursos do Mailpit:
- 📧 **Visualizar todos os emails** enviados
- 🔍 **Buscar emails** por destinatário, assunto, etc.
- 📱 **Preview responsivo** (desktop/mobile)
- 🐛 **Debug headers** SMTP completos
- 📎 **Visualizar anexos**
- 🔄 **API REST** para automação

### API do Mailpit

```python
import requests

# Listar emails
response = requests.get('http://localhost:8025/api/v1/messages')
emails = response.json()

# Buscar email específico
email_id = emails['messages'][0]['ID']
email = requests.get(f'http://localhost:8025/api/v1/message/{email_id}')

# Deletar todos
requests.delete('http://localhost:8025/api/v1/messages')
```

## Tratamento de Erros

### Retry Automático
Tasks têm **3 tentativas** com backoff exponencial:
- 1ª tentativa: imediato
- 2ª tentativa: após 30s
- 3ª tentativa: após 60s
- 4ª tentativa: após 120s

### Capturar Erros

```python
from celery.exceptions import Retry

result = send_email_async(
    subject='Test',
    message='Test message',
    recipient_list=['user@example.com']
)

try:
    # Esperar resultado (bloqueia!)
    emails_sent = result.get(timeout=10)
    print(f"Emails enviados: {emails_sent}")
except Retry:
    print("Task será tentada novamente")
except Exception as e:
    print(f"Erro: {e}")
```

### Fail Silently

```python
# Não levanta exceção se falhar
send_email_async(
    subject='Test',
    message='Test',
    recipient_list=['invalid-email'],
    fail_silently=True  # Não quebra a aplicação
)
```

## Email Síncrono (Não Recomendado)

```python
from core.utils.helpers import send_email_sync

# Bloqueia até completar!
emails_sent = send_email_sync(
    subject='Urgent',
    message='Urgent message',
    recipient_list=['admin@example.com']
)
```

⚠️ **Use apenas quando absolutamente necessário** (ex: fluxo crítico que precisa do resultado imediato).

## Testing

### Mock de Email em Testes

```python
# conftest.py
import pytest
from unittest.mock import patch

@pytest.fixture
def mock_send_email():
    with patch('core.utils.tasks.send_email_task.delay') as mock:
        mock.return_value.id = 'test-task-id'
        yield mock

# test_service.py
def test_user_registration_sends_email(mock_send_email):
    service = AuthService()
    user = service.register_user('test@example.com', 'testuser', 'password')
    
    # Verificar que email foi agendado
    mock_send_email.assert_called_once()
    args, kwargs = mock_send_email.call_args
    assert kwargs['subject'] == 'Bem-vindo ao ReserveMe!'
    assert 'test@example.com' in kwargs['recipient_list']
```

### Testar Task Diretamente

```python
from core.utils.tasks import send_email_task

def test_send_email_task():
    result = send_email_task.apply(kwargs={
        'subject': 'Test',
        'message': 'Test message',
        'recipient_list': ['test@example.com']
    })
    
    assert result.successful()
    assert result.result == 1  # 1 email enviado
```

## Comandos Úteis

```bash
# Ver emails no Mailpit
open http://localhost:8025

# Ver logs do Celery
docker compose logs -f celery

# Limpar fila do Celery
docker compose exec celery celery -A core purge

# Ver tasks ativas
docker compose exec celery celery -A core inspect active

# Ver tasks agendadas
docker compose exec celery celery -A core inspect scheduled

# Reiniciar Celery (após mudanças no código)
docker compose restart celery celery-beat
```

## Best Practices

### ✅ DO

1. **Use helpers**, não tasks diretamente
2. **Sempre assíncrono** em produção
3. **Templates para emails** recorrentes
4. **Context mínimo** nos templates
5. **Teste no Mailpit** antes de produção

### ❌ DON'T

1. **Não use sync** sem necessidade
2. **Não envie dados sensíveis** em emails
3. **Não sobrecarregue** a fila com emails massivos
4. **Não ignore erros** em emails críticos
5. **Não hardcode** emails no código

## Troubleshooting

### Email não aparece no Mailpit
```bash
# Verificar se Mailpit está rodando
docker compose ps mailpit

# Ver logs do Celery
docker compose logs celery --tail 50

# Verificar configuração
docker compose exec web python manage.py shell
>>> from django.conf import settings
>>> print(settings.EMAIL_HOST, settings.EMAIL_PORT)
```

### Task não executa
```bash
# Verificar worker
docker compose exec celery celery -A core inspect active

# Verificar broker
docker compose exec celery celery -A core inspect ping
```

### Mailpit não abre
```bash
# Verificar porta
curl http://localhost:8025

# Ver logs
docker compose logs mailpit
```

## Produção

### Configurar SMTP Real

```bash
# .env (produção)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.xxx
DEFAULT_FROM_EMAIL=noreply@seudominio.com
```

### Providers Recomendados
- **SendGrid**: 100 emails/dia grátis
- **Mailgun**: 5000 emails/mês grátis (primeiros 3 meses)
- **Amazon SES**: $0.10 por 1000 emails
- **Postmark**: Templates avançados

---

**Email utilities configuradas e prontas para uso!** 📧
