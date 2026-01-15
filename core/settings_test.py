"""
Settings específicos para testes.
"""
from .settings import *  # noqa

# Desabilitar throttling nos testes (rates altas para não interferir)
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '1000/minute',
    'user': '1000/minute',
    'auth_login': '1000/minute',
    'auth_register': '1000/hour',
}

# Usar cache em memória para testes (evita conflitos de throttling)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-cache',
    }
}

# Celery em modo EAGER (executa tasks síncronas nos testes)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Email backend para testes (não envia emails de verdade)
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
