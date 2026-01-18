"""Celery tasks para operações de Booking."""
import logging
from celery import shared_task
from django.utils import timezone
from reserveme.models import Booking
from core.utils.helpers import send_template_email_async

logger = logging.getLogger(__name__)


@shared_task
def release_expired_bookings_task():
    """Task periódica para liberar quartos de reservas expiradas.
    
    Busca reservas com status 'pending' cuja data de check-in já passou
    e as cancela automaticamente, liberando o quarto para novas reservas.
    Envia email de notificação ao cliente.
    
    Executa a cada 1 hora via Celery Beat.
    
    Returns:
        dict: Estatísticas da execução (status, count, message).
    """
    hoje = timezone.now().date()
    
    # Buscar reservas expiradas (pending e data de check-in passou)
    expired_bookings = Booking.objects.filter(
        status='pending',
        data_checkin__lt=hoje
    ).select_related('room', 'room__hotel', 'user')
    
    count = 0
    for booking in expired_bookings:
        # Atualizar status para cancelada
        booking.status = 'cancelled'
        booking.cancelled_at = timezone.now()
        booking.save()
        
        # Enviar email notificando o cancelamento
        try:
            send_template_email_async(
                subject=f'Reserva Cancelada Automaticamente - {booking.room.hotel.nome}',
                template_name='emails/booking_expired.html',
                context={
                    'user_name': booking.user.get_full_name(),
                    'booking': {
                        'codigo_reserva': booking.codigo_reserva,
                        'data_checkin': booking.data_checkin,
                        'data_checkout': booking.data_checkout,
                        'room': {
                            'numero': booking.room.numero,
                            'hotel': {
                                'nome': booking.room.hotel.nome,
                            },
                        },
                    },
                },
                recipient_list=[booking.user.email],
                fail_silently=True
            )
        except Exception as e:
            logger.error(f"Erro ao enviar email de cancelamento: {e}")
        
        logger.info(
            f"Reserva expirada cancelada automaticamente: {booking.codigo_reserva} - "
            f"Hotel: {booking.room.hotel.nome}, Quarto: {booking.room.numero}"
        )
        
        count += 1
    
    if count > 0:
        logger.info(f"✅ Tarefa concluída: {count} reserva(s) expirada(s) cancelada(s)")
    else:
        logger.debug("Tarefa concluída: Nenhuma reserva expirada encontrada")
    
    return {
        'status': 'success',
        'cancelled_bookings': count,
        'message': f'Liberados {count} quarto(s) de reservas expiradas'
    }


@shared_task(bind=True, max_retries=3)
def send_booking_reminder_task(self, booking_id: int):
    """Task para enviar lembrete de check-in 1 dia antes.
    
    Args:
        booking_id: ID da reserva.
        
    Returns:
        dict: Status da execução.
    """
    try:
        booking = Booking.objects.select_related(
            'room', 'room__hotel', 'user'
        ).get(id=booking_id)
        
        if booking.status == 'confirmed':
            send_template_email_async(
                subject=f'Lembrete: Check-in Amanhã - {booking.room.hotel.nome}',
                template_name='emails/booking_reminder.html',
                context={
                    'user_name': booking.user.get_full_name(),
                    'booking': {
                        'codigo_reserva': booking.codigo_reserva,
                        'data_checkin': booking.data_checkin,
                        'data_checkout': booking.data_checkout,
                    },
                    'hotel': {
                        'nome': booking.room.hotel.nome,
                        'endereco': booking.room.hotel.endereco,
                        'telefone': booking.room.hotel.telefone,
                        'horario_checkin': booking.room.hotel.horario_checkin,
                    },
                    'room': {
                        'numero': booking.room.numero,
                        'tipo': booking.room.tipo,
                        'get_tipo_display': booking.room.get_tipo_display(),
                    },
                },
                recipient_list=[booking.user.email]
            )
            
            logger.info(f"Lembrete de check-in enviado: {booking.codigo_reserva}")
            return {'status': 'success', 'booking_code': booking.codigo_reserva}
        else:
            logger.warning(
                f"Lembrete não enviado - Status inválido: {booking.codigo_reserva} "
                f"(status: {booking.status})"
            )
            return {'status': 'skipped', 'reason': 'invalid_status'}
            
    except Booking.DoesNotExist:
        logger.error(f"Booking {booking_id} não encontrada para lembrete")
        return {'status': 'error', 'reason': 'booking_not_found'}
    except Exception as exc:
        logger.error(f"Erro ao enviar lembrete: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
