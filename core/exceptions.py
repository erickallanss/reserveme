"""
Exceções customizadas da aplicação.
"""
from rest_framework.exceptions import APIException
from rest_framework import status


class BusinessLogicError(APIException):
    """
    Exceção base para erros de lógica de negócio.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Erro na lógica de negócio.'
    default_code = 'business_logic_error'


class EmailNotVerifiedError(APIException):
    """
    Exceção lançada quando o email não foi verificado.
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Por favor, verifique seu email para confirmar o registro antes de fazer login.'
    default_code = 'email_not_verified'


class AccountInactiveError(APIException):
    """
    Exceção lançada quando a conta está inativa.
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Sua conta está inativa. Entre em contato com o suporte.'
    default_code = 'account_inactive'


class InvalidCredentialsError(APIException):
    """
    Exceção lançada quando as credenciais são inválidas.
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Email ou senha incorretos.'
    default_code = 'invalid_credentials'


class InvalidTokenError(APIException):
    """
    Exceção lançada quando o token é inválido ou expirado.
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Token inválido ou expirado.'
    default_code = 'invalid_token'


class TokenNotFoundError(APIException):
    """
    Exceção lançada quando o token não é encontrado.
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Token não encontrado.'
    default_code = 'token_not_found'


class EmailAlreadyExistsError(BusinessLogicError):
    """
    Exceção lançada quando o email já existe.
    """
    default_detail = 'Este email já está cadastrado.'
    default_code = 'email_already_exists'


class UsernameAlreadyExistsError(BusinessLogicError):
    """
    Exceção lançada quando o username já existe.
    """
    default_detail = 'Este nome de usuário já está em uso.'
    default_code = 'username_already_exists'


class UserNotFoundError(APIException):
    """
    Exceção lançada quando o usuário não é encontrado.
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Usuário não encontrado.'
    default_code = 'user_not_found'


class InvalidVerificationTokenError(BusinessLogicError):
    """
    Exceção lançada quando o token de verificação é inválido.
    """
    default_detail = 'Token de verificação inválido ou expirado.'
    default_code = 'invalid_verification_token'
