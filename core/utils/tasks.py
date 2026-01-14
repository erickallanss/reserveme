"""
Celery tasks para envio de emails assíncronos
"""
from typing import List, Optional, Dict, Any
from celery import shared_task
from django.core.mail import send_mail, send_mass_mail
from django.template.loader import render_to_string
from django.conf import settings


@shared_task(bind=True, max_retries=3)
def send_email_task(
    self,
    subject: str,
    message: str,
    recipient_list: List[str],
    from_email: Optional[str] = None,
    html_message: Optional[str] = None,
    fail_silently: bool = False
) -> int:
    """
    Task assíncrona para enviar email simples.
    
    Args:
        subject: Assunto do email
        message: Mensagem em texto plano
        recipient_list: Lista de emails destinatários
        from_email: Email do remetente (usa DEFAULT_FROM_EMAIL se None)
        html_message: Versão HTML da mensagem (opcional)
        fail_silently: Se True, não levanta exceção em caso de erro
        
    Returns:
        Número de emails enviados com sucesso
        
    Raises:
        Exception: Se fail_silently=False e houver erro no envio
    """
    try:
        from_email = from_email or settings.DEFAULT_FROM_EMAIL
        
        result = send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=fail_silently
        )
        
        return result
    except Exception as exc:
        # Retry com backoff exponencial: 30s, 60s, 120s
        raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def send_template_email_task(
    self,
    subject: str,
    template_name: str,
    context: Dict[str, Any],
    recipient_list: List[str],
    from_email: Optional[str] = None,
    fail_silently: bool = False
) -> int:
    """
    Task assíncrona para enviar email usando template Django.
    
    Args:
        subject: Assunto do email
        template_name: Nome do template (ex: 'emails/welcome.html')
        context: Dicionário com variáveis do template
        recipient_list: Lista de emails destinatários
        from_email: Email do remetente (usa DEFAULT_FROM_EMAIL se None)
        fail_silently: Se True, não levanta exceção em caso de erro
        
    Returns:
        Número de emails enviados com sucesso
    """
    try:
        from_email = from_email or settings.DEFAULT_FROM_EMAIL
        
        # Renderizar template HTML
        html_message = render_to_string(template_name, context)
        
        # Renderizar versão texto (busca template .txt se existir)
        text_template = template_name.replace('.html', '.txt')
        try:
            message = render_to_string(text_template, context)
        except:
            # Se não houver template .txt, remove tags HTML
            from django.utils.html import strip_tags
            message = strip_tags(html_message)
        
        result = send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=fail_silently
        )
        
        return result
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def send_mass_email_task(
    self,
    datatuple: List[tuple],
    fail_silently: bool = False
) -> int:
    """
    Task assíncrona para enviar múltiplos emails diferentes.
    
    Args:
        datatuple: Lista de tuplas (subject, message, from_email, recipient_list)
        fail_silently: Se True, não levanta exceção em caso de erro
        
    Returns:
        Número de emails enviados com sucesso
        
    Example:
        >>> datatuple = [
        ...     ('Subject 1', 'Message 1', 'from@example.com', ['to1@example.com']),
        ...     ('Subject 2', 'Message 2', 'from@example.com', ['to2@example.com']),
        ... ]
        >>> send_mass_email_task.delay(datatuple)
    """
    try:
        result = send_mass_mail(
            datatuple=datatuple,
            fail_silently=fail_silently
        )
        
        return result
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))
