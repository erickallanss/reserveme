# 📧 Email Setup - Quick Guide

## ✅ Configuração Completa!

Email assíncrono via **Celery** + **Mailpit** configurado e funcionando.

## 🚀 Uso Rápido

### 1. Enviar Email Simples

```python
from core.utils.helpers import send_email_async

send_email_async(
    subject='Bem-vindo!',
    message='Obrigado por se cadastrar.',
    recipient_list=['user@example.com']
)
```

### 2. Email com HTML

```python
send_email_async(
    subject='Confirmação de Reserva',
    message='Sua reserva foi confirmada.',
    recipient_list=['user@example.com'],
    html_message='<h1>Confirmado!</h1><p>Reserva <strong>#12345</strong></p>'
)
```

### 3. Email com Template

```python
send_template_email_async(
    subject='Recuperação de Senha',
    template_name='emails/password_reset.html',
    context={
        'user_name': 'João',
        'reset_link': 'https://app.com/reset/token123'
    },
    recipient_list=['user@example.com']
)
```

## 📬 Mailpit - Interface Web

### Acessar emails capturados:
**http://localhost:8025**

### Recursos:
- ✅ Ver todos os emails enviados
- ✅ Preview HTML/Texto
- ✅ Headers completos
- ✅ Busca e filtros
- ✅ API REST

## 🧪 Testar Agora

```bash
# No terminal do projeto
docker compose exec web python manage.py shell

# No shell Python:
from core.utils.helpers import send_email_async

send_email_async(
    subject='Teste ReserveMe',
    message='Email de teste!',
    recipient_list=['test@example.com'],
    html_message='<h1>Funcionou!</h1>'
)

# Abra: http://localhost:8025
```

## 📊 Status dos Serviços

```bash
# Ver containers
docker compose ps

# Ver emails no Mailpit
open http://localhost:8025

# Ver logs do Celery
docker compose logs -f celery

# Ver tasks executando
docker compose exec celery celery -A core inspect active
```

## 🏗️ Arquitetura

```
View/Service
    ↓
send_email_async()
    ↓
Celery Task (async)
    ↓
Mailpit (captura)
    ↓
http://localhost:8025 (visualizar)
```

## ⚙️ Configuração Atual

### Desenvolvimento (Docker)
- **Backend**: SMTP
- **Host**: mailpit (container)
- **Port**: 1025
- **TLS**: Desabilitado
- **Emails**: Capturados no Mailpit

### Produção (usar .env)
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.xxx
DEFAULT_FROM_EMAIL=noreply@seudominio.com
```

## 📚 Documentação Completa

Ver: `core/utils/README.md`

## ✨ Features

- ✅ **Envio assíncrono** via Celery
- ✅ **Retry automático** (3 tentativas)
- ✅ **Templates Django** suportados
- ✅ **HTML + Texto** automático
- ✅ **Mailpit integrado** para desenvolvimento
- ✅ **API REST** do Mailpit disponível
- ✅ **Zero configuração** SMTP externa necessária

---

**Pronto para enviar emails!** 🚀
