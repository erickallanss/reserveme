"""
Models do app reserveme.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model para o sistema ReserveMe.
    Extends AbstractUser do Django com campos adicionais.
    """
    
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('staff', 'Staff'),
        ('customer', 'Cliente'),
    ]
    
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("Já existe um usuário com este email."),
        }
    )
    
    cpf = models.CharField(
        max_length=11,
        unique=True,
        verbose_name='CPF'
    )
    
    telefone = models.CharField(
        max_length=20,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\(\d{2}\)\s\d{4,5}-\d{4}$',
                message='Telefone deve estar no formato: (99) 99999-9999',
            )
        ],
        verbose_name='Telefone',
        help_text='Formato: (99) 99999-9999'
    )
    
    data_nascimento = models.DateField(
        null=True,
        blank=True,
        verbose_name='Data de Nascimento'
    )
    
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/',
        null=True,
        blank=True,
        verbose_name='Avatar',
        help_text='Imagem de perfil do usuário'
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='customer',
        verbose_name='Papel',
        help_text='Papel do usuário no sistema'
    )
    
    email_verified = models.BooleanField(
        default=False,
        verbose_name='Email Verificado',
        help_text='Usuário verificou seu email'
    )
    
    email_verification_token = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Token de Verificação de Email'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'cpf', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def __repr__(self):
        return f'<User: {self.email} - {self.role}>'
    
    def can_login(self):
        """Verifica se o usuário pode fazer login."""
        return self.is_active and self.email_verified
    
    @property
    def is_admin(self):
        """Verifica se o usuário é admin."""
        return self.role == 'admin' or self.is_superuser
    
    @property
    def is_staff_member(self):
        """Verifica se o usuário é staff."""
        return self.role == 'staff' or self.is_admin
    
    @property
    def is_customer(self):
        """Verifica se o usuário é cliente."""
        return self.role == 'customer'


class Hotel(models.Model):
    """
    Modelo para representar um Hotel no sistema.
    """
    
    nome = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Nome do Hotel'
    )
    
    descricao = models.TextField(
        blank=True,
        verbose_name='Descrição',
        help_text='Descrição detalhada do hotel'
    )
    
    logo = models.ImageField(
        upload_to='hotels/logos/%Y/%m/',
        null=True,
        blank=True,
        verbose_name='Logo',
        help_text='Logo do hotel'
    )
    
    endereco = models.CharField(
        max_length=500,
        verbose_name='Endereço',
        help_text='Endereço completo do hotel'
    )
    
    telefone = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\(\d{2}\)\s\d{4,5}-\d{4}$',
                message='Telefone deve estar no formato: (99) 99999-9999',
            )
        ],
        verbose_name='Telefone',
        help_text='Formato: (99) 99999-9999'
    )
    
    email = models.EmailField(
        verbose_name='Email',
        help_text='Email de contato do hotel'
    )
    
    horario_checkin = models.TimeField(
        verbose_name='Horário de Check-in',
        help_text='Horário padrão para check-in'
    )
    
    horario_checkout = models.TimeField(
        verbose_name='Horário de Check-out',
        help_text='Horário padrão para check-out'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo',
        help_text='Hotel está ativo no sistema'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )
    
    class Meta:
        verbose_name = 'Hotel'
        verbose_name_plural = 'Hotéis'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome
    
    def __repr__(self):
        return f'<Hotel: {self.nome}>'
