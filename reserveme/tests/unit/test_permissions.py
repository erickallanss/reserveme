import pytest
from unittest.mock import Mock
from reserveme.permissions import IsAdmin, IsStaffOrAdmin
from reserveme.tests.factories import UserFactory, AdminUserFactory, StaffUserFactory


@pytest.mark.django_db
class TestIsAdminPermission:
    
    def test_admin_has_permission(self):
        permission = IsAdmin()
        request = Mock()
        request.user = AdminUserFactory()
        view = Mock()
        
        assert permission.has_permission(request, view) is True
    
    def test_staff_no_permission(self):
        permission = IsAdmin()
        request = Mock()
        request.user = StaffUserFactory()
        view = Mock()
        
        assert permission.has_permission(request, view) is False
    
    def test_customer_no_permission(self):
        permission = IsAdmin()
        request = Mock()
        request.user = UserFactory(role='customer')
        view = Mock()
        
        assert permission.has_permission(request, view) is False
    
    def test_unauthenticated_no_permission(self):
        permission = IsAdmin()
        request = Mock()
        request.user = Mock(is_authenticated=False)
        view = Mock()
        
        assert permission.has_permission(request, view) is False


@pytest.mark.django_db
class TestIsStaffOrAdminPermission:
    
    def test_admin_has_permission(self):
        permission = IsStaffOrAdmin()
        request = Mock()
        request.user = AdminUserFactory()
        view = Mock()
        
        assert permission.has_permission(request, view) is True
    
    def test_staff_has_permission(self):
        permission = IsStaffOrAdmin()
        request = Mock()
        request.user = StaffUserFactory()
        view = Mock()
        
        assert permission.has_permission(request, view) is True
    
    def test_customer_no_permission(self):
        permission = IsStaffOrAdmin()
        request = Mock()
        request.user = UserFactory(role='customer')
        view = Mock()
        
        assert permission.has_permission(request, view) is False
