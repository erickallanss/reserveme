"""
Factory para criar objetos Booking para testes.
"""
import factory
from factory.django import DjangoModelFactory
from decimal import Decimal
from datetime import date, timedelta
from reserveme.models import Booking
from reserveme.tests.room_factories import RoomFactory
from reserveme.tests.factories import UserFactory


class BookingFactory(DjangoModelFactory):
    """Factory para criar instâncias de Booking."""
    
    class Meta:
        model = Booking
        skip_postgeneration_save = True
    
    room = factory.SubFactory(RoomFactory)
    user = factory.SubFactory(UserFactory)
    data_checkin = factory.LazyFunction(lambda: date.today() + timedelta(days=5))
    data_checkout = factory.LazyFunction(lambda: date.today() + timedelta(days=8))
    numero_hospedes = 2
    numero_diarias = 3
    preco_diaria = Decimal('250.00')
    preco_total = Decimal('750.00')
    status = 'pending'
    observacoes = ''


class ConfirmedBookingFactory(BookingFactory):
    """Factory para criar reservas confirmadas."""
    
    status = 'confirmed'


class CheckedInBookingFactory(BookingFactory):
    """Factory para criar reservas com check-in realizado."""
    
    status = 'checked_in'
    data_checkin = factory.LazyFunction(lambda: date.today() - timedelta(days=1))


class CancelledBookingFactory(BookingFactory):
    """Factory para criar reservas canceladas."""
    
    status = 'cancelled'
