"""
Configuração global do pytest
"""
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def user(db):
    """Cria um usuário de teste"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def api_client():
    """Cliente API sem autenticação"""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_api_client(user):
    """Cliente API com autenticação"""
    from rest_framework.test import APIClient
    from rest_framework_simplejwt.tokens import RefreshToken
    
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client
