"""
Filtros para API usando django-filter.
"""
import django_filters
from reserveme.models import Room, Booking


class RoomFilter(django_filters.FilterSet):
    """Filtros para Room."""
    
    hotel = django_filters.NumberFilter(field_name='hotel_id')
    tipo = django_filters.ChoiceFilter(choices=Room.TIPO_CHOICES)
    min_preco = django_filters.NumberFilter(field_name='preco_diaria', lookup_expr='gte')
    max_preco = django_filters.NumberFilter(field_name='preco_diaria', lookup_expr='lte')
    capacidade_min = django_filters.NumberFilter(field_name='capacidade', lookup_expr='gte')
    is_active = django_filters.BooleanFilter()
    
    class Meta:
        model = Room
        fields = ['hotel', 'tipo', 'is_active']


class BookingFilter(django_filters.FilterSet):
    """Filtros para Booking."""
    
    status = django_filters.ChoiceFilter(choices=Booking.STATUS_CHOICES)
    room = django_filters.NumberFilter(field_name='room_id')
    hotel = django_filters.NumberFilter(field_name='room__hotel_id')
    user = django_filters.NumberFilter(field_name='user_id')
    data_checkin_min = django_filters.DateFilter(field_name='data_checkin', lookup_expr='gte')
    data_checkin_max = django_filters.DateFilter(field_name='data_checkin', lookup_expr='lte')
    data_checkout_min = django_filters.DateFilter(field_name='data_checkout', lookup_expr='gte')
    data_checkout_max = django_filters.DateFilter(field_name='data_checkout', lookup_expr='lte')
    
    class Meta:
        model = Booking
        fields = ['status', 'room', 'user']
