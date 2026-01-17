"""
Testes unitários para AuthService.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError, PermissionDenied
from core.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    EmailNotVerifiedError,
    InvalidVerificationTokenError,
)
from reserveme.services.auth_service import AuthService
from reserveme.repositories.user_repository import UserRepository
from reserveme.tests.factories import UserFactory, ApprovedUserFactory, AdminUserFactory

User = get_user_model()


@pytest.fixture
def user_repository():
    """Mock do repository."""
    return Mock(spec=UserRepository)


@pytest.fixture
def auth_service(user_repository):
    """Fixture do service."""
    return AuthService(repository=user_repository)


@pytest.mark.django_db
class TestAuthService:
    """Testes para AuthService."""
    
    @patch('reserveme.services.auth_service.send_template_email_async')
    def test_register_user_success(self, mock_email, auth_service, user_repository):
        """Testa registro de usuário com sucesso."""
        user_data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'cpf': '111.444.777-35',
        }
        
        created_user = UserFactory.build(**user_data)
        user_repository.create.return_value = created_user
        
        user = auth_service.register_user(user_data)
        
        assert user_repository.create.called
        assert mock_email.called
        assert user.email == user_data['email']
    
    def test_login_success(self, auth_service, user_repository):
        """Testa login bem-sucedido."""
        user = ApprovedUserFactory()
        user.set_password('TestPass123!@#')
        user.save()
        
        user_repository.get_by_email.return_value = user
        
        logged_user, tokens = auth_service.login(user.email, 'TestPass123!@#')
        
        assert logged_user == user
        assert 'access' in tokens
        assert 'refresh' in tokens
    
    def test_login_invalid_email(self, auth_service, user_repository):
        """Testa login com email inválido."""
        user_repository.get_by_email.return_value = None
        
        with pytest.raises(InvalidCredentialsError):
            auth_service.login('invalid@example.com', 'password')
    
    def test_login_invalid_password(self, auth_service, user_repository):
        """Testa login com senha inválida."""
        user = ApprovedUserFactory()
        user.set_password('correct_password')
        user.save()
        
        user_repository.get_by_email.return_value = user
        
        with pytest.raises(InvalidCredentialsError):
            auth_service.login(user.email, 'wrong_password')
    
    def test_login_email_not_verified(self, auth_service, user_repository):
        """Testa login com email não verificado."""
        user = UserFactory(email_verified=False)
        user.set_password('TestPass123!@#')
        user.save()
        
        user_repository.get_by_email.return_value = user
        
        with pytest.raises(EmailNotVerifiedError):
            auth_service.login(user.email, 'TestPass123!@#')
    
    
    @patch('reserveme.services.auth_service.send_template_email_async')
    def test_verify_email_success(self, mock_email, auth_service, user_repository):
        """Testa verificação de email e ativação da conta."""
        user = UserFactory(
            email_verified=False,
            email_verification_token='valid_token'
        )
        user_repository.get_by_verification_token.return_value = user
        
        verified_user = auth_service.verify_email('valid_token')
        
        assert verified_user.email_verified is True
        assert verified_user.email_verification_token == ''
        assert mock_email.called  # Verifica que email de ativação foi enviado
    
    def test_verify_email_invalid_token(self, auth_service, user_repository):
        """Testa verificação com token inválido."""
        user_repository.get_by_verification_token.return_value = None
        
        with pytest.raises(InvalidVerificationTokenError):
            auth_service.verify_email('invalid_token')
    
    @patch('reserveme.services.auth_service.send_template_email_async')
    def test_resend_verification_email(self, mock_email, auth_service, user_repository):
        """Testa reenvio de email de verificação."""
        user = UserFactory(email_verified=False)
        user_repository.get_by_email.return_value = user
        
        auth_service.resend_verification_email(user.email)
        
        assert mock_email.called
        assert user.email_verification_token != ''
    
    def test_resend_verification_already_verified(self, auth_service, user_repository):
        """Testa reenvio quando email já verificado."""
        user = ApprovedUserFactory()
        user_repository.get_by_email.return_value = user
        
        with pytest.raises(ValidationError) as exc:
            auth_service.resend_verification_email(user.email)
        
        assert 'já verificado' in str(exc.value).lower()
    
    def test_change_password_success(self, auth_service):
        """Testa mudança de senha."""
        user = ApprovedUserFactory()
        user.set_password('old_password')
        user.save()
        
        auth_service.change_password(user, 'old_password', 'NewPass123!@#')
        
        user.refresh_from_db()
        assert user.check_password('NewPass123!@#')
    
    def test_change_password_wrong_old_password(self, auth_service):
        """Testa mudança de senha com senha antiga incorreta."""
        user = ApprovedUserFactory()
        user.set_password('old_password')
        user.save()
        
        with pytest.raises(ValidationError) as exc:
            auth_service.change_password(user, 'wrong_password', 'NewPass123!@#')
        
        assert 'incorreta' in str(exc.value).lower()
    
    def test_refresh_token_success(self, auth_service, user_repository):
        """Testa refresh de token."""
        from rest_framework_simplejwt.tokens import RefreshToken
        
        user = ApprovedUserFactory()
        user_repository.get_by_id.return_value = user
        
        refresh = RefreshToken.for_user(user)
        refresh_token = str(refresh)
        
        tokens = auth_service.refresh_token(refresh_token)
        
        assert 'access' in tokens
        assert 'refresh' in tokens
    
    def test_refresh_token_invalid(self, auth_service):
        """Testa refresh com token inválido."""
        with pytest.raises(InvalidTokenError):
            auth_service.refresh_token('invalid_token')
