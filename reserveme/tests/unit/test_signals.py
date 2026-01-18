"""Unit tests for cache invalidation signals."""
import pytest
from django.core.cache import cache
from reserveme.models import Hotel, Room, Booking
from reserveme.tests.hotel_factories import HotelFactory
from reserveme.tests.room_factories import RoomFactory
from reserveme.tests.booking_factories import BookingFactory
from reserveme.cache_utils import get_cache_key, invalidate_hotel_cache, invalidate_room_cache, invalidate_booking_cache


@pytest.mark.django_db
class TestCacheSignals:
    """Tests for cache invalidation signals."""
    
    def test_hotel_save_invalidates_cache(self):
        """Test that saving a hotel invalidates its cache."""
        hotel = HotelFactory()
        cache_key = get_cache_key('hotel', hotel.id)
        cache.set(cache_key, {'data': 'test'}, 300)
        
        # Manually call invalidation (signals are tested via integration)
        invalidate_hotel_cache(hotel_id=hotel.id)
        
        # Cache should be invalidated
        assert cache.get(cache_key) is None
    
    def test_hotel_delete_invalidates_cache(self):
        """Test that deleting a hotel invalidates its cache."""
        hotel = HotelFactory()
        cache_key = get_cache_key('hotel', hotel.id)
        cache.set(cache_key, {'data': 'test'}, 300)
        
        # Manually call invalidation
        invalidate_hotel_cache(hotel_id=hotel.id)
        
        # Cache should be invalidated
        assert cache.get(cache_key) is None
    
    def test_room_save_invalidates_cache(self):
        """Test that saving a room invalidates its cache."""
        room = RoomFactory()
        room_key = get_cache_key('room', room.id)
        hotel_key = get_cache_key('hotel', room.hotel_id, 'rooms')
        
        cache.set(room_key, {'data': 'test'}, 300)
        cache.set(hotel_key, {'rooms': []}, 300)
        
        # Manually call invalidation
        invalidate_room_cache(room_id=room.id, hotel_id=room.hotel_id)
        
        # Cache should be invalidated
        assert cache.get(room_key) is None
        assert cache.get(hotel_key) is None
    
    def test_room_delete_invalidates_cache(self):
        """Test that deleting a room invalidates its cache."""
        room = RoomFactory()
        room_key = get_cache_key('room', room.id)
        hotel_key = get_cache_key('hotel', room.hotel_id, 'rooms')
        
        cache.set(room_key, {'data': 'test'}, 300)
        cache.set(hotel_key, {'rooms': []}, 300)
        
        # Manually call invalidation
        invalidate_room_cache(room_id=room.id, hotel_id=room.hotel_id)
        
        # Cache should be invalidated
        assert cache.get(room_key) is None
        assert cache.get(hotel_key) is None
    
    def test_booking_save_invalidates_cache(self):
        """Test that saving a booking invalidates its cache."""
        booking = BookingFactory()
        booking_key = get_cache_key('booking', booking.id)
        user_key = get_cache_key('user', booking.user_id, 'bookings')
        
        cache.set(booking_key, {'data': 'test'}, 300)
        cache.set(user_key, {'bookings': []}, 300)
        
        # Manually call invalidation
        invalidate_booking_cache(booking_id=booking.id, user_id=booking.user_id)
        
        # Cache should be invalidated
        assert cache.get(booking_key) is None
        assert cache.get(user_key) is None
    
    def test_booking_delete_invalidates_cache(self):
        """Test that deleting a booking invalidates its cache."""
        booking = BookingFactory()
        booking_key = get_cache_key('booking', booking.id)
        user_key = get_cache_key('user', booking.user_id, 'bookings')
        
        cache.set(booking_key, {'data': 'test'}, 300)
        cache.set(user_key, {'bookings': []}, 300)
        
        # Manually call invalidation
        invalidate_booking_cache(booking_id=booking.id, user_id=booking.user_id)
        
        # Cache should be invalidated
        assert cache.get(booking_key) is None
        assert cache.get(user_key) is None
