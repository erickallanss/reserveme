"""
Classe base para repositories.
Implementa métodos comuns que podem ser reutilizados.
"""
from typing import Optional, List, TypeVar, Generic
from django.db.models import Model, QuerySet
from django.core.exceptions import ObjectDoesNotExist

from reserveme.repositories.protocols import BaseRepositoryProtocol

T = TypeVar('T', bound=Model)


class BaseRepository(Generic[T]):
    """
    Classe base abstrata para repositories.
    Fornece implementação padrão dos métodos do protocolo.
    """
    
    def __init__(self, model: type[T]):
        """Inicializa o repository com o model."""
        self.model = model
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Busca uma instância pelo ID."""
        try:
            return self.model.objects.get(pk=id)
        except ObjectDoesNotExist:
            return None
    
    def get_all(self) -> List[T]:
        """Retorna todas as instâncias."""
        return list(self.model.objects.all())
    
    def create(self, **kwargs) -> T:
        """Cria uma nova instância."""
        return self.model.objects.create(**kwargs)
    
    def update(self, instance: T, **kwargs) -> T:
        """Atualiza uma instância existente."""
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save()
        return instance
    
    def delete(self, instance: T) -> None:
        """Deleta uma instância."""
        instance.delete()
    
    def exists(self, id: int) -> bool:
        """Verifica se uma instância existe pelo ID."""
        return self.model.objects.filter(pk=id).exists()
    
    def get_queryset(self) -> QuerySet[T]:
        """Retorna um QuerySet base."""
        return self.model.objects.all()
    
    def filter(self, **kwargs) -> QuerySet[T]:
        """Aplica filtros ao QuerySet."""
        return self.model.objects.filter(**kwargs)
    
    def get(self, **kwargs) -> Optional[T]:
        """Busca uma instância usando filtros."""
        try:
            return self.model.objects.get(**kwargs)
        except ObjectDoesNotExist:
            return None
    
    def list(self, **filters) -> list[T]:
        """Lista registros como uma lista Python."""
        if filters:
            return list(self.filter(**filters))
        return list(self.get_queryset())
