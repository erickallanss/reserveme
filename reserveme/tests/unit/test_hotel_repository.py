"""
Testes unitários para o repositório de Hotel.
"""
import pytest
from reserveme.repositories.hotel_repository import HotelRepository
from reserveme.tests.hotel_factories import HotelFactory


@pytest.mark.django_db
class TestHotelRepository:
    """Testes para HotelRepository."""
    
    @pytest.fixture
    def hotel_repository(self):
        """Fixture que retorna instância do repositório."""
        return HotelRepository()
    
    def test_create_hotel(self, hotel_repository):
        """Testa criação de hotel."""
        hotel_data = {
            'nome': 'Hotel Teste',
            'descricao': 'Descrição do hotel teste',
            'endereco': 'Rua Teste, 123',
            'telefone': '(11) 98765-4321',
            'email': 'teste@hotel.com',
            'horario_checkin': '14:00',
            'horario_checkout': '12:00'
        }
        
        hotel = hotel_repository.create(**hotel_data)
        
        assert hotel.id is not None
        assert hotel.nome == hotel_data['nome']
        assert hotel.email == hotel_data['email']
    
    def test_get_by_id(self, hotel_repository):
        """Testa busca por ID."""
        hotel = HotelFactory()
        
        found_hotel = hotel_repository.get_by_id(hotel.id)
        
        assert found_hotel is not None
        assert found_hotel.id == hotel.id
    
    def test_get_by_nome(self, hotel_repository):
        """Testa busca por nome."""
        hotel = HotelFactory(nome='Hotel Unique')
        
        found_hotel = hotel_repository.get_by_nome('Hotel Unique')
        
        assert found_hotel is not None
        assert found_hotel.nome == hotel.nome
    
    def test_get_by_nome_case_insensitive(self, hotel_repository):
        """Testa busca por nome case insensitive."""
        hotel = HotelFactory(nome='Hotel Unique')
        
        found_hotel = hotel_repository.get_by_nome('hotel unique')
        
        assert found_hotel is not None
        assert found_hotel.id == hotel.id
    
    def test_get_by_email(self, hotel_repository):
        """Testa busca por email."""
        hotel = HotelFactory(email='unique@hotel.com')
        
        found_hotel = hotel_repository.get_by_email('unique@hotel.com')
        
        assert found_hotel is not None
        assert found_hotel.email == hotel.email
    
    def test_get_active_hotels(self, hotel_repository):
        """Testa busca de hotéis ativos."""
        active_hotel = HotelFactory(is_active=True)
        inactive_hotel = HotelFactory(is_active=False)
        
        active_hotels = hotel_repository.get_active_hotels()
        
        assert len(active_hotels) >= 1
        assert active_hotel.id in [h.id for h in active_hotels]
        assert inactive_hotel.id not in [h.id for h in active_hotels]
    
    def test_nome_exists(self, hotel_repository):
        """Testa verificação de existência de nome."""
        hotel = HotelFactory(nome='Hotel Exists')
        
        assert hotel_repository.nome_exists('Hotel Exists') is True
        assert hotel_repository.nome_exists('Hotel Not Exists') is False
    
    def test_nome_exists_exclude_id(self, hotel_repository):
        """Testa verificação de nome excluindo um ID."""
        hotel = HotelFactory(nome='Hotel Exists')
        
        assert hotel_repository.nome_exists('Hotel Exists', exclude_id=hotel.id) is False
    
    def test_email_exists(self, hotel_repository):
        """Testa verificação de existência de email."""
        hotel = HotelFactory(email='exists@hotel.com')
        
        assert hotel_repository.email_exists('exists@hotel.com') is True
        assert hotel_repository.email_exists('notexists@hotel.com') is False
    
    def test_update_hotel(self, hotel_repository):
        """Testa atualização de hotel."""
        hotel = HotelFactory()
        
        updated_hotel = hotel_repository.update(hotel, nome='Hotel Atualizado')
        
        assert updated_hotel.nome == 'Hotel Atualizado'
    
    def test_delete_hotel(self, hotel_repository):
        """Testa deleção de hotel."""
        hotel = HotelFactory()
        hotel_id = hotel.id
        
        hotel_repository.delete(hotel)
        
        assert hotel_repository.get_by_id(hotel_id) is None
