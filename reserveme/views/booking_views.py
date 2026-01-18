"""Views para operações de Booking."""
import logging
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
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
from reserveme.filters import BookingFilter
from reserveme.cache_utils import get_cache_key, invalidate_booking_cache
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
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BookingFilter
    ordering_fields = ['created_at', 'data_checkin', 'data_checkout', 'preco_total']
    ordering = ['-created_at']
    
    def get(self, request):
        """Lista reservas com paginação, filtros e cache.
        
        - Customer: vê apenas suas próprias reservas
        - Staff/Admin: vê todas as reservas (pode filtrar por user_id)
        """
        from rest_framework.pagination import PageNumberPagination
        from reserveme.models import Booking
        from hashlib import md5
        
        # Gerar chave de cache baseada nos parâmetros
        params_str = str(sorted(request.query_params.items()))
        params_hash = md5(params_str.encode()).hexdigest()[:8]
        user_id = request.user.id if request.user.is_authenticated else None
        is_staff = request.user.is_staff_member if request.user.is_authenticated else False
        cache_key = get_cache_key('bookings', 'list', user=user_id, staff=is_staff, params=params_hash)
        
        # Tentar obter do cache (apenas para customers, staff pode ter dados mais dinâmicos)
        if not is_staff:
            cached_response = cache.get(cache_key)
            if cached_response:
                logger.debug(f"Cache hit: {cache_key}")
                return Response(cached_response)
        
        booking_repository = BookingRepository()
        room_repository = RoomRepository()
        booking_service = BookingService(booking_repository, room_repository)
        
        # Base queryset
        if request.user.is_staff_member:
            # Staff/Admin vê todas as reservas
            filter_user_id = request.query_params.get('user_id')
            if filter_user_id:
                queryset = Booking.objects.filter(user_id=filter_user_id).select_related('room', 'room__hotel', 'user')
            else:
                queryset = Booking.objects.all().select_related('room', 'room__hotel', 'user')
        else:
            # Customer vê apenas suas próprias reservas
            queryset = Booking.objects.filter(user_id=request.user.id).select_related('room', 'room__hotel', 'user')
        
        # Aplicar filtros
        filterset = BookingFilter(request.query_params, queryset=queryset)
        queryset = filterset.qs
        
        # Aplicar ordenação
        ordering = request.query_params.get('ordering', '-created_at')
        queryset = queryset.order_by(ordering)
        
        # Paginação
        paginator = PageNumberPagination()
        paginator.page_size = int(request.query_params.get('page_size', 20))
        page = paginator.paginate_queryset(queryset, request)
        
        serializer = BookingListSerializer(page, many=True)
        response_data = paginator.get_paginated_response(serializer.data).data
        
        # Salvar no cache apenas para customers (2 minutos)
        if not is_staff:
            cache.set(cache_key, response_data, 120)
            logger.debug(f"Cache set: {cache_key}")
        
        return Response(response_data)
    
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
            
            # Invalidar cache de reservas do usuário
            invalidate_booking_cache(user_id=request.user.id)
            
            # Enviar email de confirmação assíncronamente
            send_template_email_async(
                subject=f'Confirmação de Reserva - {booking.room.hotel.nome}',
                template_name='emails/booking_confirmation.html',
                context={
                    'user_name': request.user.get_full_name(),
                    'booking_id': booking.id,
                    'booking_code': booking.codigo_reserva,
                    'hotel_name': booking.room.hotel.nome,
                    'room_number': booking.room.numero,
                    'checkin_date': booking.data_checkin.strftime('%d/%m/%Y'),
                    'checkout_date': booking.data_checkout.strftime('%d/%m/%Y'),
                    'total_price': str(booking.preco_total),
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
            
            # Invalidar cache
            invalidate_booking_cache(booking_id=booking.id, user_id=booking.user_id)
            
            # Enviar email de cancelamento
            send_template_email_async(
                subject=f'Reserva Cancelada - {booking.room.hotel.nome}',
                template_name='emails/booking_cancellation.html',
                context={
                    'user_name': booking.user.get_full_name(),
                    'booking_code': booking.codigo_reserva,
                    'hotel_name': booking.room.hotel.nome,
                    'room_number': booking.room.numero,
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
    """View para confirmar reserva (staff/admin).
    
    POST: Confirma uma reserva pendente e envia email ao cliente.
    """
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]
    
    def post(self, request, booking_id):
        """Confirma uma reserva pendente.
        
        Args:
            request: Request HTTP.
            booking_id: ID da reserva.
            
        Returns:
            Response com dados da reserva confirmada.
        """
        booking_repository = BookingRepository()
        room_repository = RoomRepository()
        booking_service = BookingService(booking_repository, room_repository)
        
        try:
            booking = booking_service.confirm_booking(booking_id)
            
            # Invalidar cache
            invalidate_booking_cache(booking_id=booking.id, user_id=booking.user_id)
            
            # Enviar email de confirmação
            send_template_email_async(
                subject=f'Reserva Confirmada - {booking.room.hotel.nome}',
                template_name='emails/booking_confirmed.html',
                context={
                    'user_name': booking.user.get_full_name(),
                    'booking_code': booking.codigo_reserva,
                    'hotel_name': booking.room.hotel.nome,
                    'room_number': booking.room.numero,
                    'checkin_date': booking.data_checkin.strftime('%d/%m/%Y'),
                    'checkout_date': booking.data_checkout.strftime('%d/%m/%Y'),
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
    """View para realizar check-in (staff/admin).
    
    POST: Registra check-in de uma reserva confirmada.
    """
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]
    
    def post(self, request, booking_id):
        """Realiza check-in de uma reserva.
        
        Args:
            request: Request HTTP.
            booking_id: ID da reserva.
            
        Returns:
            Response com dados da reserva atualizada.
        """
        booking_repository = BookingRepository()
        room_repository = RoomRepository()
        booking_service = BookingService(booking_repository, room_repository)
        
        try:
            booking = booking_service.checkin(booking_id)
            
            # Invalidar cache
            invalidate_booking_cache(booking_id=booking.id, user_id=booking.user_id)
            
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
    """View para realizar check-out (staff/admin).
    
    POST: Registra check-out de uma reserva com check-in realizado.
    """
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]
    
    def post(self, request, booking_id):
        """Realiza check-out de uma reserva.
        
        Args:
            request: Request HTTP.
            booking_id: ID da reserva.
            
        Returns:
            Response com dados da reserva atualizada.
        """
        booking_repository = BookingRepository()
        room_repository = RoomRepository()
        booking_service = BookingService(booking_repository, room_repository)
        
        try:
            booking = booking_service.checkout(booking_id)
            
            # Invalidar cache
            invalidate_booking_cache(booking_id=booking.id, user_id=booking.user_id)
            
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
    """View para listar reservas de um hotel (staff/admin).
    
    GET: Lista todas as reservas de um hotel com paginação e filtros.
    """
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]
    
    def get(self, request, hotel_id):
        """Lista reservas de um hotel específico.
        
        Args:
            request: Request HTTP.
            hotel_id: ID do hotel.
            
        Returns:
            Response paginada com lista de reservas.
        """
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
