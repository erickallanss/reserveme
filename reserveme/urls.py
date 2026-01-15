"""
URLs do app reserveme.
"""
from django.urls import path
from reserveme.views.auth_views import (
    RegisterAPIView,
    LoginAPIView,
    LogoutAPIView,
    RefreshTokenAPIView,
    VerifyEmailAPIView,
    UserProfileAPIView,
    ChangePasswordAPIView,
    InternalRegisterAPIView,
)

urlpatterns = [
    path('auth/register/', RegisterAPIView.as_view(), name='auth-register'),
    path('auth/login/', LoginAPIView.as_view(), name='auth-login'),
    path('auth/logout/', LogoutAPIView.as_view(), name='auth-logout'),
    path('auth/refresh/', RefreshTokenAPIView.as_view(), name='auth-refresh'),
    path('auth/verify-email/', VerifyEmailAPIView.as_view(), name='auth-verify-email'),
    path('auth/me/', UserProfileAPIView.as_view(), name='auth-me'),
    path('auth/change-password/', ChangePasswordAPIView.as_view(), name='auth-change-password'),
    path('internal/register/', InternalRegisterAPIView.as_view(), name='internal-register'),
]
