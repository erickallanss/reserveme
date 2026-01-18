"""Extended unit tests for HotelService."""
import pytest
from reserveme.services.hotel_service import (
    HotelService,
    HotelNotFoundError,
    HotelAlreadyExistsError
)
from reserveme.repositories.hotel_repository import HotelRepository
from reserveme.tests.hotel_factories import HotelFactory


@pytest.mark.django_db
class TestHotelServiceExtended:
    """Extended tests for HotelService."""
    
    @pytest.fixture
    def hotel_service(self):
        """Fixture that returns service instance."""
        return HotelService(HotelRepository())
    
    def test_list_hotels(self, hotel_service):
        """Test listing all hotels."""
        hotel1 = HotelFactory()
        hotel2 = HotelFactory()
        
        hotels = hotel_service.list_hotels()
        
        assert len(hotels) >= 2
        assert hotel1.id in [h.id for h in hotels]
        assert hotel2.id in [h.id for h in hotels]
    
    def test_list_active_hotels(self, hotel_service):
        """Test listing only active hotels."""
        active = HotelFactory(is_active=True)
        inactive = HotelFactory(is_active=False)
        
        active_hotels = hotel_service.list_active_hotels()
        
        hotel_ids = [h.id for h in active_hotels]
        assert active.id in hotel_ids
        assert inactive.id not in hotel_ids
    
    def test_update_hotel(self, hotel_service):
        """Test updating a hotel."""
        hotel = HotelFactory()
        
        updated = hotel_service.update_hotel(
            hotel.id,
            {'nome': 'Updated Name', 'descricao': 'New description'}
        )
        
        assert updated.nome == 'Updated Name'
        assert updated.descricao == 'New description'
    
    def test_update_hotel_duplicate_nome(self, hotel_service):
        """Test error when updating to duplicate nome."""
        hotel1 = HotelFactory(nome='Hotel A')
        hotel2 = HotelFactory(nome='Hotel B')
        
        with pytest.raises(HotelAlreadyExistsError):
            hotel_service.update_hotel(hotel2.id, {'nome': 'Hotel A'})
    
    def test_delete_hotel(self, hotel_service):
        """Test soft deleting a hotel."""
        hotel = HotelFactory(is_active=True)
        
        hotel_service.delete_hotel(hotel.id)
        
        updated = hotel_service.get_hotel(hotel.id)
        assert updated.is_active is False
    
    def test_delete_hotel_not_found(self, hotel_service):
        """Test error when deleting non-existent hotel."""
        with pytest.raises(HotelNotFoundError):
            hotel_service.delete_hotel(99999)
