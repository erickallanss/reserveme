"""
Views para operações de Room.
"""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from reserveme.permissions import IsAdmin, IsStaffOrAdmin
from reserveme.serializers import (
    RoomSerializer,
    RoomCreateSerializer,
    RoomUpdateSerializer
)
from reserveme.services.room_service import (
    RoomService,
    RoomNotFoundError,
    RoomAlreadyExistsError
)
from reserveme.repositories.room_repository import RoomRepository
from reserveme.filters import RoomFilter

logger = logging.getLogger(__name__)


class RoomListCreateAPIView(APIView):
    """View para listar e criar quartos.
    
    GET: Lista quartos com paginação e filtros.
        - Público: vê apenas quartos ativos
        - Staff/Admin: vê todos os quartos
    POST: Cria novo quarto (requer autenticação staff/admin).
    """
    
    def get_permissions(self):
        """Define permissões por método HTTP."""
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsStaffOrAdmin()]
        return []
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RoomFilter
    search_fields = ['numero', 'descricao']
    ordering_fields = ['preco_diaria', 'capacidade', 'numero', 'created_at']
    ordering = ['numero']
    
    def get(self, request):
        """Lista quartos com paginação e filtros."""
        from rest_framework.pagination import PageNumberPagination
        from django.db.models import Q
        
        room_repository = RoomRepository()
        room_service = RoomService(room_repository)
        
        # Base queryset
        if request.user.is_authenticated and request.user.is_staff_member:
            from reserveme.models import Room
            queryset = Room.objects.all().select_related('hotel')
        else:
            from reserveme.models import Room
            queryset = Room.objects.filter(is_active=True).select_related('hotel')
        
        # Aplicar filtros
        filterset = RoomFilter(request.query_params, queryset=queryset)
        queryset = filterset.qs
        
        # Aplicar busca
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(numero__icontains=search) |
                Q(descricao__icontains=search)
            )
        
        # Aplicar ordenação
        ordering = request.query_params.get('ordering', 'numero')
        queryset = queryset.order_by(ordering)
        
        # Paginação
        paginator = PageNumberPagination()
        paginator.page_size = int(request.query_params.get('page_size', 20))
        page = paginator.paginate_queryset(queryset, request)
        
        serializer = RoomSerializer(page, many=True)
        
        logger.info(f"Listagem de quartos: {len(queryset)} quartos encontrados")
        
        return paginator.get_paginated_response(serializer.data)
    
    def post(self, request):
        """Cria um novo quarto."""
        serializer = RoomCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        room_repository = RoomRepository()
        room_service = RoomService(room_repository)
        
        try:
            room = room_service.create_room(serializer.validated_data)
            
            response_serializer = RoomSerializer(room)
            
            logger.info(
                f"Quarto criado por {request.user.email}: "
                f"{room.hotel.nome} - {room.numero}"
            )
            
            return Response({
                'message': 'Quarto criado com sucesso!',
                'room': response_serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except RoomAlreadyExistsError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class RoomDetailAPIView(APIView):
    """View para detalhes, atualização e desativação de quarto.
    
    GET: Obtém detalhes de um quarto (público para ativos).
    PUT/PATCH: Atualiza quarto (requer autenticação staff/admin).
    DELETE: Desativa quarto (requer autenticação staff/admin).
    """
    
    def get_permissions(self):
        """Define permissões por método HTTP."""
        if self.request.method == 'GET':
            return []
        return [IsAuthenticated(), IsStaffOrAdmin()]
    
    def get(self, request, room_id):
        """Obtém detalhes de um quarto."""
        room_repository = RoomRepository()
        room_service = RoomService(room_repository)
        
        try:
            room = room_service.get_room(room_id)
            
            # Se não for staff e quarto estiver inativo, não mostrar
            if not room.is_active and (
                not request.user.is_authenticated or 
                not request.user.is_staff_member
            ):
                return Response({
                    'error': 'Quarto não encontrado.'
                }, status=status.HTTP_404_NOT_FOUND)
            
            serializer = RoomSerializer(room)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except RoomNotFoundError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, room_id):
        """Atualiza completamente um quarto."""
        return self._update_room(request, room_id, partial=False)
    
    def patch(self, request, room_id):
        """Atualiza parcialmente um quarto."""
        return self._update_room(request, room_id, partial=True)
    
    def _update_room(self, request, room_id, partial=False):
        """Método auxiliar para atualização."""
        room_repository = RoomRepository()
        room_service = RoomService(room_repository)
        
        try:
            room = room_service.get_room(room_id)
            
            serializer = RoomUpdateSerializer(
                room,
                data=request.data,
                partial=partial
            )
            serializer.is_valid(raise_exception=True)
            
            updated_room = room_service.update_room(
                room_id,
                serializer.validated_data
            )
            
            response_serializer = RoomSerializer(updated_room)
            
            logger.info(
                f"Quarto atualizado por {request.user.email}: "
                f"{updated_room.hotel.nome} - {updated_room.numero}"
            )
            
            return Response({
                'message': 'Quarto atualizado com sucesso!',
                'room': response_serializer.data
            }, status=status.HTTP_200_OK)
            
        except RoomNotFoundError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        except RoomAlreadyExistsError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, room_id):
        """Desativa um quarto (soft delete)."""
        room_repository = RoomRepository()
        room_service = RoomService(room_repository)
        
        try:
            room_service.delete_room(room_id)
            
            logger.info(
                f"Quarto desativado por {request.user.email}: ID {room_id}"
            )
            
            return Response({
                'message': 'Quarto desativado com sucesso!'
            }, status=status.HTTP_200_OK)
            
        except RoomNotFoundError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
