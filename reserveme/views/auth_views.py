"""Views para autenticação."""
import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiResponse
from core.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    TokenNotFoundError,
    EmailNotVerifiedError,
    AccountInactiveError,
    InvalidVerificationTokenError,
)
from reserveme.containers import container
from reserveme.serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer,
    EmailVerificationSerializer,
)

logger = logging.getLogger(__name__)


class AuthMixin:
    @staticmethod
    def set_auth_cookies(response: Response, tokens: dict) -> Response:
        response.set_cookie(
            key=settings.SIMPLE_JWT_COOKIE_NAME,
            value=tokens['access'],
            max_age=int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
            httponly=settings.SIMPLE_JWT_COOKIE_HTTP_ONLY,
            secure=settings.SIMPLE_JWT_COOKIE_SECURE,
            samesite=settings.SIMPLE_JWT_COOKIE_SAMESITE,
            path=settings.SIMPLE_JWT_COOKIE_PATH,
        )
        
        if 'refresh' in tokens:
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
    
    @staticmethod
    def delete_auth_cookies(response: Response) -> Response:
        response.delete_cookie(
            key=settings.SIMPLE_JWT_COOKIE_NAME,
            path=settings.SIMPLE_JWT_COOKIE_PATH,
        )
        
        response.delete_cookie(
            key=settings.SIMPLE_JWT_REFRESH_COOKIE_NAME,
            path=settings.SIMPLE_JWT_COOKIE_PATH,
        )
        
        return response


