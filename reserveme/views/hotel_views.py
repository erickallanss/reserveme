"""Views para operações de Hotel."""
import logging
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from reserveme.permissions import IsAdmin, IsStaffOrAdmin
from reserveme.serializers import (
    HotelSerializer,
    HotelCreateSerializer,
    HotelUpdateSerializer
)
from reserveme.services.hotel_service import (
    HotelService,
    HotelAlreadyExistsError,
    HotelNotFoundError
)
from reserveme.repositories.hotel_repository import HotelRepository
from reserveme.cache_utils import get_cache_key

logger = logging.getLogger(__name__)


class HotelListCreateAPIView(APIView):
    """
    GET: Lista todos os hotéis (público)
    POST: Cria um novo hotel (apenas admin)
    """
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdmin()]
        return []
    
    def get(self, request):
        """Lista hotéis com paginação e cache."""
        from rest_framework.pagination import PageNumberPagination
        from reserveme.models import Hotel
        
        # Chave de cache baseada no usuário e filtros
        is_admin = request.user.is_authenticated and request.user.is_admin
        cache_key = get_cache_key('hotels', 'list', admin=is_admin)
        
        # Tentar obter do cache
        cached_response = cache.get(cache_key)
        if cached_response:
            logger.debug(f"Cache hit: {cache_key}")
            return Response(cached_response)
        
        hotel_repository = HotelRepository()
        hotel_service = HotelService(hotel_repository)
        
        # Base queryset
        if not request.user.is_authenticated or not request.user.is_admin:
            queryset = Hotel.objects.filter(is_active=True)
        else:
            queryset = Hotel.objects.all()
        
        queryset = queryset.order_by('nome')
        
        # Paginação
        paginator = PageNumberPagination()
        paginator.page_size = int(request.query_params.get('page_size', 20))
        page = paginator.paginate_queryset(queryset, request)
        
        serializer = HotelSerializer(page, many=True)
        response_data = paginator.get_paginated_response(serializer.data).data
        
        # Salvar no cache (5 minutos)
        cache.set(cache_key, response_data, 300)
        logger.debug(f"Cache set: {cache_key}")
        
        logger.info(f"Listagem de hotéis: {len(queryset)} hotéis encontrados")
        
        return Response(response_data)
    
    def post(self, request):
        """Cria um novo hotel."""
        serializer = HotelCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        hotel_repository = HotelRepository()
        hotel_service = HotelService(hotel_repository)
        
        try:
            hotel = hotel_service.create_hotel(serializer.validated_data)
            
            # Cache será invalidado automaticamente via signal
            
            response_serializer = HotelSerializer(hotel)
            
            logger.info(f"Hotel criado por {request.user.email}: {hotel.nome}")
            
            return Response({
                'message': 'Hotel criado com sucesso!',
                'hotel': response_serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except HotelAlreadyExistsError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class HotelDetailAPIView(APIView):
    """
    GET: Obtém detalhes de um hotel (público)
    PUT/PATCH: Atualiza um hotel (apenas admin)
    DELETE: Desativa um hotel (apenas admin)
    """
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [IsAuthenticated(), IsAdmin()]
    
    def get(self, request, hotel_id):
        """Obtém detalhes de um hotel com cache."""
        cache_key = get_cache_key('hotel', hotel_id)
        
        # Tentar obter do cache
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.debug(f"Cache hit: {cache_key}")
            return Response(cached_data, status=status.HTTP_200_OK)
        
        hotel_repository = HotelRepository()
        hotel_service = HotelService(hotel_repository)
        
        try:
            hotel = hotel_service.get_hotel(hotel_id)
            
            # Se não for admin e hotel estiver inativo, não mostrar
            if not hotel.is_active and (not request.user.is_authenticated or not request.user.is_admin):
                return Response({
                    'error': 'Hotel não encontrado.'
                }, status=status.HTTP_404_NOT_FOUND)
            
            serializer = HotelSerializer(hotel)
            response_data = serializer.data
            
            # Salvar no cache (10 minutos para detalhes)
            cache.set(cache_key, response_data, 600)
            logger.debug(f"Cache set: {cache_key}")
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except HotelNotFoundError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, hotel_id):
        """Atualiza completamente um hotel."""
        return self._update_hotel(request, hotel_id, partial=False)
    
    def patch(self, request, hotel_id):
        """Atualiza parcialmente um hotel."""
        return self._update_hotel(request, hotel_id, partial=True)
    
    def _update_hotel(self, request, hotel_id, partial=False):
        """Método auxiliar para atualização."""
        hotel_repository = HotelRepository()
        hotel_service = HotelService(hotel_repository)
        
        try:
            hotel = hotel_service.get_hotel(hotel_id)
            
            serializer = HotelUpdateSerializer(
                hotel,
                data=request.data,
                partial=partial
            )
            serializer.is_valid(raise_exception=True)
            
            updated_hotel = hotel_service.update_hotel(
                hotel_id,
                serializer.validated_data
            )
            
            response_serializer = HotelSerializer(updated_hotel)
            
            logger.info(f"Hotel atualizado por {request.user.email}: {updated_hotel.nome}")
            
            return Response({
                'message': 'Hotel atualizado com sucesso!',
                'hotel': response_serializer.data
            }, status=status.HTTP_200_OK)
            
        except HotelNotFoundError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        except HotelAlreadyExistsError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, hotel_id):
        """Desativa um hotel (soft delete)."""
        hotel_repository = HotelRepository()
        hotel_service = HotelService(hotel_repository)
        
        try:
            hotel_service.delete_hotel(hotel_id)
            
            logger.info(f"Hotel desativado por {request.user.email}: ID {hotel_id}")
            
            return Response({
                'message': 'Hotel desativado com sucesso!'
            }, status=status.HTTP_200_OK)
            
        except HotelNotFoundError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
