"""
Service para operações de Booking.
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import date
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from reserveme.models import Booking, Room, User
from reserveme.repositories.booking_repository import BookingRepository
from reserveme.repositories.room_repository import RoomRepository

logger = logging.getLogger(__name__)


class BookingNotFoundError(Exception):
    """Exceção quando reserva não é encontrada."""
    pass


class RoomNotAvailableError(Exception):
    """Exceção quando quarto não está disponível."""
    pass


class InvalidBookingError(Exception):
    """Exceção para validações de reserva."""
    pass


class BookingService:
    """Service para gerenciar lógica de negócio de Booking."""
    
    def __init__(
        self, 
        booking_repository: BookingRepository,
        room_repository: RoomRepository
    ):
        self.booking_repository = booking_repository
        self.room_repository = room_repository
    
    def validate_dates(self, data_checkin: date, data_checkout: date) -> None:
        """
        Valida as datas da reserva.
        
        Raises:
            InvalidBookingError: Se datas inválidas
        """
        hoje = timezone.now().date()
        
        if data_checkin < hoje:
            raise InvalidBookingError("Data de check-in não pode ser no passado.")
        
        if data_checkout <= data_checkin:
            raise InvalidBookingError(
                "Data de check-out deve ser posterior à data de check-in."
            )
    
    def calculate_total_price(
        self, 
        preco_diaria: Decimal, 
        numero_diarias: int
    ) -> Decimal:
        """Calcula o preço total da reserva."""
        return preco_diaria * numero_diarias
    
    def calculate_numero_diarias(self, data_checkin: date, data_checkout: date) -> int:
        """Calcula o número de diárias."""
        delta = data_checkout - data_checkin
        return delta.days
    
    @transaction.atomic
    def create_booking(self, data: Dict[str, Any]) -> Booking:
        """
        Cria uma nova reserva.
        
        Raises:
            InvalidBookingError: Se dados inválidos
            RoomNotAvailableError: Se quarto não disponível
        """
        room = data.get('room')
        user = data.get('user')
        data_checkin = data.get('data_checkin')
        data_checkout = data.get('data_checkout')
        numero_hospedes = data.get('numero_hospedes')
        
        # Validar datas
        self.validate_dates(data_checkin, data_checkout)
        
        # Validar capacidade
        if numero_hospedes > room.capacidade:
            raise InvalidBookingError(
                f"Número de hóspedes ({numero_hospedes}) excede a capacidade do quarto ({room.capacidade})."
            )
        
        # Verificar disponibilidade
        if not self.booking_repository.check_room_availability(
            room.id, data_checkin, data_checkout
        ):
            raise RoomNotAvailableError(
                "Quarto não disponível para o período selecionado."
            )
        
        # Calcular valores
        numero_diarias = self.calculate_numero_diarias(data_checkin, data_checkout)
        preco_diaria = room.preco_diaria
        preco_total = self.calculate_total_price(preco_diaria, numero_diarias)
        
        # Preparar dados da reserva
        booking_data = {
            'room': room,
            'user': user,
            'data_checkin': data_checkin,
            'data_checkout': data_checkout,
            'numero_hospedes': numero_hospedes,
            'numero_diarias': numero_diarias,
            'preco_diaria': preco_diaria,
            'preco_total': preco_total,
            'status': 'pending',
            'observacoes': data.get('observacoes', '')
        }
        
        booking = self.booking_repository.create(booking_data)
        logger.info(
            f"Reserva criada: {booking.codigo_reserva} - "
            f"{user.email} - {room.hotel.nome} Quarto {room.numero}"
        )
        
        return booking
    
    def get_booking(self, booking_id: int) -> Booking:
        """
        Busca reserva por ID.
        
        Raises:
            BookingNotFoundError: Se reserva não existe
        """
        booking = self.booking_repository.get_by_id(booking_id)
        if not booking:
            raise BookingNotFoundError(f"Reserva com ID {booking_id} não encontrada.")
        return booking
    
    def get_booking_by_codigo(self, codigo_reserva: str) -> Booking:
        """
        Busca reserva por código.
        
        Raises:
            BookingNotFoundError: Se reserva não existe
        """
        booking = self.booking_repository.get_by_codigo(codigo_reserva)
        if not booking:
            raise BookingNotFoundError(
                f"Reserva '{codigo_reserva}' não encontrada."
            )
        return booking
    
    def list_user_bookings(
        self, 
        user_id: int,
        status: Optional[str] = None
    ) -> List[Booking]:
        """Lista reservas de um usuário."""
        return self.booking_repository.get_user_bookings(user_id, status)
    
    def list_all_bookings(
        self,
        status: Optional[str] = None
    ) -> List[Booking]:
        """Lista todas as reservas (apenas para staff/admin)."""
        if status:
            return list(
                self.booking_repository.model.objects.filter(status=status)
                .select_related('room', 'room__hotel', 'user')
                .order_by('-created_at')
            )
        return list(
            self.booking_repository.model.objects.all()
            .select_related('room', 'room__hotel', 'user')
            .order_by('-created_at')
        )
    
    def list_hotel_bookings(
        self,
        hotel_id: int,
        status: Optional[str] = None
    ) -> List[Booking]:
        """Lista reservas de um hotel."""
        return self.booking_repository.get_hotel_bookings(hotel_id, status)
    
    @transaction.atomic
    def confirm_booking(self, booking_id: int) -> Booking:
        """
        Confirma uma reserva (apenas staff/admin).
        
        Raises:
            BookingNotFoundError: Se reserva não existe
            InvalidBookingError: Se reserva não pode ser confirmada
        """
        booking = self.get_booking(booking_id)
        
        if booking.status != 'pending':
            raise InvalidBookingError(
                f"Apenas reservas pendentes podem ser confirmadas. Status atual: {booking.status}"
            )
        
        updated_booking = self.booking_repository.update(
            booking_id, 
            {'status': 'confirmed'}
        )
        
        logger.info(f"Reserva confirmada: {booking.codigo_reserva}")
        return updated_booking
    
    @transaction.atomic
    def cancel_booking(self, booking_id: int, user_id: Optional[int] = None) -> Booking:
        """
        Cancela uma reserva.
        
        Raises:
            BookingNotFoundError: Se reserva não existe
            InvalidBookingError: Se reserva não pode ser cancelada
        """
        booking = self.get_booking(booking_id)
        
        if not booking.can_cancel:
            raise InvalidBookingError(
                f"Reserva não pode ser cancelada. Status atual: {booking.status}"
            )
        
        # Se user_id fornecido, verificar se é o dono da reserva
        if user_id and booking.user_id != user_id:
            raise InvalidBookingError("Você não tem permissão para cancelar esta reserva.")
        
        updated_booking = self.booking_repository.update(
            booking_id,
            {
                'status': 'cancelled',
                'cancelled_at': timezone.now()
            }
        )
        
        logger.info(f"Reserva cancelada: {booking.codigo_reserva}")
        return updated_booking
    
    @transaction.atomic
    def checkin(self, booking_id: int) -> Booking:
        """
        Realiza check-in (apenas staff/admin).
        
        Raises:
            BookingNotFoundError: Se reserva não existe
            InvalidBookingError: Se não pode fazer check-in
        """
        booking = self.get_booking(booking_id)
        
        if not booking.can_checkin:
            raise InvalidBookingError(
                f"Check-in não pode ser realizado. Status atual: {booking.status}"
            )
        
        updated_booking = self.booking_repository.update(
            booking_id,
            {
                'status': 'checked_in',
                'checked_in_at': timezone.now()
            }
        )
        
        logger.info(f"Check-in realizado: {booking.codigo_reserva}")
        return updated_booking
    
    @transaction.atomic
    def checkout(self, booking_id: int) -> Booking:
        """
        Realiza check-out (apenas staff/admin).
        
        Raises:
            BookingNotFoundError: Se reserva não existe
            InvalidBookingError: Se não pode fazer check-out
        """
        booking = self.get_booking(booking_id)
        
        if not booking.can_checkout:
            raise InvalidBookingError(
                f"Check-out não pode ser realizado. Status atual: {booking.status}"
            )
        
        updated_booking = self.booking_repository.update(
            booking_id,
            {
                'status': 'checked_out',
                'checked_out_at': timezone.now()
            }
        )
        
        logger.info(f"Check-out realizado: {booking.codigo_reserva}")
        return updated_booking
    
    def check_availability(
        self,
        room_id: int,
        data_checkin: date,
        data_checkout: date
    ) -> bool:
        """Verifica disponibilidade de um quarto."""
        self.validate_dates(data_checkin, data_checkout)
        return self.booking_repository.check_room_availability(
            room_id, data_checkin, data_checkout
        )
