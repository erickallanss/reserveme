"""
Factory para criar objetos Room para testes.
"""
import factory
from factory.django import DjangoModelFactory
from decimal import Decimal
from reserveme.models import Room
from reserveme.tests.hotel_factories import HotelFactory


class RoomFactory(DjangoModelFactory):
    """Factory para criar instâncias de Room."""
    
    class Meta:
        model = Room
        skip_postgeneration_save = True
    
    hotel = factory.SubFactory(HotelFactory)
    numero = factory.Sequence(lambda n: f'{100 + n}')
    tipo = 'double'
    descricao = factory.Faker('text', max_nb_chars=200, locale='pt_BR')
    capacidade = 2
    preco_diaria = Decimal('250.00')
    tem_ar_condicionado = True
    tem_wifi = True
    tem_tv = True
    tem_frigobar = True
    tem_banheira = False
    tem_varanda = False
    is_active = True


class SuiteRoomFactory(RoomFactory):
    """Factory para criar suítes."""
    
    tipo = 'suite'
    capacidade = 2
    preco_diaria = Decimal('500.00')
    tem_banheira = True
    tem_varanda = True


class SingleRoomFactory(RoomFactory):
    """Factory para criar quartos single."""
    
    tipo = 'single'
    capacidade = 1
    preco_diaria = Decimal('150.00')
