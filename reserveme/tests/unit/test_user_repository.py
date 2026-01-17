"""
Testes unitários para UserRepository.
"""
import pytest
from django.contrib.auth import get_user_model
from reserveme.repositories.user_repository import UserRepository
from reserveme.tests.factories import UserFactory, ApprovedUserFactory

User = get_user_model()


@pytest.fixture
def user_repository():
    """Fixture do repository."""
    return UserRepository()


@pytest.mark.django_db
class TestUserRepository:
    """Testes para UserRepository."""
    
    def test_create_user(self, user_repository):
        """Testa criação de usuário."""
        user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'TestPass123!@#',
            'first_name': 'Test',
            'last_name': 'User',
            'cpf': '11144477735',
        }
        
        user = user_repository.create(**user_data)
        
        assert user.id is not None
        assert user.email == user_data['email']
        assert user.username == user_data['username']
        assert user.cpf == user_data['cpf']
    
    def test_get_by_id(self, user_repository):
        """Testa busca por ID."""
        created_user = UserFactory()
        
        user = user_repository.get_by_id(created_user.id)
        
        assert user is not None
        assert user.id == created_user.id
        assert user.email == created_user.email
    
    def test_get_by_email(self, user_repository):
        """Testa busca por email."""
        created_user = UserFactory(email='specific@example.com')
        
        user = user_repository.get_by_email('specific@example.com')
        
        assert user is not None
        assert user.email == created_user.email
    
    def test_get_by_email_case_insensitive(self, user_repository):
        """Testa busca por email case-insensitive."""
        UserFactory(email='test@example.com')
        
        user = user_repository.get_by_email('TEST@EXAMPLE.COM')
        
        assert user is not None
        assert user.email == 'test@example.com'
    
    def test_get_by_username(self, user_repository):
        """Testa busca por username."""
        created_user = UserFactory(username='testuser')
        
        user = user_repository.get_by_username('testuser')
        
        assert user is not None
        assert user.username == created_user.username
    
    def test_get_by_cpf(self, user_repository):
        """Testa busca por CPF."""
        created_user = UserFactory(cpf='11144477735')
        
        user = user_repository.get_by_cpf('11144477735')
        
        assert user is not None
        assert user.cpf == created_user.cpf
    
    def test_get_by_verification_token(self, user_repository):
        """Testa busca por token de verificação."""
        token = 'test_token_123'
        UserFactory(email_verification_token=token)
        
        user = user_repository.get_by_verification_token(token)
        
        assert user is not None
        assert user.email_verification_token == token
    
    def test_email_exists(self, user_repository):
        """Testa verificação de existência de email."""
        assert not user_repository.email_exists('new@example.com')
        
        UserFactory(email='new@example.com')
        
        assert user_repository.email_exists('new@example.com')
    
    def test_username_exists(self, user_repository):
        """Testa verificação de existência de username."""
        assert not user_repository.username_exists('newuser')
        
        UserFactory(username='newuser')
        
        assert user_repository.username_exists('newuser')
    
    def test_cpf_exists(self, user_repository):
        """Testa verificação de existência de CPF."""
        cpf = '11144477735'
        assert not user_repository.cpf_exists(cpf)
        
        UserFactory(cpf=cpf)
        
        assert user_repository.cpf_exists(cpf)
    
    def test_update_user(self, user_repository):
        """Testa atualização de usuário."""
        user = UserFactory()
        
        updated = user_repository.update(user, first_name='Updated')
        
        assert updated.first_name == 'Updated'
        assert updated.email == user.email
    
    def test_delete_user(self, user_repository):
        """Testa exclusão de usuário."""
        user = UserFactory()
        user_id = user.id
        
        user_repository.delete(user)
        
        assert user_repository.get_by_id(user_id) is None
    
    def test_get_by_role(self, user_repository):
        """Testa busca por role."""
        UserFactory(role='customer')
        UserFactory(role='customer')
        UserFactory(role='admin')
        UserFactory(role='staff')
        
        customers = list(user_repository.get_by_role('customer'))
        admins = list(user_repository.get_by_role('admin'))
        staff = list(user_repository.get_by_role('staff'))
        
        assert len(customers) == 2
        assert len(admins) == 1
        assert len(staff) == 1
        assert all(u.role == 'customer' for u in customers)
        assert all(u.role == 'admin' for u in admins)
    
    def test_list_with_filters(self, user_repository):
        """Testa listagem com filtros."""
        UserFactory.create_batch(3, role='customer')
        UserFactory.create_batch(2, role='admin')
        
        all_users = user_repository.list()
        
        assert len(all_users) >= 5
    
    def test_get_nonexistent_user(self, user_repository):
        """Testa busca de usuário inexistente."""
        user = user_repository.get_by_id(99999)
        
        assert user is None
