"""
Testes para URLs de autenticação.
"""
import pytest
from django.urls import reverse, resolve
from reserveme.views.auth_views import (
    RegisterAPIView,
    LoginAPIView,
    LogoutAPIView,
    RefreshTokenAPIView,
    VerifyEmailAPIView,
    UserProfileAPIView,
    ChangePasswordAPIView,
    InternalRegisterAPIView,
)


class TestAuthURLs:
    
    def test_register_url_resolves(self):
        url = reverse('auth-register')
        assert url == '/api/v1/auth/register/'
        assert resolve(url).func.view_class == RegisterAPIView
    
    def test_login_url_resolves(self):
        url = reverse('auth-login')
        assert url == '/api/v1/auth/login/'
        assert resolve(url).func.view_class == LoginAPIView
    
    def test_logout_url_resolves(self):
        url = reverse('auth-logout')
        assert url == '/api/v1/auth/logout/'
        assert resolve(url).func.view_class == LogoutAPIView
    
    def test_refresh_url_resolves(self):
        url = reverse('auth-refresh')
        assert url == '/api/v1/auth/refresh/'
        assert resolve(url).func.view_class == RefreshTokenAPIView
    
    def test_verify_email_url_resolves(self):
        url = reverse('auth-verify-email')
        assert url == '/api/v1/auth/verify-email/'
        assert resolve(url).func.view_class == VerifyEmailAPIView
    
    def test_me_url_resolves(self):
        url = reverse('auth-me')
        assert url == '/api/v1/auth/me/'
        assert resolve(url).func.view_class == UserProfileAPIView
    
    def test_change_password_url_resolves(self):
        url = reverse('auth-change-password')
        assert url == '/api/v1/auth/change-password/'
        assert resolve(url).func.view_class == ChangePasswordAPIView
    
    def test_internal_register_url_resolves(self):
        url = reverse('internal-register')
        assert url == '/api/v1/internal/register/'
        assert resolve(url).func.view_class == InternalRegisterAPIView
