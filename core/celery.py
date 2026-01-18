"""
Celery configuration for ReserveMe project.
"""
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('reserveme')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Import tasks from core.utils explicitly
app.autodiscover_tasks(['core.utils'])

# Configure Celery Beat schedule
from celery.schedules import crontab

app.conf.beat_schedule = {
    'release-expired-bookings': {
        'task': 'reserveme.tasks.release_expired_bookings_task',
        'schedule': crontab(minute='0', hour='*/1'),  # A cada 1 hora
    },
}

app.conf.timezone = 'America/Sao_Paulo'


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
