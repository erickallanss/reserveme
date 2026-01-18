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
from reserveme.views.hotel_views import (
    HotelListCreateAPIView,
    HotelDetailAPIView
)
from reserveme.views.room_views import (
    RoomListCreateAPIView,
    RoomDetailAPIView
)
from reserveme.views.booking_views import (
    BookingListCreateAPIView,
    BookingDetailAPIView,
    BookingConfirmAPIView,
    BookingCheckinAPIView,
    BookingCheckoutAPIView,
    HotelBookingsAPIView
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
    
    # Hotel routes
    path('hotels/', HotelListCreateAPIView.as_view(), name='hotel-list-create'),
    path('hotels/<int:hotel_id>/', HotelDetailAPIView.as_view(), name='hotel-detail'),
    
    # Room routes
    path('rooms/', RoomListCreateAPIView.as_view(), name='room-list-create'),
    path('rooms/<int:room_id>/', RoomDetailAPIView.as_view(), name='room-detail'),
    
    # Booking routes
    path('bookings/', BookingListCreateAPIView.as_view(), name='booking-list-create'),
    path('bookings/<int:booking_id>/', BookingDetailAPIView.as_view(), name='booking-detail'),
    path('bookings/<int:booking_id>/confirm/', BookingConfirmAPIView.as_view(), name='booking-confirm'),
    path('bookings/<int:booking_id>/checkin/', BookingCheckinAPIView.as_view(), name='booking-checkin'),
    path('bookings/<int:booking_id>/checkout/', BookingCheckoutAPIView.as_view(), name='booking-checkout'),
    path('hotels/<int:hotel_id>/bookings/', HotelBookingsAPIView.as_view(), name='hotel-bookings'),
]
