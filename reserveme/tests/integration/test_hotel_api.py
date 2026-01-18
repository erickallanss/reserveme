"""
Testes de integração para API de Hotel.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from reserveme.tests.factories import AdminUserFactory, UserFactory
from reserveme.tests.hotel_factories import HotelFactory
from reserveme.models import Hotel


@pytest.fixture
def api_client():
    """Fixture do cliente API."""
    return APIClient()


@pytest.fixture
def admin_client():
    """Cliente autenticado como admin."""
    client = APIClient()
    admin = AdminUserFactory()
    client.force_authenticate(user=admin)
    return client, admin


@pytest.fixture
def customer_client():
    """Cliente autenticado como cliente."""
    client = APIClient()
    user = UserFactory()
    client.force_authenticate(user=user)
    return client, user


@pytest.mark.django_db
class TestHotelListCreateAPI:
    """Testes para endpoint de listagem e criação de hotéis."""
    
    def test_list_hotels_public(self, api_client):
        """Testa listagem de hotéis (público)."""
        HotelFactory.create_batch(3, is_active=True)
        HotelFactory(is_active=False)  # Inativo não deve aparecer
        
        url = reverse('hotel-list-create')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert response.data['count'] == 3
    
    def test_list_hotels_admin_sees_all(self, admin_client):
        """Testa que admin vê todos os hotéis."""
        client, admin = admin_client
        
        HotelFactory.create_batch(3, is_active=True)
        HotelFactory(is_active=False)
        
        url = reverse('hotel-list-create')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 4
    
    def test_create_hotel_as_admin(self, admin_client):
        """Testa criação de hotel como admin."""
        client, admin = admin_client
        
        url = reverse('hotel-list-create')
        data = {
            'nome': 'Novo Hotel',
            'descricao': 'Descrição do novo hotel',
            'endereco': 'Rua Nova, 123',
            'telefone': '(11) 98765-4321',
            'email': 'novo@hotel.com',
            'horario_checkin': '14:00:00',
            'horario_checkout': '12:00:00'
        }
        
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'hotel' in response.data
        assert response.data['hotel']['nome'] == 'Novo Hotel'
        
        # Verificar se foi criado no banco
        assert Hotel.objects.filter(nome='Novo Hotel').exists()
    
    def test_create_hotel_unauthenticated(self, api_client):
        """Testa que usuário não autenticado não pode criar hotel."""
        url = reverse('hotel-list-create')
        data = {
            'nome': 'Novo Hotel',
            'endereco': 'Rua Nova, 123',
            'telefone': '(11) 98765-4321',
            'email': 'novo@hotel.com',
            'horario_checkin': '14:00:00',
            'horario_checkout': '12:00:00'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_hotel_as_customer(self, customer_client):
        """Testa que cliente não pode criar hotel."""
        client, user = customer_client
        
        url = reverse('hotel-list-create')
        data = {
            'nome': 'Novo Hotel',
            'endereco': 'Rua Nova, 123',
            'telefone': '(11) 98765-4321',
            'email': 'novo@hotel.com',
            'horario_checkin': '14:00:00',
            'horario_checkout': '12:00:00'
        }
        
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_hotel_duplicate_nome(self, admin_client):
        """Testa que não pode criar hotel com nome duplicado."""
        client, admin = admin_client
        
        existing_hotel = HotelFactory(nome='Hotel Existente')
        
        url = reverse('hotel-list-create')
        data = {
            'nome': 'Hotel Existente',
            'endereco': 'Rua Nova, 123',
            'telefone': '(11) 98765-4321',
            'email': 'novo@hotel.com',
            'horario_checkin': '14:00:00',
            'horario_checkout': '12:00:00'
        }
        
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'nome' in response.data or 'error' in response.data


@pytest.mark.django_db
class TestHotelDetailAPI:
    """Testes para endpoint de detalhes do hotel."""
    
    def test_get_hotel_public(self, api_client):
        """Testa obtenção de detalhes de hotel (público)."""
        hotel = HotelFactory()
        
        url = reverse('hotel-detail', kwargs={'hotel_id': hotel.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['nome'] == hotel.nome
    
    def test_get_hotel_not_found(self, api_client):
        """Testa obtenção de hotel inexistente."""
        url = reverse('hotel-detail', kwargs={'hotel_id': 99999})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_inactive_hotel_as_public(self, api_client):
        """Testa que usuário público não vê hotel inativo."""
        hotel = HotelFactory(is_active=False)
        
        url = reverse('hotel-detail', kwargs={'hotel_id': hotel.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_inactive_hotel_as_admin(self, admin_client):
        """Testa que admin vê hotel inativo."""
        client, admin = admin_client
        
        hotel = HotelFactory(is_active=False)
        
        url = reverse('hotel-detail', kwargs={'hotel_id': hotel.id})
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_active'] is False
    
    def test_update_hotel_as_admin(self, admin_client):
        """Testa atualização de hotel como admin."""
        client, admin = admin_client
        
        hotel = HotelFactory(nome='Hotel Original')
        
        url = reverse('hotel-detail', kwargs={'hotel_id': hotel.id})
        data = {
            'nome': 'Hotel Atualizado',
            'descricao': 'Nova descrição'
        }
        
        response = client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['hotel']['nome'] == 'Hotel Atualizado'
        
        # Verificar no banco
        hotel.refresh_from_db()
        assert hotel.nome == 'Hotel Atualizado'
    
    def test_update_hotel_unauthenticated(self, api_client):
        """Testa que usuário não autenticado não pode atualizar."""
        hotel = HotelFactory()
        
        url = reverse('hotel-detail', kwargs={'hotel_id': hotel.id})
        data = {'nome': 'Hotel Atualizado'}
        
        response = api_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_delete_hotel_as_admin(self, admin_client):
        """Testa desativação de hotel como admin."""
        client, admin = admin_client
        
        hotel = HotelFactory(is_active=True)
        
        url = reverse('hotel-detail', kwargs={'hotel_id': hotel.id})
        response = client.delete(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar que foi desativado (soft delete)
        hotel.refresh_from_db()
        assert hotel.is_active is False
    
    def test_delete_hotel_unauthenticated(self, api_client):
        """Testa que usuário não autenticado não pode deletar."""
        hotel = HotelFactory()
        
        url = reverse('hotel-detail', kwargs={'hotel_id': hotel.id})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
