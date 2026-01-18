"""
Views para operações de Booking.
"""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from reserveme.permissions import IsStaffOrAdmin
from reserveme.serializers import (
    BookingSerializer,
    BookingCreateSerializer,
    BookingListSerializer
)
from reserveme.services.booking_service import (
    BookingService,
    BookingNotFoundError,
    RoomNotAvailableError,
    InvalidBookingError
)
from reserveme.repositories.booking_repository import BookingRepository
from reserveme.repositories.room_repository import RoomRepository
from core.utils.helpers import send_template_email_async

logger = logging.getLogger(__name__)


class BookingListCreateAPIView(APIView):
    """
    GET: Lista reservas
        - Customer: vê apenas suas próprias reservas
        - Staff/Admin: vê todas as reservas (pode filtrar por ?user_id=X)
        - Filtros: ?status=pending|confirmed|checked_in|checked_out|cancelled
                   ?user_id=X (apenas staff/admin)
    POST: Cria uma nova reserva
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Lista reservas.
        
        - Customer: vê apenas suas próprias reservas
        - Staff/Admin: vê todas as reservas (pode filtrar por user_id)
        """
        booking_repository = BookingRepository()
        room_repository = RoomRepository()
        booking_service = BookingService(booking_repository, room_repository)
        
        # Staff/Admin vê todas as reservas
        if request.user.is_staff_member:
            # Pode filtrar por usuário específico se fornecido
            user_id = request.query_params.get('user_id')
            if user_id:
                bookings = booking_service.list_user_bookings(int(user_id), request.query_params.get('status'))
            else:
                # Lista todas as reservas (incluindo canceladas e concluídas)
                bookings = booking_service.list_all_bookings(request.query_params.get('status'))
        else:
            # Customer vê apenas suas próprias reservas
            booking_status = request.query_params.get('status')
            bookings = booking_service.list_user_bookings(request.user.id, booking_status)
        
        serializer = BookingListSerializer(bookings, many=True)
        
        return Response({
            'bookings': serializer.data,
            'count': len(bookings)
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Cria uma nova reserva."""
        serializer = BookingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        booking_repository = BookingRepository()
        room_repository = RoomRepository()
        booking_service = BookingService(booking_repository, room_repository)
        
        # Adicionar usuário autenticado
        booking_data = serializer.validated_data
        booking_data['user'] = request.user
        
        try:
            booking = booking_service.create_booking(booking_data)
            
            # Enviar email de confirmação assíncronamente
            send_template_email_async(
                subject=f'Confirmação de Reserva - {booking.hotel.nome}',
                template_name='emails/booking_confirmation.html',
                context={
                    'user_name': request.user.get_full_name(),
                    'booking': booking,
                    'hotel': booking.hotel,
                    'room': booking.room,
                },
                recipient_list=[request.user.email]
            )
            
            response_serializer = BookingSerializer(booking)
            
            logger.info(
                f"Reserva criada: {booking.codigo_reserva} - {request.user.email}"
            )
            
            return Response({
                'message': 'Reserva criada com sucesso! Você receberá um email de confirmação.',
                'booking': response_serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except RoomNotAvailableError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except InvalidBookingError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class BookingDetailAPIView(APIView):
    """
    GET: Obtém detalhes de uma reserva
    DELETE: Cancela uma reserva
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, booking_id):
        """Obtém detalhes de uma reserva."""
        booking_repository = BookingRepository()
        room_repository = RoomRepository()
        booking_service = BookingService(booking_repository, room_repository)
        
        try:
            booking = booking_service.get_booking(booking_id)
            
            # Apenas o dono da reserva ou staff podem ver
            if booking.user_id != request.user.id and not request.user.is_staff_member:
                return Response({
                    'error': 'Você não tem permissão para ver esta reserva.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            serializer = BookingSerializer(booking)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except BookingNotFoundError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, booking_id):
        """Cancela uma reserva."""
        booking_repository = BookingRepository()
        room_repository = RoomRepository()
        booking_service = BookingService(booking_repository, room_repository)
        
        try:
            # Staff pode cancelar qualquer reserva
            user_id = None if request.user.is_staff_member else request.user.id
            
            booking = booking_service.cancel_booking(booking_id, user_id)
            
            # Enviar email de cancelamento
            send_template_email_async(
                subject=f'Reserva Cancelada - {booking.hotel.nome}',
                template_name='emails/booking_cancellation.html',
                context={
                    'user_name': booking.user.get_full_name(),
                    'booking': booking,
                },
                recipient_list=[booking.user.email]
            )
            
            logger.info(
                f"Reserva cancelada: {booking.codigo_reserva} - {request.user.email}"
            )
            
            return Response({
                'message': 'Reserva cancelada com sucesso!'
            }, status=status.HTTP_200_OK)
            
        except BookingNotFoundError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        except InvalidBookingError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class BookingConfirmAPIView(APIView):
    """
    POST: Confirma uma reserva (apenas staff/admin)
    """
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]
    
    def post(self, request, booking_id):
        """Confirma uma reserva."""
        booking_repository = BookingRepository()
        room_repository = RoomRepository()
        booking_service = BookingService(booking_repository, room_repository)
        
        try:
            booking = booking_service.confirm_booking(booking_id)
            
            # Enviar email de confirmação
            send_template_email_async(
                subject=f'Reserva Confirmada - {booking.hotel.nome}',
                template_name='emails/booking_confirmed.html',
                context={
                    'user_name': booking.user.get_full_name(),
                    'booking': booking,
                    'hotel': booking.hotel,
                    'room': booking.room,
                },
                recipient_list=[booking.user.email]
            )
            
            serializer = BookingSerializer(booking)
            
            logger.info(
                f"Reserva confirmada por {request.user.email}: {booking.codigo_reserva}"
            )
            
            return Response({
                'message': 'Reserva confirmada com sucesso!',
                'booking': serializer.data
            }, status=status.HTTP_200_OK)
            
        except BookingNotFoundError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        except InvalidBookingError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class BookingCheckinAPIView(APIView):
    """
    POST: Realiza check-in (apenas staff/admin)
    """
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]
    
    def post(self, request, booking_id):
        """Realiza check-in."""
        booking_repository = BookingRepository()
        room_repository = RoomRepository()
        booking_service = BookingService(booking_repository, room_repository)
        
        try:
            booking = booking_service.checkin(booking_id)
            
            serializer = BookingSerializer(booking)
            
            logger.info(
                f"Check-in realizado por {request.user.email}: {booking.codigo_reserva}"
            )
            
            return Response({
                'message': 'Check-in realizado com sucesso!',
                'booking': serializer.data
            }, status=status.HTTP_200_OK)
            
        except BookingNotFoundError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        except InvalidBookingError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class BookingCheckoutAPIView(APIView):
    """
    POST: Realiza check-out (apenas staff/admin)
    """
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]
    
    def post(self, request, booking_id):
        """Realiza check-out."""
        booking_repository = BookingRepository()
        room_repository = RoomRepository()
        booking_service = BookingService(booking_repository, room_repository)
        
        try:
            booking = booking_service.checkout(booking_id)
            
            serializer = BookingSerializer(booking)
            
            logger.info(
                f"Check-out realizado por {request.user.email}: {booking.codigo_reserva}"
            )
            
            return Response({
                'message': 'Check-out realizado com sucesso!',
                'booking': serializer.data
            }, status=status.HTTP_200_OK)
            
        except BookingNotFoundError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        except InvalidBookingError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class HotelBookingsAPIView(APIView):
    """
    GET: Lista todas as reservas de um hotel (apenas staff/admin)
    """
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]
    
    def get(self, request, hotel_id):
        """Lista reservas de um hotel."""
        booking_repository = BookingRepository()
        room_repository = RoomRepository()
        booking_service = BookingService(booking_repository, room_repository)
        
        booking_status = request.query_params.get('status')
        
        bookings = booking_service.list_hotel_bookings(hotel_id, booking_status)
        
        serializer = BookingListSerializer(bookings, many=True)
        
        return Response({
            'bookings': serializer.data,
            'count': len(bookings)
        }, status=status.HTTP_200_OK)
