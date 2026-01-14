"""
Testes de integração para API de Autenticação.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from reserveme.tests.factories import UserFactory, ApprovedUserFactory, AdminUserFactory

User = get_user_model()


@pytest.fixture
def api_client():
    """Fixture do cliente API."""
    return APIClient()


@pytest.fixture
def authenticated_client():
    """Cliente autenticado."""
    client = APIClient()
    user = ApprovedUserFactory()
    client.force_authenticate(user=user)
    return client, user


@pytest.mark.django_db
class TestRegisterAPI:
    """Testes para endpoint de registro."""
    
    def test_register_success(self, api_client):
        """Testa registro bem-sucedido."""
        url = reverse('auth-register')
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'TestPass123!@#',
            'password_confirm': 'TestPass123!@#',
            'first_name': 'New',
            'last_name': 'User',
            'cpf': '123.456.789-00',
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert response.data['user']['email'] == data['email']
        
        # Verificar se usuário foi criado
        user = User.objects.get(email=data['email'])
        assert user.email_verified is False
        assert user.is_approved is False
    
    def test_register_duplicate_email(self, api_client):
        """Testa registro com email duplicado."""
        UserFactory(email='existing@example.com')
        
        url = reverse('auth-register')
        data = {
            'email': 'existing@example.com',
            'username': 'newuser',
            'password': 'TestPass123!@#',
            'password_confirm': 'TestPass123!@#',
            'first_name': 'New',
            'last_name': 'User',
            'cpf': '123.456.789-00',
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
    
    def test_register_password_mismatch(self, api_client):
        """Testa registro com senhas diferentes."""
        url = reverse('auth-register')
        data = {
            'email': 'test@example.com',
            'username': 'test',
            'password': 'TestPass123!@#',
            'password_confirm': 'DifferentPass123!@#',
            'first_name': 'Test',
            'last_name': 'User',
            'cpf': '123.456.789-00',
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password_confirm' in response.data
    
    def test_register_invalid_cpf_format(self, api_client):
        """Testa registro com CPF em formato inválido."""
        url = reverse('auth-register')
        data = {
            'email': 'test@example.com',
            'username': 'test',
            'password': 'TestPass123!@#',
            'password_confirm': 'TestPass123!@#',
            'first_name': 'Test',
            'last_name': 'User',
            'cpf': '12345678900',  # Formato errado
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'cpf' in response.data


@pytest.mark.django_db
class TestLoginAPI:
    """Testes para endpoint de login."""
    
    def test_login_success(self, api_client):
        """Testa login bem-sucedido."""
        user = ApprovedUserFactory()
        user.set_password('TestPass123!@#')
        user.save()
        
        url = reverse('auth-login')
        data = {
            'email': user.email,
            'password': 'TestPass123!@#',
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'user' in response.data
        assert response.data['user']['email'] == user.email
        
        # Verificar cookies
        assert 'access_token' in response.cookies
        assert 'refresh_token' in response.cookies
    
    def test_login_invalid_credentials(self, api_client):
        """Testa login com credenciais inválidas."""
        user = ApprovedUserFactory()
        user.set_password('correct_password')
        user.save()
        
        url = reverse('auth-login')
        data = {
            'email': user.email,
            'password': 'wrong_password',
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_not_verified(self, api_client):
        """Testa login com email não verificado."""
        user = UserFactory(email_verified=False, is_approved=True)
        user.set_password('TestPass123!@#')
        user.save()
        
        url = reverse('auth-login')
        data = {
            'email': user.email,
            'password': 'TestPass123!@#',
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'email' in str(response.data).lower()
    
    def test_login_not_approved(self, api_client):
        """Testa login com conta não aprovada."""
        user = UserFactory(email_verified=True, is_approved=False)
        user.set_password('TestPass123!@#')
        user.save()
        
        url = reverse('auth-login')
        data = {
            'email': user.email,
            'password': 'TestPass123!@#',
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'aprovação' in str(response.data).lower()


@pytest.mark.django_db
class TestLogoutAPI:
    """Testes para endpoint de logout."""
    
    def test_logout_success(self, authenticated_client):
        """Testa logout bem-sucedido."""
        client, user = authenticated_client
        
        url = reverse('auth-logout')
        response = client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
    
    def test_logout_unauthenticated(self, api_client):
        """Testa logout sem autenticação."""
        url = reverse('auth-logout')
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestMeAPI:
    """Testes para endpoint /me."""
    
    def test_get_me_success(self, authenticated_client):
        """Testa busca de dados do usuário autenticado."""
        client, user = authenticated_client
        
        url = reverse('auth-me')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email
        assert response.data['id'] == user.id
    
    def test_get_me_unauthenticated(self, api_client):
        """Testa /me sem autenticação."""
        url = reverse('auth-me')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_profile_success(self, authenticated_client):
        """Testa atualização de perfil."""
        client, user = authenticated_client
        
        url = reverse('auth-me')
        data = {
            'first_name': 'Updated',
            'telefone': '(11) 98765-4321',
        }
        
        response = client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['first_name'] == 'Updated'
        
        user.refresh_from_db()
        assert user.first_name == 'Updated'


@pytest.mark.django_db
class TestChangePasswordAPI:
    """Testes para endpoint de mudança de senha."""
    
    def test_change_password_success(self, authenticated_client):
        """Testa mudança de senha bem-sucedida."""
        client, user = authenticated_client
        user.set_password('OldPass123!@#')
        user.save()
        
        # Reautenticar com nova senha
        client.force_authenticate(user=user)
        
        url = reverse('auth-change-password')
        data = {
            'old_password': 'OldPass123!@#',
            'new_password': 'NewPass123!@#',
            'new_password_confirm': 'NewPass123!@#',
        }
        
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        user.refresh_from_db()
        assert user.check_password('NewPass123!@#')
    
    def test_change_password_wrong_old(self, authenticated_client):
        """Testa mudança com senha antiga incorreta."""
        client, user = authenticated_client
        user.set_password('OldPass123!@#')
        user.save()
        
        client.force_authenticate(user=user)
        
        url = reverse('auth-change-password')
        data = {
            'old_password': 'WrongPass123!@#',
            'new_password': 'NewPass123!@#',
            'new_password_confirm': 'NewPass123!@#',
        }
        
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestVerifyEmailAPI:
    """Testes para verificação de email."""
    
    def test_verify_email_success(self, api_client):
        """Testa verificação de email."""
        user = UserFactory(
            email_verified=False,
            email_verification_token='valid_token_123'
        )
        
        url = reverse('auth-verify-email')
        data = {'token': 'valid_token_123'}
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        user.refresh_from_db()
        assert user.email_verified is True
    
    def test_verify_email_invalid_token(self, api_client):
        """Testa verificação com token inválido."""
        url = reverse('auth-verify-email')
        data = {'token': 'invalid_token'}
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
