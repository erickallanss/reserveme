"""
URLs da API v1
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Criar router para versionamento REST
router = DefaultRouter()

# Registrar seus ViewSets aqui
# router.register('exemplo', ExemploViewSet, basename='exemplo')

urlpatterns = [
    # Incluir rotas do router
    path('', include(router.urls)),
    # Incluir URLs do app reserveme
    path('', include('reserveme.urls')),
]
