"""
Custom throttling classes para diferentes operações de autenticação.
"""
from rest_framework.throttling import AnonRateThrottle


class LoginThrottle(AnonRateThrottle):
    """Rate limiting específico para login."""
    rate = '5/15min'
    scope = 'auth_login'


class RegisterThrottle(AnonRateThrottle):
    """Rate limiting específico para registro."""
    rate = '3/hour'
    scope = 'auth_register'
