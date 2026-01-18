"""Integration tests for auth view error handling."""
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from reserveme.tests.factories import UserFactory


@pytest.fixture
def api_client():
    """Fixture for API client."""
    return APIClient()


@pytest.mark.django_db
class TestAuthViewErrors:
    """Tests for auth view error handling."""
    
    def test_refresh_token_without_cookie(self, api_client):
        """Test refresh token without cookie."""
        response = api_client.post('/api/v1/auth/refresh/')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_refresh_token_with_invalid_token(self, api_client):
        """Test refresh token with invalid token."""
        api_client.cookies['refresh_token'] = 'invalid_token'
        response = api_client.post('/api/v1/auth/refresh/')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
