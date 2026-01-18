"""Unit tests for Celery tasks."""
import pytest
from datetime import date, timedelta
from django.utils import timezone
from unittest.mock import patch, MagicMock
from reserveme.tasks import release_expired_bookings_task, send_booking_reminder_task
from reserveme.tests.booking_factories import BookingFactory
from reserveme.tests.room_factories import RoomFactory
from reserveme.tests.factories import UserFactory


@pytest.mark.django_db
class TestReleaseExpiredBookingsTask:
    """Tests for release_expired_bookings_task."""
    
    @patch('reserveme.tasks.send_template_email_async')
    def test_release_expired_bookings_with_expired(self, mock_email):
        """Test releasing expired bookings."""
        room = RoomFactory()
        user = UserFactory()
        
        # Create expired booking
        expired_booking = BookingFactory(
            room=room,
            user=user,
            status='pending',
            data_checkin=date.today() - timedelta(days=2)
        )
        
        result = release_expired_bookings_task()
        
        expired_booking.refresh_from_db()
        assert expired_booking.status == 'cancelled'
        assert expired_booking.cancelled_at is not None
        assert result['status'] == 'success'
        assert result['cancelled_bookings'] == 1
        mock_email.assert_called_once()
    
    def test_release_expired_bookings_no_expired(self):
        """Test task when no expired bookings exist."""
        result = release_expired_bookings_task()
        
        assert result['status'] == 'success'
        assert result['cancelled_bookings'] == 0
    
    @patch('reserveme.tasks.send_template_email_async')
    def test_release_expired_bookings_email_error(self, mock_email):
        """Test task handles email errors gracefully."""
        mock_email.side_effect = Exception("Email error")
        
        room = RoomFactory()
        user = UserFactory()
        
        expired_booking = BookingFactory(
            room=room,
            user=user,
            status='pending',
            data_checkin=date.today() - timedelta(days=2)
        )
        
        result = release_expired_bookings_task()
        
        expired_booking.refresh_from_db()
        assert expired_booking.status == 'cancelled'
        assert result['status'] == 'success'
        assert result['cancelled_bookings'] == 1


@pytest.mark.django_db
class TestSendBookingReminderTask:
    """Tests for send_booking_reminder_task."""
    
    @patch('reserveme.tasks.send_template_email_async')
    def test_send_reminder_confirmed_booking(self, mock_email):
        """Test sending reminder for confirmed booking."""
        booking = BookingFactory(status='confirmed')
        
        result = send_booking_reminder_task(booking.id)
        
        assert result['status'] == 'success'
        assert result['booking_code'] == booking.codigo_reserva
        mock_email.assert_called_once()
    
    def test_send_reminder_pending_booking(self):
        """Test reminder not sent for pending booking."""
        booking = BookingFactory(status='pending')
        
        result = send_booking_reminder_task(booking.id)
        
        assert result['status'] == 'skipped'
        assert result['reason'] == 'invalid_status'
    
    def test_send_reminder_booking_not_found(self):
        """Test reminder task when booking doesn't exist."""
        result = send_booking_reminder_task(99999)
        
        assert result['status'] == 'error'
        assert result['reason'] == 'booking_not_found'
    
    @patch('reserveme.tasks.send_template_email_async')
    def test_send_reminder_retry_on_error(self, mock_email):
        """Test task retries on error."""
        mock_email.side_effect = Exception("Email error")
        booking = BookingFactory(status='confirmed')
        
        task_instance = MagicMock()
        task_instance.request = MagicMock()
        task_instance.request.retries = 0
        
        with pytest.raises(Exception):
            send_booking_reminder_task.apply(
                args=(booking.id,),
                task_instance=task_instance
            )
