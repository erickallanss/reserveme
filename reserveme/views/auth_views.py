"""
Views para autenticação com JWT via HTTP-only cookies.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiResponse
from reserveme.containers import container
from reserveme.serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer,
    EmailVerificationSerializer,
)


@extend_schema(
    tags=['Authentication'],
    request=UserRegisterSerializer,
    responses={
        201: OpenApiResponse(description='Usuário registrado com sucesso'),
        400: OpenApiResponse(description='Dados inválidos'),
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request: Request) -> Response:
    """
    Registra novo usuário no sistema.
    
    O usuário receberá um email para verificação e precisará de aprovação manual.
    """
    serializer = UserRegisterSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Obter service do container (DI)
    auth_service = container.auth_service()
    
    try:
        user = auth_service.register_user(serializer.validated_data)
        
        return Response({
            'message': 'Usuário registrado com sucesso! Verifique seu email.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Authentication'],
    request=UserLoginSerializer,
    responses={
        200: OpenApiResponse(description='Login realizado com sucesso'),
        401: OpenApiResponse(description='Credenciais inválidas'),
        403: OpenApiResponse(description='Conta não verificada/aprovada'),
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request: Request) -> Response:
    """
    Realiza login e retorna tokens JWT via HTTP-only cookies.
    
    Os tokens são armazenados em cookies seguros (HTTP-only, Secure em produção).
    """
    serializer = UserLoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    auth_service = container.auth_service()
    
    try:
        user, tokens = auth_service.login(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        # Criar response
        response = Response({
            'message': 'Login realizado com sucesso',
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
        
        # Configurar cookies HTTP-only
        response.set_cookie(
            key=settings.SIMPLE_JWT_COOKIE_NAME,
            value=tokens['access'],
            max_age=int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
            httponly=settings.SIMPLE_JWT_COOKIE_HTTP_ONLY,
            secure=settings.SIMPLE_JWT_COOKIE_SECURE,
            samesite=settings.SIMPLE_JWT_COOKIE_SAMESITE,
            path=settings.SIMPLE_JWT_COOKIE_PATH,
        )
        
        response.set_cookie(
            key=settings.SIMPLE_JWT_REFRESH_COOKIE_NAME,
            value=tokens['refresh'],
            max_age=int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()),
            httponly=settings.SIMPLE_JWT_COOKIE_HTTP_ONLY,
            secure=settings.SIMPLE_JWT_COOKIE_SECURE,
            samesite=settings.SIMPLE_JWT_COOKIE_SAMESITE,
            path=settings.SIMPLE_JWT_COOKIE_PATH,
        )
        
        return response
    
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_401_UNAUTHORIZED)


@extend_schema(
    tags=['Authentication'],
    responses={
        200: OpenApiResponse(description='Logout realizado com sucesso'),
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request: Request) -> Response:
    """
    Realiza logout removendo os cookies de autenticação.
    """
    response = Response({
        'message': 'Logout realizado com sucesso'
    }, status=status.HTTP_200_OK)
    
    # Remover cookies
    response.delete_cookie(
        key=settings.SIMPLE_JWT_COOKIE_NAME,
        path=settings.SIMPLE_JWT_COOKIE_PATH,
    )
    
    response.delete_cookie(
        key=settings.SIMPLE_JWT_REFRESH_COOKIE_NAME,
        path=settings.SIMPLE_JWT_COOKIE_PATH,
    )
    
    return response


@extend_schema(
    tags=['Authentication'],
    responses={
        200: OpenApiResponse(description='Token renovado com sucesso'),
        401: OpenApiResponse(description='Refresh token inválido'),
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request: Request) -> Response:
    """
    Renova o access token usando o refresh token do cookie.
    """
    refresh_token = request.COOKIES.get(settings.SIMPLE_JWT_REFRESH_COOKIE_NAME)
    
    if not refresh_token:
        return Response({
            'error': 'Refresh token não encontrado'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    auth_service = container.auth_service()
    
    try:
        tokens = auth_service.refresh_token(refresh_token)
        
        response = Response({
            'message': 'Token renovado com sucesso'
        }, status=status.HTTP_200_OK)
        
        # Atualizar access token cookie
        response.set_cookie(
            key=settings.SIMPLE_JWT_COOKIE_NAME,
            value=tokens['access'],
            max_age=int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
            httponly=settings.SIMPLE_JWT_COOKIE_HTTP_ONLY,
            secure=settings.SIMPLE_JWT_COOKIE_SECURE,
            samesite=settings.SIMPLE_JWT_COOKIE_SAMESITE,
            path=settings.SIMPLE_JWT_COOKIE_PATH,
        )
        
        # Atualizar refresh token cookie
        response.set_cookie(
            key=settings.SIMPLE_JWT_REFRESH_COOKIE_NAME,
            value=tokens['refresh'],
            max_age=int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()),
            httponly=settings.SIMPLE_JWT_COOKIE_HTTP_ONLY,
            secure=settings.SIMPLE_JWT_COOKIE_SECURE,
            samesite=settings.SIMPLE_JWT_COOKIE_SAMESITE,
            path=settings.SIMPLE_JWT_COOKIE_PATH,
        )
        
        return response
    
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_401_UNAUTHORIZED)


@extend_schema(
    tags=['Authentication'],
    request=EmailVerificationSerializer,
    responses={
        200: OpenApiResponse(description='Email verificado com sucesso'),
        400: OpenApiResponse(description='Token inválido'),
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request: Request) -> Response:
    """
    Verifica email do usuário usando token enviado por email.
    """
    serializer = EmailVerificationSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    auth_service = container.auth_service()
    
    try:
        user = auth_service.verify_email(serializer.validated_data['token'])
        
        return Response({
            'message': 'Email verificado com sucesso! Aguarde aprovação de um administrador.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Authentication'],
    responses={
        200: OpenApiResponse(description='Dados do usuário autenticado'),
        401: OpenApiResponse(description='Não autenticado'),
    }
)
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def me(request: Request) -> Response:
    """
    GET: Retorna dados do usuário autenticado.
    PATCH: Atualiza dados do perfil do usuário.
    """
    if request.method == 'GET':
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
    
    elif request.method == 'PATCH':
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        
        return Response({
            'message': 'Perfil atualizado com sucesso',
            'user': UserSerializer(request.user).data
        }, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Authentication'],
    request=PasswordChangeSerializer,
    responses={
        200: OpenApiResponse(description='Senha alterada com sucesso'),
        400: OpenApiResponse(description='Dados inválidos'),
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request: Request) -> Response:
    """
    Altera a senha do usuário autenticado.
    """
    serializer = PasswordChangeSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    auth_service = container.auth_service()
    
    try:
        auth_service.change_password(
            user=request.user,
            old_password=serializer.validated_data['old_password'],
            new_password=serializer.validated_data['new_password']
        )
        
        return Response({
            'message': 'Senha alterada com sucesso'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
