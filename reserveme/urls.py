"""
URLs do app reserveme.
"""
from django.urls import path
from reserveme.views import example_views, auth_views

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', auth_views.register, name='auth-register'),
    path('auth/login/', auth_views.login, name='auth-login'),
    path('auth/logout/', auth_views.logout, name='auth-logout'),
    path('auth/refresh/', auth_views.refresh_token, name='auth-refresh'),
    path('auth/verify-email/', auth_views.verify_email, name='auth-verify-email'),
    path('auth/me/', auth_views.me, name='auth-me'),
    path('auth/change-password/', auth_views.change_password, name='auth-change-password'),
    
    # Example endpoints
    path('examples/', example_views.example_list_create, name='example-list-create'),
    path('examples/<int:pk>/', example_views.example_detail, name='example-detail'),
]
