"""
Funções auxiliares do projeto.
"""
from typing import List, Optional, Dict, Any
from celery.result import AsyncResult
from .tasks import send_email_task, send_template_email_task, send_mass_email_task


def validate_cpf(cpf: str) -> bool:
    """
    Valida CPF usando algoritmo de dígitos verificadores.
    Remove automaticamente caracteres especiais antes da validação.
    
    Args:
        cpf: String contendo CPF (aceita com ou sem máscara)
        
    Returns:
        True se CPF válido, False caso contrário
    """
    if not cpf:
        return False
    
    # Remove todos os caracteres não numéricos
    cpf_clean = ''.join(filter(str.isdigit, cpf))
    
    if not cpf_clean or len(cpf_clean) != 11:
        return False
    
    if cpf_clean == cpf_clean[0] * 11:
        return False
    
    def calculate_digit(cpf_partial: str, weight: int) -> int:
        total = sum(int(cpf_partial[i]) * (weight - i) for i in range(len(cpf_partial)))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder
    
    first_digit = calculate_digit(cpf_clean[:9], 10)
    if first_digit != int(cpf_clean[9]):
        return False
    
    second_digit = calculate_digit(cpf_clean[:10], 11)
    if second_digit != int(cpf_clean[10]):
        return False
    
    return True


def format_cpf(cpf: str) -> str:
    """
    Formata CPF para o padrão brasileiro (111.444.777-35).
    
    Args:
        cpf: String contendo apenas números (11 dígitos)
        
    Returns:
        CPF formatado com . e -
    """
    if not cpf:
        return cpf
    
    # Remove caracteres não numéricos
    cpf_clean = ''.join(filter(str.isdigit, cpf))
    
    if len(cpf_clean) != 11:
        return cpf
    
    # Formato: 111.444.777-35
    return f"{cpf_clean[:3]}.{cpf_clean[3:6]}.{cpf_clean[6:9]}-{cpf_clean[9:]}"


def send_email_async(
    subject: str,
    message: str,
    recipient_list: List[str],
    from_email: Optional[str] = None,
    html_message: Optional[str] = None,
    fail_silently: bool = False
) -> AsyncResult:
    """
    Envia email de forma assíncrona usando Celery.
    
    Args:
        subject: Assunto do email
        message: Mensagem em texto plano
        recipient_list: Lista de emails destinatários
        from_email: Email do remetente (opcional)
        html_message: Versão HTML da mensagem (opcional)
        fail_silently: Se True, não levanta exceção em caso de erro
        
    Returns:
        AsyncResult: Objeto para acompanhar o status da task
        
    Example:
        >>> result = send_email_async(
        ...     subject='Bem-vindo!',
        ...     message='Obrigado por se cadastrar.',
        ...     recipient_list=['user@example.com']
        ... )
        >>> # Verificar status
        >>> result.ready()  # True se completou
        >>> result.successful()  # True se sucesso
        >>> result.get()  # Obtém o resultado (bloqueia até completar)
    """
    return send_email_task.delay(
        subject=subject,
        message=message,
        recipient_list=recipient_list,
        from_email=from_email,
        html_message=html_message,
        fail_silently=fail_silently
    )


def send_template_email_async(
    subject: str,
    template_name: str,
    context: Dict[str, Any],
    recipient_list: List[str],
    from_email: Optional[str] = None,
    fail_silently: bool = False
) -> AsyncResult:
    """
    Envia email usando template Django de forma assíncrona.
    
    Args:
        subject: Assunto do email
        template_name: Nome do template (ex: 'emails/welcome.html')
        context: Dicionário com variáveis do template
        recipient_list: Lista de emails destinatários
        from_email: Email do remetente (opcional)
        fail_silently: Se True, não levanta exceção em caso de erro
        
    Returns:
        AsyncResult: Objeto para acompanhar o status da task
        
    Example:
        >>> result = send_template_email_async(
        ...     subject='Bem-vindo ao ReserveMe!',
        ...     template_name='emails/welcome.html',
        ...     context={'user_name': 'João', 'activation_link': 'http://...'},
        ...     recipient_list=['user@example.com']
        ... )
    """
    return send_template_email_task.delay(
        subject=subject,
        template_name=template_name,
        context=context,
        recipient_list=recipient_list,
        from_email=from_email,
        fail_silently=fail_silently
    )


def send_mass_email_async(
    datatuple: List[tuple],
    fail_silently: bool = False
) -> AsyncResult:
    """
    Envia múltiplos emails diferentes de forma assíncrona.
    
    Args:
        datatuple: Lista de tuplas (subject, message, from_email, recipient_list)
        fail_silently: Se True, não levanta exceção em caso de erro
        
    Returns:
        AsyncResult: Objeto para acompanhar o status da task
        
    Example:
        >>> emails = [
        ...     ('Welcome', 'Welcome message', 'from@example.com', ['user1@example.com']),
        ...     ('Reminder', 'Reminder message', 'from@example.com', ['user2@example.com']),
        ... ]
        >>> result = send_mass_email_async(emails)
    """
    return send_mass_email_task.delay(
        datatuple=datatuple,
        fail_silently=fail_silently
    )


def send_email_sync(
    subject: str,
    message: str,
    recipient_list: List[str],
    from_email: Optional[str] = None,
    html_message: Optional[str] = None,
    fail_silently: bool = False
) -> int:
    """
    Envia email de forma SÍNCRONA (bloqueia até completar).
    Use apenas quando necessário esperar o resultado imediatamente.
    
    Para a maioria dos casos, prefira send_email_async().
    
    Returns:
        int: Número de emails enviados com sucesso
    """
    from django.core.mail import send_mail
    from django.conf import settings
    
    from_email = from_email or settings.DEFAULT_FROM_EMAIL
    
    return send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
        html_message=html_message,
        fail_silently=fail_silently
    )
