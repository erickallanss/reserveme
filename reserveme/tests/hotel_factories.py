"""
Factory para criar objetos Hotel para testes.
"""
import factory
from factory.django import DjangoModelFactory
from reserveme.models import Hotel
from datetime import time


class HotelFactory(DjangoModelFactory):
    """Factory para criar instâncias de Hotel."""
    
    class Meta:
        model = Hotel
        skip_postgeneration_save = True
    
    nome = factory.Sequence(lambda n: f'Hotel {n}')
    descricao = factory.Faker('text', max_nb_chars=200, locale='pt_BR')
    endereco = factory.Faker('address', locale='pt_BR')
    telefone = '(11) 98765-4321'
    email = factory.Sequence(lambda n: f'hotel{n}@example.com')
    horario_checkin = time(14, 0)  # 14:00
    horario_checkout = time(12, 0)  # 12:00
    is_active = True
