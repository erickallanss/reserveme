"""
Testes para URLs de autenticação.
"""
import pytest
from django.urls import reverse, resolve
from reserveme.views import auth_views


class TestAuthURLs:
    """Testes para URLs de autenticação."""
    
    def test_register_url_resolves(self):
        """Testa se URL de registro resolve corretamente."""
        url = reverse('auth-register')
        assert url == '/api/v1/auth/register/'
        assert resolve(url).func == auth_views.register
    
    def test_login_url_resolves(self):
        """Testa se URL de login resolve corretamente."""
        url = reverse('auth-login')
        assert url == '/api/v1/auth/login/'
        assert resolve(url).func == auth_views.login
    
    def test_logout_url_resolves(self):
        """Testa se URL de logout resolve corretamente."""
        url = reverse('auth-logout')
        assert url == '/api/v1/auth/logout/'
        assert resolve(url).func == auth_views.logout
    
    def test_refresh_url_resolves(self):
        """Testa se URL de refresh resolve corretamente."""
        url = reverse('auth-refresh')
        assert url == '/api/v1/auth/refresh/'
        assert resolve(url).func == auth_views.refresh_token
    
    def test_verify_email_url_resolves(self):
        """Testa se URL de verificação resolve corretamente."""
        url = reverse('auth-verify-email')
        assert url == '/api/v1/auth/verify-email/'
        assert resolve(url).func == auth_views.verify_email
    
    def test_me_url_resolves(self):
        """Testa se URL /me resolve corretamente."""
        url = reverse('auth-me')
        assert url == '/api/v1/auth/me/'
        assert resolve(url).func == auth_views.me
    
    def test_change_password_url_resolves(self):
        """Testa se URL de mudança de senha resolve corretamente."""
        url = reverse('auth-change-password')
        assert url == '/api/v1/auth/change-password/'
        assert resolve(url).func == auth_views.change_password
