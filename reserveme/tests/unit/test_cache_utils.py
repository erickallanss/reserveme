"""Unit tests for cache utilities."""
import pytest
from django.core.cache import cache
from reserveme.cache_utils import (
    get_cache_key,
    invalidate_hotel_cache,
    invalidate_room_cache,
    invalidate_booking_cache
)


@pytest.mark.django_db
class TestCacheUtils:
    """Tests for cache utility functions."""
    
    def test_get_cache_key_with_args(self):
        """Test cache key generation with positional arguments."""
        key = get_cache_key('hotel', 1, 'rooms')
        assert key == 'hotel:1:rooms'
    
    def test_get_cache_key_with_kwargs(self):
        """Test cache key generation with keyword arguments."""
        key = get_cache_key('bookings', user=1, staff=True)
        assert 'bookings' in key
        assert 'user:1' in key
        assert 'staff:True' in key
    
    def test_get_cache_key_with_args_and_kwargs(self):
        """Test cache key generation with both args and kwargs."""
        key = get_cache_key('room', 5, hotel=1, active=True)
        assert 'room:5' in key
        assert 'hotel:1' in key
        assert 'active:True' in key
    
    def test_invalidate_hotel_cache_with_id(self):
        """Test hotel cache invalidation with specific hotel ID."""
        # Set some cache
        cache.set(get_cache_key('hotel', 1), {'data': 'test'}, 300)
        cache.set(get_cache_key('hotel', 1, 'rooms'), {'rooms': []}, 300)
        
        invalidate_hotel_cache(hotel_id=1)
        
        assert cache.get(get_cache_key('hotel', 1)) is None
        assert cache.get(get_cache_key('hotel', 1, 'rooms')) is None
    
    def test_invalidate_hotel_cache_without_id(self):
        """Test hotel cache invalidation without specific ID."""
        cache.set('hotels:list', {'data': 'test'}, 300)
        cache.set('hotels:active', {'data': 'test'}, 300)
        
        invalidate_hotel_cache()
        
        assert cache.get('hotels:list') is None
        assert cache.get('hotels:active') is None
    
    def test_invalidate_room_cache_with_ids(self):
        """Test room cache invalidation with room and hotel IDs."""
        cache.set(get_cache_key('room', 1), {'data': 'test'}, 300)
        cache.set(get_cache_key('hotel', 1, 'rooms'), {'rooms': []}, 300)
        
        invalidate_room_cache(room_id=1, hotel_id=1)
        
        assert cache.get(get_cache_key('room', 1)) is None
        assert cache.get(get_cache_key('hotel', 1, 'rooms')) is None
    
    def test_invalidate_room_cache_without_ids(self):
        """Test room cache invalidation without specific IDs."""
        cache.set('rooms:list', {'data': 'test'}, 300)
        cache.set('rooms:active', {'data': 'test'}, 300)
        
        invalidate_room_cache()
        
        assert cache.get('rooms:list') is None
        assert cache.get('rooms:active') is None
    
    def test_invalidate_booking_cache_with_ids(self):
        """Test booking cache invalidation with booking and user IDs."""
        cache.set(get_cache_key('booking', 1), {'data': 'test'}, 300)
        cache.set(get_cache_key('user', 1, 'bookings'), {'bookings': []}, 300)
        
        invalidate_booking_cache(booking_id=1, user_id=1)
        
        assert cache.get(get_cache_key('booking', 1)) is None
        assert cache.get(get_cache_key('user', 1, 'bookings')) is None
    
    def test_invalidate_booking_cache_without_ids(self):
        """Test booking cache invalidation without specific IDs."""
        cache.set('bookings:list', {'data': 'test'}, 300)
        
        invalidate_booking_cache()
        
        assert cache.get('bookings:list') is None