class RegisterAPIView(APIView, AuthMixin):
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer
    
    @extend_schema(
        tags=['Authentication'],
        request=UserRegisterSerializer,
        responses={
            201: OpenApiResponse(description='Usuário registrado com sucesso'),
            400: OpenApiResponse(description='Dados inválidos'),
        }
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        if not serializer.is_valid():
            logger.warning(
                "Tentativa de registro com dados inválidos",
                extra={'errors': serializer.errors, 'ip': request.META.get('REMOTE_ADDR')}
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        auth_service = container.auth_service()
        
        try:
            user = auth_service.register_user(serializer.validated_data)
            
            logger.info(
                f"Novo usuário registrado: {user.email}",
                extra={'user_id': user.id, 'email': user.email}
            )
            
            return Response({
                'message': 'Usuário registrado com sucesso! Verifique seu email.',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        
        except ValidationError as e:
            logger.warning(
                f"Erro de validação no registro: {str(e)}",
                extra={'email': serializer.validated_data.get('email')}
            )
            raise
        except Exception as e:
            logger.error(
                f"Erro inesperado no registro: {str(e)}",
                extra={'email': serializer.validated_data.get('email')},
                exc_info=True
            )
            return Response({
                'error': 'Erro ao registrar usuário. Tente novamente mais tarde.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginAPIView(APIView, AuthMixin):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer
    
    @extend_schema(
        tags=['Authentication'],
        request=UserLoginSerializer,
        responses={
            200: OpenApiResponse(description='Login realizado com sucesso'),
            401: OpenApiResponse(description='Credenciais inválidas'),
            403: OpenApiResponse(description='Conta não verificada/aprovada'),
        }
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        if not serializer.is_valid():
            logger.warning(
                "Tentativa de login com dados inválidos",
                extra={'errors': serializer.errors, 'ip': request.META.get('REMOTE_ADDR')}
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        auth_service = container.auth_service()
        email = serializer.validated_data['email']
        
        try:
            user, tokens = auth_service.login(
                email=email,
                password=serializer.validated_data['password']
            )
            
            logger.info(
                f"Login realizado com sucesso: {user.email}",
                extra={'user_id': user.id, 'email': user.email}
            )
            
            response = Response({
                'message': 'Login realizado com sucesso',
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
            
            return self.set_auth_cookies(response, tokens)
        
        except (InvalidCredentialsError, EmailNotVerifiedError, 
                AccountInactiveError) as e:
            logger.warning(
                f"Falha no login para {email}: {e.detail}",
                extra={'email': email, 'error_type': type(e).__name__}
            )
            raise
        except Exception as e:
            logger.error(
                f"Erro inesperado no login: {str(e)}",
                extra={'email': email},
                exc_info=True
            )
            return Response({
                'error': 'Erro ao realizar login. Tente novamente mais tarde.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutAPIView(APIView, AuthMixin):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Authentication'],
        responses={
            200: OpenApiResponse(description='Logout realizado com sucesso'),
        }
    )
    def post(self, request):
        logger.info(
            f"Logout realizado: {request.user.email}",
            extra={'user_id': request.user.id, 'email': request.user.email}
        )
        
        response = Response({
            'message': 'Logout realizado com sucesso'
        }, status=status.HTTP_200_OK)
        
        return self.delete_auth_cookies(response)


class RefreshTokenAPIView(APIView, AuthMixin):
    """
    API para renovação de tokens.
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        tags=['Authentication'],
        responses={
            200: OpenApiResponse(description='Token renovado com sucesso'),
            401: OpenApiResponse(description='Token inválido'),
        }
    )
    def post(self, request):
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT_REFRESH_COOKIE_NAME)
        
        if not refresh_token:
            logger.warning(
                "Tentativa de refresh sem token",
                extra={'ip': request.META.get('REMOTE_ADDR')}
            )
            raise TokenNotFoundError('Refresh token não encontrado')
        
        auth_service = container.auth_service()
        
        try:
            tokens = auth_service.refresh_token(refresh_token)
            
            logger.info("Token renovado com sucesso")
            
            response = Response({
                'message': 'Token renovado com sucesso'
            }, status=status.HTTP_200_OK)
            
            return self.set_auth_cookies(response, tokens)
        
        except InvalidTokenError as e:
            logger.warning(
                f"Tentativa de refresh com token inválido: {e.detail}",
                extra={'ip': request.META.get('REMOTE_ADDR')}
            )
            raise
        except Exception as e:
            logger.error(
                f"Erro inesperado ao renovar token: {str(e)}",
                exc_info=True
            )
            return Response({
                'error': 'Erro ao renovar token. Tente novamente mais tarde.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyEmailAPIView(APIView, AuthMixin):
    permission_classes = [AllowAny]
    serializer_class = EmailVerificationSerializer
    
    @extend_schema(
        tags=['Authentication'],
        request=EmailVerificationSerializer,
        responses={
            200: OpenApiResponse(description='Email verificado com sucesso'),
            400: OpenApiResponse(description='Token inválido'),
        }
    )
    def post(self, request):
        """
        Verifica o email do usuário usando o token enviado por email.
        A conta é ativada automaticamente após a verificação.
        """
        serializer = self.serializer_class(data=request.data)
        
        if not serializer.is_valid():
            logger.warning(
                "Tentativa de verificação com dados inválidos",
                extra={'errors': serializer.errors}
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        auth_service = container.auth_service()
        token = serializer.validated_data['token']
        
        try:
            user = auth_service.verify_email(token)
            
            logger.info(
                f"Email verificado e conta ativada com sucesso: {user.email}",
                extra={'user_id': user.id, 'email': user.email, 'email_verified': user.email_verified}
            )
            
            return Response({
                'message': 'Email verificado com sucesso! Sua conta está ativa e você já pode fazer login.',
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        
        except InvalidVerificationTokenError as e:
            logger.warning(
                f"Tentativa de verificação com token inválido: {e.detail}",
                extra={'token_prefix': token[:10] if token else None}
            )
            raise
        except Exception as e:
            logger.error(
                f"Erro inesperado na verificação de email: {str(e)}",
                exc_info=True
            )
            return Response({
                'error': 'Erro ao verificar email. Tente novamente mais tarde.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileAPIView(APIView, AuthMixin):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Authentication'],
        responses={
            200: UserSerializer,
        }
    )
    def get(self, request):
        logger.debug(
            f"Consulta de perfil: {request.user.email}",
            extra={'user_id': request.user.id}
        )
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        tags=['Authentication'],
        request=UserUpdateSerializer,
        responses={
            200: UserSerializer,
            400: OpenApiResponse(description='Dados inválidos'),
        }
    )
    def patch(self, request):
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        
        if not serializer.is_valid():
            logger.warning(
                f"Tentativa de atualização com dados inválidos: {request.user.email}",
                extra={'user_id': request.user.id, 'errors': serializer.errors}
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        auth_service = container.auth_service()
        
        try:
            updated_user = auth_service.update_user(
                user=request.user,
                data=serializer.validated_data
            )
            
            logger.info(
                f"Perfil atualizado com sucesso: {updated_user.email}",
                extra={'user_id': updated_user.id, 'updated_fields': list(serializer.validated_data.keys())}
            )
            
            return Response({
                'message': 'Perfil atualizado com sucesso',
                'user': UserSerializer(updated_user).data
            }, status=status.HTTP_200_OK)
        
        except ValidationError as e:
            logger.warning(
                f"Erro de validação na atualização: {request.user.email}",
                extra={'user_id': request.user.id, 'error': str(e)}
            )
            raise
        except Exception as e:
            logger.error(
                f"Erro inesperado na atualização de perfil: {str(e)}",
                extra={'user_id': request.user.id},
                exc_info=True
            )
            return Response({
                'error': 'Erro ao atualizar perfil. Tente novamente mais tarde.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangePasswordAPIView(APIView, AuthMixin):
    """
    API para alteração de senha.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer
    
    @extend_schema(
        tags=['Authentication'],
        request=PasswordChangeSerializer,
        responses={
            200: OpenApiResponse(description='Senha alterada com sucesso'),
            400: OpenApiResponse(description='Dados inválidos'),
        }
    )
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            logger.warning(
                f"Tentativa de alteração de senha com dados inválidos: {request.user.email}",
                extra={'user_id': request.user.id, 'errors': serializer.errors}
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        auth_service = container.auth_service()
        
        try:
            auth_service.change_password(
                user=request.user,
                old_password=serializer.validated_data['old_password'],
                new_password=serializer.validated_data['new_password']
            )
            
            logger.info(
                f"Senha alterada com sucesso: {request.user.email}",
                extra={'user_id': request.user.id}
            )
            
            return Response({
                'message': 'Senha alterada com sucesso'
            }, status=status.HTTP_200_OK)
        
        except ValidationError as e:
            logger.warning(
                f"Erro ao alterar senha: {request.user.email}",
                extra={'user_id': request.user.id, 'error': str(e)}
            )
            raise
        except Exception as e:
            logger.error(
                f"Erro inesperado ao alterar senha: {str(e)}",
                extra={'user_id': request.user.id},
                exc_info=True
            )
            return Response({
                'error': 'Erro ao alterar senha. Tente novamente mais tarde.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
