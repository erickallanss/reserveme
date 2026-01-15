"""
Testes para os models.
"""
import pytest
from django.contrib.auth import get_user_model
from reserveme.tests.factories import UserFactory, ApprovedUserFactory, AdminUserFactory

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Testes para o User model."""
    
    def test_user_str_representation(self):
        """Testa representação string do usuário."""
        user = UserFactory(first_name='John', last_name='Doe', email='john@example.com')
        assert str(user) == "John Doe (john@example.com)"
    
    def test_user_repr(self):
        """Testa repr do usuário."""
        user = UserFactory(email='john@example.com', role='customer')
        assert repr(user) == "<User: john@example.com - customer>"
    
    def test_can_login_approved_user(self):
        """Testa que usuário aprovado pode logar."""
        user = ApprovedUserFactory()
        assert user.can_login() is True
    
    def test_can_login_not_verified(self):
        """Testa que usuário não verificado não pode logar."""
        user = UserFactory(email_verified=False)
        assert user.can_login() is False
    
    def test_can_login_inactive(self):
        """Testa que usuário inativo não pode logar."""
        user = ApprovedUserFactory(is_active=False)
        assert user.can_login() is False
    
    def test_is_admin_property(self):
        """Testa propriedade is_admin."""
        admin = AdminUserFactory()
        assert admin.is_admin is True
        
        customer = UserFactory(role='customer')
        assert customer.is_admin is False
    
    def test_is_staff_member_property(self):
        """Testa propriedade is_staff_member."""
        admin = AdminUserFactory()
        assert admin.is_staff_member is True
        
        staff = UserFactory(role='staff')
        assert staff.is_staff_member is True
        
        customer = UserFactory(role='customer')
        assert customer.is_staff_member is False
    
    def test_is_customer_property(self):
        """Testa propriedade is_customer."""
        customer = UserFactory(role='customer')
        assert customer.is_customer is True
        
        admin = AdminUserFactory()
        assert admin.is_customer is False
