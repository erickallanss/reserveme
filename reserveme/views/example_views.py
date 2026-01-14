"""
Views para ExampleModel.
Views são enxutas e apenas delegam para services.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from reserveme.serializers import (
    ExampleSerializer,
    ExampleCreateSerializer,
    ExampleUpdateSerializer,
)
from reserveme.containers import container


@extend_schema(
    tags=['Examples'],
    operation_id='list_examples',
    description='Lista todos os exemplos do usuário autenticado',
    responses={200: ExampleSerializer(many=True)},
)
@extend_schema(
    methods=['POST'],
    tags=['Examples'],
    operation_id='create_example',
    description='Cria um novo exemplo',
    request=ExampleCreateSerializer,
    responses={201: ExampleSerializer},
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def example_list_create(request: Request) -> Response:
    """
    Lista ou cria exemplos.
    
    GET: Lista todos os exemplos do usuário
    POST: Cria um novo exemplo
    """
    service = container.example_service()
    
    if request.method == 'GET':
        examples = service.list_examples(user=request.user)
        serializer = ExampleSerializer(examples, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ExampleCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                example = service.create_example(
                    user=request.user,
                    data=serializer.validated_data
                )
                response_serializer = ExampleSerializer(example)
                return Response(
                    response_serializer.data,
                    status=status.HTTP_201_CREATED
                )
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Examples'],
    operation_id='retrieve_example',
    description='Busca um exemplo específico',
    responses={200: ExampleSerializer, 404: None},
)
@extend_schema(
    methods=['PUT', 'PATCH'],
    tags=['Examples'],
    operation_id='update_example',
    description='Atualiza um exemplo',
    request=ExampleUpdateSerializer,
    responses={200: ExampleSerializer, 404: None, 403: None},
)
@extend_schema(
    methods=['DELETE'],
    tags=['Examples'],
    operation_id='delete_example',
    description='Deleta um exemplo',
    responses={204: None, 404: None, 403: None},
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def example_detail(request: Request, pk: int) -> Response:
    """
    Operações em um exemplo específico.
    
    GET: Busca um exemplo
    PUT/PATCH: Atualiza um exemplo
    DELETE: Deleta um exemplo
    """
    service = container.example_service()
    
    if request.method == 'GET':
        example = service.get_example(pk)
        if example:
            serializer = ExampleSerializer(example)
            return Response(serializer.data)
        return Response(
            {'error': 'Exemplo não encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    elif request.method in ['PUT', 'PATCH']:
        serializer = ExampleUpdateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                example = service.update_example(
                    example_id=pk,
                    data=serializer.validated_data,
                    user=request.user
                )
                if example:
                    response_serializer = ExampleSerializer(example)
                    return Response(response_serializer.data)
                return Response(
                    {'error': 'Exemplo não encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except PermissionError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_403_FORBIDDEN
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        try:
            deleted = service.delete_example(pk, user=request.user)
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': 'Exemplo não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
