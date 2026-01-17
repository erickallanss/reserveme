"""
Testes para os serializers.
"""
import pytest
from django.contrib.auth import get_user_model
from reserveme.serializers import (
    UserSerializer, UserRegisterSerializer, UserLoginSerializer,
    UserUpdateSerializer, PasswordChangeSerializer, EmailVerificationSerializer
)
from reserveme.tests.factories import UserFactory

User = get_user_model()


@pytest.mark.django_db
class TestUserSerializer:
    """Testes para UserSerializer."""
    
    def test_get_full_name(self):
        """Testa método get_full_name."""
        user = UserFactory(first_name='John', last_name='Doe')
        serializer = UserSerializer(instance=user)
        assert serializer.data['full_name'] == 'John Doe'


@pytest.mark.django_db
class TestUserRegisterSerializer:
    """Testes para UserRegisterSerializer."""
    
    def test_validate_email_lowercase(self):
        """Testa que email é convertido para lowercase."""
        data = {
            'email': 'TEST@EXAMPLE.COM',
            'username': 'testuser',
            'password': 'TestPass123!@#',
            'password_confirm': 'TestPass123!@#',
            'first_name': 'Test',
            'last_name': 'User',
            'cpf': '111.444.777-35',
        }
        serializer = UserRegisterSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['email'] == 'test@example.com'
    
    def test_validate_username_lowercase(self):
        """Testa que username é convertido para lowercase."""
        data = {
            'email': 'test@example.com',
            'username': 'TESTUSER',
            'password': 'TestPass123!@#',
            'password_confirm': 'TestPass123!@#',
            'first_name': 'Test',
            'last_name': 'User',
            'cpf': '11144477735',
        }
        serializer = UserRegisterSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['username'] == 'testuser'
    
    def test_validate_cpf_invalid_format(self):
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'TestPass123!@#',
            'password_confirm': 'TestPass123!@#',
            'first_name': 'Test',
            'last_name': 'User',
            'cpf': '12345678901',
        }
        serializer = UserRegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'cpf' in serializer.errors
    
    def test_validate_telefone_invalid_format(self):
        """Testa validação de telefone com formato inválido."""
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'TestPass123!@#',
            'password_confirm': 'TestPass123!@#',
            'first_name': 'Test',
            'last_name': 'User',
            'cpf': '111.444.777-35',
            'telefone': '11999999999',
        }
        serializer = UserRegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'telefone' in serializer.errors
    
    def test_validate_weak_password(self):
        """Testa validação de senha fraca."""
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': '123',
            'password_confirm': '123',
            'first_name': 'Test',
            'last_name': 'User',
            'cpf': '111.444.777-35',
        }
        serializer = UserRegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors


@pytest.mark.django_db
class TestUserUpdateSerializer:
    """Testes para UserUpdateSerializer."""
    
    def test_validate_telefone_valid(self):
        """Testa validação de telefone válido."""
        user = UserFactory()
        data = {'telefone': '(11) 99999-9999'}
        serializer = UserUpdateSerializer(instance=user, data=data, partial=True)
        assert serializer.is_valid()
    
    def test_validate_telefone_invalid(self):
        """Testa validação de telefone inválido."""
        user = UserFactory()
        data = {'telefone': '11999999999'}
        serializer = UserUpdateSerializer(instance=user, data=data, partial=True)
        assert not serializer.is_valid()
        assert 'telefone' in serializer.errors


@pytest.mark.django_db
class TestPasswordChangeSerializer:
    """Testes para PasswordChangeSerializer."""
    
    def test_passwords_dont_match(self):
        """Testa erro quando senhas não coincidem."""
        data = {
            'old_password': 'OldPass123!@#',
            'new_password': 'NewPass123!@#',
            'new_password_confirm': 'DifferentPass123!@#'
        }
        serializer = PasswordChangeSerializer(data=data)
        assert not serializer.is_valid()
        assert 'new_password_confirm' in serializer.errors
    
    def test_weak_new_password(self):
        """Testa erro com senha fraca."""
        user = UserFactory()
        data = {
            'old_password': 'OldPass123!@#',
            'new_password': '123',
            'new_password_confirm': '123'
        }
        serializer = PasswordChangeSerializer(data=data, context={'request': type('obj', (object,), {'user': user})()})
        assert not serializer.is_valid()
        assert 'new_password' in serializer.errors


class TestEmailVerificationSerializer:
    """Testes para EmailVerificationSerializer."""
    
    def test_token_required(self):
        """Testa que token é obrigatório."""
        serializer = EmailVerificationSerializer(data={})
        assert not serializer.is_valid()
        assert 'token' in serializer.errors
