"""
Service para operações de autenticação.
"""
from typing import Dict, Any, Optional, Tuple
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.crypto import get_random_string
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
from core.exceptions import (
    EmailNotVerifiedError,
    AccountInactiveError,
    InvalidCredentialsError,
    InvalidTokenError,
    InvalidVerificationTokenError,
    UserNotFoundError,
)
from core.utils.helpers import send_template_email_async
from ..repositories.user_repository import UserRepository

User = get_user_model()


class AuthService:
    """
    Service para lógica de autenticação.
    """
    
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    def register_user(self, data: Dict[str, Any]) -> User:
        """
        Registra novo usuário e envia email de verificação.
        
        Args:
            data: Dados do usuário já validados
            
        Returns:
            User criado
            
        Raises:
            ValidationError: Se dados inválidos
        """
        user_data = data.copy()
        password = user_data.pop('password', None)
        user_data.pop('password_confirm', None)
        
        verification_token = get_random_string(64)
        
        user = self.repository.create(
            **user_data,
            email_verification_token=verification_token,
            is_active=True,
            email_verified=False,
            role='customer'
        )
        
        if password:
            user.set_password(password)
            user.save(update_fields=['password'])
        
        self._send_verification_email(user, verification_token)
        
        return user
    
    def login(self, email: str, password: str) -> Tuple[User, Dict[str, str]]:
        """
        Autentica usuário e retorna tokens.
        
        Args:
            email: Email do usuário
            password: Senha do usuário
            
        Returns:
            Tupla (User, tokens_dict)
            
        Raises:
            AuthenticationFailed: Se credenciais inválidas ou conta não aprovada
        """
        # Buscar usuário
        user = self.repository.get_by_email(email)
        
        if not user:
            raise InvalidCredentialsError()
        
        # Verificar senha
        if not user.check_password(password):
            raise InvalidCredentialsError()
        
        # Verificar se pode fazer login
        if not user.can_login():
            if not user.email_verified:
                raise EmailNotVerifiedError()
            if not user.is_active:
                raise AccountInactiveError()
        
        # Gerar tokens JWT
        tokens = self._generate_tokens(user)
        
        return user, tokens
    
    def verify_email(self, token: str) -> User:
        """
        Verifica email do usuário usando token, ativando a conta para login.
        
        Args:
            token: Token de verificação
            
        Returns:
            User verificado
            
        Raises:
            InvalidVerificationTokenError: Se token inválido
        """
        user = self.repository.get_by_verification_token(token)
        
        if not user:
            raise InvalidVerificationTokenError()
        
        # Marcar email como verificado
        user.email_verified = True
        user.email_verification_token = ''
        user.save(update_fields=['email_verified', 'email_verification_token'])
        
        # Enviar email confirmando que a conta está ativa
        self._send_account_activated_email(user)
        
        return user
    
    def resend_verification_email(self, email: str) -> None:
        """
        Reenvia email de verificação.
        
        Args:
            email: Email do usuário
            
        Raises:
            ValidationError: Se usuário não encontrado ou já verificado
        """
        user = self.repository.get_by_email(email)
        
        if not user:
            raise ValidationError('Usuário não encontrado.')
        
        if user.email_verified:
            raise ValidationError('Email já verificado.')
        
        # Gerar novo token
        verification_token = get_random_string(64)
        user.email_verification_token = verification_token
        user.save(update_fields=['email_verification_token'])
        
        # Enviar email
        self._send_verification_email(user, verification_token)
    
    def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Gera novo access token a partir do refresh token.
        
        Args:
            refresh_token: Refresh token válido
            
        Returns:
            Dicionário com novos tokens
            
        Raises:
            AuthenticationFailed: Se refresh token inválido
        """
        try:
            refresh = RefreshToken(refresh_token)
            
            # Verificar se usuário ainda pode logar
            user = self.repository.get_by_id(refresh['user_id'])
            if not user or not user.can_login():
                raise InvalidTokenError('Usuário não autorizado.')
            
            return {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        except InvalidTokenError:
            raise
        except Exception:
            raise InvalidTokenError()
    
    def update_user(self, user: User, data: Dict[str, Any]) -> User:
        """
        Atualiza dados do usuário.
        
        Args:
            user: Usuário a ser atualizado
            data: Dados validados para atualização
            
        Returns:
            User atualizado
        """
        for field, value in data.items():
            setattr(user, field, value)
        
        user.save()
        return user
    
    def change_password(
        self, 
        user: User, 
        old_password: str, 
        new_password: str
    ) -> None:
        """
        Altera senha do usuário.
        
        Args:
            user: Usuário
            old_password: Senha antiga
            new_password: Nova senha
            
        Raises:
            ValidationError: Se senha antiga incorreta
        """
        if not user.check_password(old_password):
            raise ValidationError({'old_password': 'Senha atual incorreta.'})
        
        user.set_password(new_password)
        user.save(update_fields=['password'])
    
    def _generate_tokens(self, user: User) -> Dict[str, str]:
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
    
    def _send_verification_email(self, user: User, token: str) -> None:
        """Envia email de verificação (assíncrono)."""
        verification_link = f"http://localhost:3000/verify-email/{token}"
        
        send_template_email_async(
            subject='Verificação de Email - ReserveMe',
            template_name='emails/email_verification.html',
            context={
                'user_name': user.first_name or user.username,
                'verification_link': verification_link,
                'verification_token': token,
            },
            recipient_list=[user.email]
        )
    
    def _send_account_activated_email(self, user: User) -> None:
        send_template_email_async(
            subject='Sua conta foi ativada! - ReserveMe',
            template_name='emails/account_approved.html',
            context={
                'user_name': user.first_name or user.username,
                'login_link': 'http://localhost:3000/login',
            },
            recipient_list=[user.email]
        )
