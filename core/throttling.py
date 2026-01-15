"""
Custom throttling classes para diferentes operações de autenticação.
"""
from rest_framework.throttling import AnonRateThrottle


class LoginThrottle(AnonRateThrottle):
    """Rate limiting específico para login (5 requests a cada 15 minutos)."""
    scope = 'auth_login'


class RegisterThrottle(AnonRateThrottle):
    """Rate limiting específico para registro (3 requests por hora)."""
    scope = 'auth_register'
