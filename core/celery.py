"""Configuração do Celery para o projeto ReserveMe."""
import os
from celery import Celery
from celery.schedules import crontab

# Configurar módulo de settings do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('reserveme')

# Configurar usando namespace CELERY
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descobrir tasks automaticamente
app.autodiscover_tasks()
app.autodiscover_tasks(['core.utils'])

# Configurar schedule do Celery Beat
app.conf.beat_schedule = {
    'release-expired-bookings': {
        'task': 'reserveme.tasks.release_expired_bookings_task',
        'schedule': crontab(minute='0', hour='*/1'),  # A cada 1 hora
    },
}

app.conf.timezone = 'America/Sao_Paulo'


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Task de debug para testar Celery."""
    print(f'Request: {self.request!r}')
