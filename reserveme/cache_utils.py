"""Utilitários para gerenciamento de cache."""
from django.core.cache import cache
from typing import Optional


def get_cache_key(prefix: str, *args, **kwargs) -> str:
    """Gera chave de cache padronizada.
    
    Args:
        prefix: Prefixo da chave (ex: 'hotel', 'room', 'booking').
        *args: Argumentos para compor a chave.
        **kwargs: Argumentos nomeados para compor a chave.
        
    Returns:
        Chave de cache formatada.
    """
    parts = [prefix]
    if args:
        parts.extend(str(arg) for arg in args)
    if kwargs:
        parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
    return ":".join(parts)


def invalidate_hotel_cache(hotel_id: Optional[int] = None):
    """Invalida cache relacionado a hotéis.
    
    Args:
        hotel_id: ID do hotel específico (opcional).
    """
    if hotel_id:
        cache.delete(get_cache_key('hotel', hotel_id))
        cache.delete(get_cache_key('hotel', hotel_id, 'rooms'))
    cache.delete('hotels:list')
    cache.delete('hotels:active')


def invalidate_room_cache(room_id: Optional[int] = None, hotel_id: Optional[int] = None):
    """Invalida cache relacionado a quartos.
    
    Args:
        room_id: ID do quarto específico (opcional).
        hotel_id: ID do hotel (opcional).
    """
    if room_id:
        cache.delete(get_cache_key('room', room_id))
    if hotel_id:
        cache.delete(get_cache_key('hotel', hotel_id, 'rooms'))
    cache.delete('rooms:list')
    cache.delete('rooms:active')


def invalidate_booking_cache(booking_id: Optional[int] = None, user_id: Optional[int] = None):
    """Invalida cache relacionado a reservas.
    
    Args:
        booking_id: ID da reserva específica (opcional).
        user_id: ID do usuário (opcional).
    """
    if booking_id:
        cache.delete(get_cache_key('booking', booking_id))
    if user_id:
        cache.delete(get_cache_key('user', user_id, 'bookings'))
    cache.delete('bookings:list')
