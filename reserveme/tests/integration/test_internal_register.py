import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from reserveme.tests.factories import AdminUserFactory, ApprovedUserFactory

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_client():
    client = APIClient()
    admin = AdminUserFactory()
    client.force_authenticate(user=admin)
    return client, admin


@pytest.mark.django_db
class TestInternalRegisterAPI:
    
    def test_admin_can_create_staff_user(self, admin_client):
        client, admin = admin_client
        url = reverse('internal-register')
        data = {
            'email': 'staff@example.com',
            'username': 'staffuser',
            'password': 'TestPass123!@#',
            'password_confirm': 'TestPass123!@#',
            'first_name': 'Staff',
            'last_name': 'User',
            'cpf': '123.456.789-00',
            'role': 'staff'
        }
        
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert response.data['user']['role'] == 'staff'
        assert response.data['user']['email_verified'] is True
        
        user = User.objects.get(email='staff@example.com')
        assert user.role == 'staff'
        assert user.email_verified is True
        assert user.is_active is True
    
    def test_admin_can_create_admin_user(self, admin_client):
        client, admin = admin_client
        url = reverse('internal-register')
        data = {
            'email': 'newadmin@example.com',
            'username': 'newadmin',
            'password': 'TestPass123!@#',
            'password_confirm': 'TestPass123!@#',
            'first_name': 'New',
            'last_name': 'Admin',
            'cpf': '987.654.321-00',
            'role': 'admin'
        }
        
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['user']['role'] == 'admin'
    
    def test_non_admin_cannot_create_internal_user(self, api_client):
        user = ApprovedUserFactory(role='customer')
        api_client.force_authenticate(user=user)
        
        url = reverse('internal-register')
        data = {
            'email': 'staff@example.com',
            'username': 'staffuser',
            'password': 'TestPass123!@#',
            'password_confirm': 'TestPass123!@#',
            'first_name': 'Staff',
            'last_name': 'User',
            'cpf': '123.456.789-00',
            'role': 'staff'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_unauthenticated_cannot_create_internal_user(self, api_client):
        url = reverse('internal-register')
        data = {
            'email': 'staff@example.com',
            'username': 'staffuser',
            'password': 'TestPass123!@#',
            'password_confirm': 'TestPass123!@#',
            'first_name': 'Staff',
            'last_name': 'User',
            'cpf': '123.456.789-00',
            'role': 'staff'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_cannot_create_customer_via_internal_register(self, admin_client):
        client, admin = admin_client
        url = reverse('internal-register')
        data = {
            'email': 'customer@example.com',
            'username': 'customer',
            'password': 'TestPass123!@#',
            'password_confirm': 'TestPass123!@#',
            'first_name': 'Customer',
            'last_name': 'User',
            'cpf': '123.456.789-00',
            'role': 'customer'
        }
        
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'role' in response.data
    
    def test_password_mismatch(self, admin_client):
        client, admin = admin_client
        url = reverse('internal-register')
        data = {
            'email': 'staff@example.com',
            'username': 'staffuser',
            'password': 'TestPass123!@#',
            'password_confirm': 'DifferentPass123!@#',
            'first_name': 'Staff',
            'last_name': 'User',
            'cpf': '123.456.789-00',
            'role': 'staff'
        }
        
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password_confirm' in response.data
    
    def test_duplicate_email(self, admin_client):
        client, admin = admin_client
        ApprovedUserFactory(email='existing@example.com')
        
        url = reverse('internal-register')
        data = {
            'email': 'existing@example.com',
            'username': 'staffuser',
            'password': 'TestPass123!@#',
            'password_confirm': 'TestPass123!@#',
            'first_name': 'Staff',
            'last_name': 'User',
            'cpf': '123.456.789-00',
            'role': 'staff'
        }
        
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
