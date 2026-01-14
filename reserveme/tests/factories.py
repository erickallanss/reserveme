"""
Factories para testes usando Factory Boy.
"""
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from reserveme.models import ExampleModel

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """Factory para User model."""
    
    class Meta:
        model = User
        django_get_or_create = ('email',)
    
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    username = factory.Sequence(lambda n: f'user{n}')
    first_name = factory.Faker('first_name', locale='pt_BR')
    last_name = factory.Faker('last_name', locale='pt_BR')
    password = factory.PostGenerationMethodCall('set_password', 'TestPass123!@#')
    cpf = factory.Sequence(lambda n: f'{n:011d}'[:3] + '.' + f'{n:011d}'[3:6] + '.' + f'{n:011d}'[6:9] + '-' + f'{n:011d}'[9:11])
    telefone = factory.LazyAttribute(lambda o: f'(11) 9{factory.Faker("random_int", min=1000, max=9999).evaluate(None, None, {"locale": None})}-{factory.Faker("random_int", min=1000, max=9999).evaluate(None, None, {"locale": None})}')
    
    is_active = True
    is_approved = False
    email_verified = False
    role = 'customer'


class AdminUserFactory(UserFactory):
    """Factory para usuário Admin."""
    
    role = 'admin'
    is_approved = True
    email_verified = True
    is_staff = True
    is_superuser = True


class StaffUserFactory(UserFactory):
    """Factory para usuário Staff."""
    
    role = 'staff'
    is_approved = True
    email_verified = True
    is_staff = True


class ApprovedUserFactory(UserFactory):
    """Factory para usuário aprovado e verificado."""
    
    is_approved = True
    email_verified = True


class ExampleModelFactory(DjangoModelFactory):
    """Factory para ExampleModel."""
    
    class Meta:
        model = ExampleModel
    
    name = factory.Faker('sentence', nb_words=3, locale='pt_BR')
    description = factory.Faker('text', locale='pt_BR')
    created_by = factory.SubFactory(UserFactory)
