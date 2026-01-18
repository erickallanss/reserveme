"""Signals para invalidar cache automaticamente."""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from reserveme.models import Hotel, Room, Booking
from reserveme.cache_utils import (
    invalidate_hotel_cache,
    invalidate_room_cache,
    invalidate_booking_cache
)


@receiver(post_save, sender=Hotel)
@receiver(post_delete, sender=Hotel)
def invalidate_hotel_cache_signal(sender, instance, **kwargs):
    """Invalida cache quando hotel é salvo ou deletado."""
    invalidate_hotel_cache(hotel_id=instance.id)


@receiver(post_save, sender=Room)
@receiver(post_delete, sender=Room)
def invalidate_room_cache_signal(sender, instance, **kwargs):
    """Invalida cache quando quarto é salvo ou deletado."""
    invalidate_room_cache(room_id=instance.id, hotel_id=instance.hotel_id)


@receiver(post_save, sender=Booking)
@receiver(post_delete, sender=Booking)
def invalidate_booking_cache_signal(sender, instance, **kwargs):
    """Invalida cache quando reserva é salva ou deletada."""
    invalidate_booking_cache(booking_id=instance.id, user_id=instance.user_id)
