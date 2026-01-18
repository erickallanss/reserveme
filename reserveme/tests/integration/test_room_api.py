"""
Testes de integração para endpoints de Room.
"""
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from reserveme.tests.room_factories import RoomFactory
from reserveme.tests.hotel_factories import HotelFactory
from reserveme.tests.factories import AdminUserFactory, StaffUserFactory, UserFactory


@pytest.fixture
def api_client():
    """Fixture do cliente API."""
    return APIClient()


@pytest.mark.django_db
class TestRoomAPI:
    """Testes de integração para API de Room."""
    
    def test_list_rooms_public(self, api_client):
        """Testa listagem pública de quartos."""
        room = RoomFactory(is_active=True)
        
        response = api_client.get('/api/v1/rooms/')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) >= 1
    
    def test_list_rooms_filter_by_hotel(self, api_client):
        """Testa filtro por hotel."""
        hotel = HotelFactory()
        room1 = RoomFactory(hotel=hotel)
        room2 = RoomFactory(hotel=hotel)
        other_room = RoomFactory()
        
        response = api_client.get(f'/api/v1/rooms/?hotel={hotel.id}')
        
        assert response.status_code == status.HTTP_200_OK
        rooms = response.data['results']
        room_ids = [r['id'] for r in rooms]
        assert room1.id in room_ids
        assert room2.id in room_ids
    
    def test_create_room_as_admin(self, api_client):
        """Testa criação de quarto como admin."""
        admin = AdminUserFactory()
        api_client.force_authenticate(user=admin)
        hotel = HotelFactory()
        
        data = {
            'hotel': hotel.id,
            'numero': '999',
            'tipo': 'double',
            'capacidade': 2,
            'preco_diaria': '250.00'
        }
        
        response = api_client.post('/api/v1/rooms/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['room']['numero'] == '999'
    
    def test_create_room_as_customer_forbidden(self, api_client):
        """Testa que cliente não pode criar quarto."""
        customer = UserFactory()
        api_client.force_authenticate(user=customer)
        hotel = HotelFactory()
        
        data = {
            'hotel': hotel.id,
            'numero': '999',
            'tipo': 'double',
            'capacidade': 2,
            'preco_diaria': '250.00'
        }
        
        response = api_client.post('/api/v1/rooms/', data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_room_details(self, api_client):
        """Testa busca de detalhes de quarto."""
        room = RoomFactory()
        
        response = api_client.get(f'/api/v1/rooms/{room.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == room.id
        assert response.data['numero'] == room.numero
    
    def test_update_room_as_staff(self, api_client):
        """Testa atualização de quarto como staff."""
        staff = StaffUserFactory()
        api_client.force_authenticate(user=staff)
        room = RoomFactory()
        
        data = {'preco_diaria': '300.00'}
        
        response = api_client.patch(f'/api/v1/rooms/{room.id}/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['room']['preco_diaria'] == '300.00'
