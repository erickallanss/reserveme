"""
Repository para operações de Booking.
"""
from typing import Optional, List
from datetime import date, datetime
from django.db.models import Q
from django.utils import timezone
from reserveme.repositories.base import BaseRepository
from reserveme.models import Booking


class BookingRepository(BaseRepository):
    """Repository para gerenciar operações de Booking."""
    
    def __init__(self):
        super().__init__(Booking)
    
    def get_by_codigo(self, codigo_reserva: str) -> Optional[Booking]:
        """Busca reserva por código."""
        return self.model.objects.filter(codigo_reserva=codigo_reserva).first()
    
    def get_user_bookings(
        self, 
        user_id: int,
        status: Optional[str] = None
    ) -> List[Booking]:
        """Retorna todas as reservas de um usuário."""
        queryset = self.model.objects.filter(user_id=user_id)
        if status:
            queryset = queryset.filter(status=status)
        return list(queryset.select_related('room', 'room__hotel', 'user'))
    
    def get_active_bookings(self) -> List[Booking]:
        """Retorna todas as reservas ativas (não canceladas/não finalizadas)."""
        return list(
            self.model.objects.filter(
                status__in=['pending', 'confirmed', 'checked_in']
            ).select_related('room', 'room__hotel', 'user')
        )
    
    def get_room_bookings(
        self,
        room_id: int,
        status: Optional[str] = None
    ) -> List[Booking]:
        """Retorna todas as reservas de um quarto."""
        queryset = self.model.objects.filter(room_id=room_id)
        if status:
            queryset = queryset.filter(status=status)
        return list(queryset.select_related('user'))
    
    def check_room_availability(
        self,
        room_id: int,
        data_checkin: date,
        data_checkout: date,
        exclude_booking_id: Optional[int] = None
    ) -> bool:
        """
        Verifica se o quarto está disponível no período.
        
        Retorna True se disponível, False se já tem reserva.
        """
        # Buscar reservas ativas (não canceladas) que se sobrepõem ao período
        queryset = self.model.objects.filter(
            room_id=room_id,
            status__in=['pending', 'confirmed', 'checked_in']
        ).filter(
            # Condição: reservas que se sobrepõem
            # Caso 1: reserva começa antes ou no mesmo dia e termina depois do checkin
            # Caso 2: reserva começa antes do checkout e termina depois ou no mesmo dia
            Q(data_checkin__lt=data_checkout, data_checkout__gt=data_checkin)
        )
        
        if exclude_booking_id:
            queryset = queryset.exclude(id=exclude_booking_id)
        
        return not queryset.exists()
    
    def get_bookings_to_release(self) -> List[Booking]:
        """
        Retorna reservas que devem ser liberadas/canceladas:
        - Status 'pending' com data de check-in passada
        """
        hoje = timezone.now().date()
        
        return list(
            self.model.objects.filter(
                status='pending',
                data_checkin__lt=hoje
            ).select_related('room', 'room__hotel', 'user')
        )
    
    def get_bookings_by_date_range(
        self,
        data_inicio: date,
        data_fim: date,
        hotel_id: Optional[int] = None
    ) -> List[Booking]:
        """Retorna reservas em um período."""
        queryset = self.model.objects.filter(
            Q(data_checkin__range=[data_inicio, data_fim]) |
            Q(data_checkout__range=[data_inicio, data_fim])
        )
        
        if hotel_id:
            queryset = queryset.filter(room__hotel_id=hotel_id)
        
        return list(queryset.select_related('room', 'room__hotel', 'user'))
    
    def get_hotel_bookings(
        self,
        hotel_id: int,
        status: Optional[str] = None
    ) -> List[Booking]:
        """Retorna todas as reservas de um hotel."""
        queryset = self.model.objects.filter(room__hotel_id=hotel_id)
        if status:
            queryset = queryset.filter(status=status)
        return list(queryset.select_related('room', 'user'))
