"""
URLs da API - Versionamento
"""
from django.urls import path, include

urlpatterns = [
    # Versionamento da API
    path('v1/', include('core.api.v1.urls')),
]
