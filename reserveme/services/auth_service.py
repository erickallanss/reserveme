"""
Service para operações de autenticação.
"""
from typing import Dict, Any, Optional, Tuple
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.crypto import get_random_string
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed, ValidationError, PermissionDenied
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
            is_approved=False,
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
            raise AuthenticationFailed(
                'Email ou senha incorretos.'
            )
        
        # Verificar senha
        if not user.check_password(password):
            raise AuthenticationFailed(
                'Email ou senha incorretos.'
            )
        
        # Verificar se pode fazer login
        if not user.can_login():
            if not user.email_verified:
                raise PermissionDenied(
                    'Por favor, verifique seu email antes de fazer login.'
                )
            if not user.is_approved:
                raise PermissionDenied(
                    'Sua conta está pendente de aprovação por um administrador.'
                )
            if not user.is_active:
                raise PermissionDenied(
                    'Sua conta está inativa. Entre em contato com o suporte.'
                )
        
        # Gerar tokens JWT
        tokens = self._generate_tokens(user)
        
        return user, tokens
    
    def verify_email(self, token: str) -> User:
        """
        Verifica email do usuário usando token.
        
        Args:
            token: Token de verificação
            
        Returns:
            User verificado
            
        Raises:
            ValidationError: Se token inválido
        """
        user = self.repository.get_by_verification_token(token)
        
        if not user:
            raise ValidationError('Token de verificação inválido ou expirado.')
        
        # Marcar email como verificado
        user.email_verified = True
        user.email_verification_token = ''
        user.save(update_fields=['email_verified', 'email_verification_token'])
        
        # Enviar email para admin notificando novo usuário para aprovação
        self._send_admin_approval_notification(user)
        
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
                raise AuthenticationFailed('Usuário não autorizado.')
            
            return {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        except Exception:
            raise AuthenticationFailed('Token inválido ou expirado.')
    
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
    
    def approve_user(self, user_id: int, approved_by: User) -> User:
        """
        Aprova usuário manualmente (apenas admins).
        
        Args:
            user_id: ID do usuário a aprovar
            approved_by: Usuário admin que está aprovando
            
        Returns:
            User aprovado
            
        Raises:
            PermissionDenied: Se quem aprova não é admin
            ValidationError: Se usuário não encontrado
        """
        if not approved_by.is_admin:
            raise PermissionDenied('Apenas administradores podem aprovar usuários.')
        
        user = self.repository.get_by_id(user_id)
        if not user:
            raise ValidationError('Usuário não encontrado.')
        
        if not user.email_verified:
            raise ValidationError('Usuário precisa verificar o email primeiro.')
        
        user.is_approved = True
        user.save(update_fields=['is_approved'])
        
        # Enviar email notificando aprovação
        self._send_approval_confirmation_email(user)
        
        return user
    
    def _generate_tokens(self, user: User) -> Dict[str, str]:
        """Gera tokens JWT para o usuário."""
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
    
    def _send_admin_approval_notification(self, user: User) -> None:
        """Notifica admins sobre novo usuário para aprovação."""
        # Buscar admins
        admins = self.repository.get_by_role('admin')
        admin_emails = [admin.email for admin in admins if admin.email]
        
        if admin_emails:
            send_template_email_async(
                subject=f'Novo Usuário Aguardando Aprovação - {user.email}',
                template_name='emails/admin_new_user.html',
                context={
                    'user': user,
                    'admin_panel_link': 'http://localhost:8000/admin/reserveme/user/',
                },
                recipient_list=admin_emails
            )
    
    def _send_approval_confirmation_email(self, user: User) -> None:
        """Envia email confirmando aprovação da conta."""
        send_template_email_async(
            subject='Sua conta foi aprovada! - ReserveMe',
            template_name='emails/account_approved.html',
            context={
                'user_name': user.first_name or user.username,
                'login_link': 'http://localhost:3000/login',
            },
            recipient_list=[user.email]
        )
