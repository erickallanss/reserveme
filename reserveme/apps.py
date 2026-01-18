"""Configuração do app reserveme."""
from django.apps import AppConfig


class ReservemeConfig(AppConfig):
    """Configuração do app reserveme."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reserveme'
    
    def ready(self):
        """Importa signals quando app está pronto."""
        import reserveme.signals  # noqa