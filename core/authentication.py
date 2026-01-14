"""
Custom JWT Authentication com suporte a HTTP-only cookies.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django.conf import settings


class JWTCookieAuthentication(JWTAuthentication):
    """
    Extensão do JWTAuthentication para suportar tokens via cookies HTTP-only.
    
    Tenta ler o token do cookie primeiro, se não encontrar, tenta o header Authorization.
    """
    
    def authenticate(self, request):
        """
        Tenta autenticar usando cookie primeiro, depois header.
        """
        # Tentar obter token do cookie HTTP-only
        cookie_token = request.COOKIES.get(settings.SIMPLE_JWT_COOKIE_NAME)
        
        if cookie_token:
            try:
                validated_token = self.get_validated_token(cookie_token)
                return self.get_user(validated_token), validated_token
            except InvalidToken:
                pass
        
        # Se não encontrou no cookie, tentar o header Authorization (fallback)
        return super().authenticate(request)
