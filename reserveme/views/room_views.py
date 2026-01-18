"""
Views para operações de Room.
"""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
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

logger = logging.getLogger(__name__)


class RoomListCreateAPIView(APIView):
    """
    GET: Lista todos os quartos (público para ativos, staff/admin vê todos)
    POST: Cria um novo quarto (apenas staff/admin)
    """
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsStaffOrAdmin()]
        return []
    
    def get(self, request):
        """Lista quartos."""
        room_repository = RoomRepository()
        room_service = RoomService(room_repository)
        
        # Filtros opcionais
        hotel_id = request.query_params.get('hotel_id')
        tipo = request.query_params.get('tipo')
        
        # Staff/Admin vê todos, outros apenas ativos
        if request.user.is_authenticated and request.user.is_staff_member:
            rooms = room_service.list_rooms(hotel_id=hotel_id)
        else:
            rooms = room_service.list_active_rooms(hotel_id=hotel_id)
        
        # Aplicar filtros adicionais
        if tipo:
            rooms = [r for r in rooms if r.tipo == tipo]
        
        serializer = RoomSerializer(rooms, many=True)
        
        logger.info(f"Listagem de quartos: {len(rooms)} quartos retornados")
        
        return Response({
            'rooms': serializer.data,
            'count': len(rooms)
        }, status=status.HTTP_200_OK)
    
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
    """
    GET: Obtém detalhes de um quarto (público para ativos)
    PUT/PATCH: Atualiza um quarto (apenas staff/admin)
    DELETE: Desativa um quarto (apenas staff/admin)
    """
    
    def get_permissions(self):
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
