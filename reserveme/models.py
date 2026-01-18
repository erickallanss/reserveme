"""
Models do app reserveme.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Modelo de usuário customizado para o sistema ReserveMe.
    
    Estende AbstractUser do Django com campos adicionais como CPF,
    telefone, avatar e sistema de roles (admin/staff/customer).
    
    Attributes:
        email: Email único do usuário (usado como USERNAME_FIELD)
        cpf: CPF único do usuário
        telefone: Telefone no formato (99) 99999-9999
        role: Papel do usuário (admin, staff ou customer)
        email_verified: Indica se o email foi verificado
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
        """Verifica se o usuário pode fazer login.
        
        Returns:
            bool: True se usuário está ativo e email verificado.
        """
        return self.is_active and self.email_verified
    
    @property
    def is_admin(self):
        """Verifica se o usuário é administrador.
        
        Returns:
            bool: True se role é 'admin' ou é superuser.
        """
        return self.role == 'admin' or self.is_superuser
    
    @property
    def is_staff_member(self):
        """Verifica se o usuário é staff ou admin.
        
        Returns:
            bool: True se role é 'staff' ou 'admin'.
        """
        return self.role == 'staff' or self.is_admin
    
    @property
    def is_customer(self):
        """Verifica se o usuário é cliente.
        
        Returns:
            bool: True se role é 'customer'.
        """
        return self.role == 'customer'


class Hotel(models.Model):
    """Modelo que representa um Hotel no sistema.
    
    Attributes:
        nome: Nome único do hotel
        endereco: Endereço completo
        telefone: Telefone de contato
        email: Email de contato
        horario_checkin: Horário padrão de check-in
        horario_checkout: Horário padrão de check-out
        is_active: Indica se o hotel está ativo
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


class Room(models.Model):
    """Modelo que representa um Quarto em um Hotel.
    
    Attributes:
        hotel: Hotel ao qual o quarto pertence
        numero: Número do quarto (único por hotel)
        tipo: Tipo do quarto (single, double, suite, etc)
        capacidade: Número máximo de hóspedes
        preco_diaria: Preço da diária em reais
        is_active: Indica se o quarto está disponível para reservas
    """
    
    TIPO_CHOICES = [
        ('single', 'Solteiro'),
        ('double', 'Casal'),
        ('twin', 'Twin (2 Solteiros)'),
        ('triple', 'Triplo'),
        ('suite', 'Suíte'),
        ('deluxe', 'Suíte Deluxe'),
        ('presidential', 'Suíte Presidencial'),
    ]
    
    # Relacionamento
    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name='quartos',
        verbose_name='Hotel'
    )
    
    # Identificação
    numero = models.CharField(
        max_length=10,
        verbose_name='Número do Quarto',
        help_text='Número ou identificação do quarto (ex: 101, A1, etc)'
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='double',
        verbose_name='Tipo de Quarto'
    )
    
    # Descrição
    descricao = models.TextField(
        blank=True,
        verbose_name='Descrição',
        help_text='Descrição detalhada do quarto'
    )
    
    # Capacidade
    capacidade = models.PositiveIntegerField(
        default=2,
        verbose_name='Capacidade',
        help_text='Número máximo de hóspedes'
    )
    
    # Preço
    preco_diaria = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Preço da Diária',
        help_text='Valor da diária em reais'
    )
    
    # Comodidades
    tem_ar_condicionado = models.BooleanField(
        default=True,
        verbose_name='Ar Condicionado'
    )
    
    tem_wifi = models.BooleanField(
        default=True,
        verbose_name='Wi-Fi'
    )
    
    tem_tv = models.BooleanField(
        default=True,
        verbose_name='TV'
    )
    
    tem_frigobar = models.BooleanField(
        default=True,
        verbose_name='Frigobar'
    )
    
    tem_banheira = models.BooleanField(
        default=False,
        verbose_name='Banheira'
    )
    
    tem_varanda = models.BooleanField(
        default=False,
        verbose_name='Varanda'
    )
    
    # Imagens
    foto_principal = models.ImageField(
        upload_to='rooms/photos/%Y/%m/',
        null=True,
        blank=True,
        verbose_name='Foto Principal',
        help_text='Foto principal do quarto'
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo',
        help_text='Quarto disponível para reservas'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )
    
    class Meta:
        verbose_name = 'Quarto'
        verbose_name_plural = 'Quartos'
        ordering = ['hotel', 'numero']
        unique_together = [['hotel', 'numero']]
    
    def __str__(self):
        return f"{self.hotel.nome} - Quarto {self.numero}"
    
    def __repr__(self):
        return f'<Room: {self.hotel.nome} - {self.numero} ({self.tipo})>'
    
    @property
    def nome_completo(self):
        """Retorna nome completo formatado do quarto.
        
        Returns:
            str: Nome no formato "Quarto {numero} - {tipo}".
        """
        return f"Quarto {self.numero} - {self.get_tipo_display()}"
    
    @property
    def comodidades_list(self):
        """Retorna lista de comodidades disponíveis no quarto.
        
        Returns:
            list: Lista de strings com comodidades ativas.
        """
        comodidades = []
        if self.tem_ar_condicionado:
            comodidades.append('Ar Condicionado')
        if self.tem_wifi:
            comodidades.append('Wi-Fi')
        if self.tem_tv:
            comodidades.append('TV')
        if self.tem_frigobar:
            comodidades.append('Frigobar')
        if self.tem_banheira:
            comodidades.append('Banheira')
        if self.tem_varanda:
            comodidades.append('Varanda')
        return comodidades


class Booking(models.Model):
    """Modelo que representa uma Reserva de Quarto.
    
    Attributes:
        room: Quarto reservado
        user: Cliente que fez a reserva
        codigo_reserva: Código único gerado automaticamente
        data_checkin: Data de entrada
        data_checkout: Data de saída
        status: Status da reserva (pending, confirmed, checked_in, etc)
        preco_total: Valor total calculado automaticamente
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('confirmed', 'Confirmada'),
        ('checked_in', 'Check-in Realizado'),
        ('checked_out', 'Check-out Realizado'),
        ('cancelled', 'Cancelada'),
    ]
    
    # Relacionamentos
    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name='reservas',
        verbose_name='Quarto'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reservas',
        verbose_name='Cliente'
    )
    
    # Código único da reserva
    codigo_reserva = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código da Reserva',
        help_text='Código único para identificar a reserva'
    )
    
    # Datas
    data_checkin = models.DateField(
        verbose_name='Data de Check-in'
    )
    
    data_checkout = models.DateField(
        verbose_name='Data de Check-out'
    )
    
    # Valores
    numero_hospedes = models.PositiveIntegerField(
        verbose_name='Número de Hóspedes',
        help_text='Quantidade de pessoas'
    )
    
    numero_diarias = models.PositiveIntegerField(
        verbose_name='Número de Diárias',
        help_text='Quantidade de noites'
    )
    
    preco_diaria = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Preço da Diária',
        help_text='Valor da diária no momento da reserva'
    )
    
    preco_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Preço Total',
        help_text='Valor total da reserva'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Status'
    )
    
    # Observações
    observacoes = models.TextField(
        blank=True,
        verbose_name='Observações',
        help_text='Observações ou requisitos especiais'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criada em'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizada em'
    )
    
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Cancelada em'
    )
    
    checked_in_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Check-in realizado em'
    )
    
    checked_out_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Check-out realizado em'
    )
    
    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.codigo_reserva} - {self.user.email}"
    
    def __repr__(self):
        return f'<Booking: {self.codigo_reserva} - {self.status}>'
    
    @property
    def hotel(self):
        """Retorna o hotel associado ao quarto da reserva.
        
        Returns:
            Hotel: Instância do hotel.
        """
        return self.room.hotel
    
    @property
    def is_active(self):
        """Verifica se a reserva está ativa.
        
        Returns:
            bool: True se status é pending, confirmed ou checked_in.
        """
        return self.status in ['pending', 'confirmed', 'checked_in']
    
    @property
    def can_cancel(self):
        """Verifica se a reserva pode ser cancelada.
        
        Returns:
            bool: True se status permite cancelamento.
        """
        return self.status in ['pending', 'confirmed']
    
    @property
    def can_checkin(self):
        """Verifica se pode realizar check-in.
        
        Returns:
            bool: True se status é 'confirmed'.
        """
        return self.status == 'confirmed'
    
    @property
    def can_checkout(self):
        """Verifica se pode realizar check-out.
        
        Returns:
            bool: True se status é 'checked_in'.
        """
        return self.status == 'checked_in'
    
    def save(self, *args, **kwargs):
        """Override save para gerar código único da reserva automaticamente.
        
        O código é gerado no formato RES-YYYYMMDD-XXXX onde XXXX são
        dígitos aleatórios. Se já existir, gera um novo.
        """
        if not self.codigo_reserva:
            from django.utils import timezone
            import random
            import string
            
            # Formato: RES-YYYYMMDD-XXXX
            date_str = timezone.now().strftime('%Y%m%d')
            random_str = ''.join(random.choices(string.digits, k=4))
            self.codigo_reserva = f'RES-{date_str}-{random_str}'
            
            # Verificar se já existe (muito improvável, mas melhor garantir)
            while Booking.objects.filter(codigo_reserva=self.codigo_reserva).exists():
                random_str = ''.join(random.choices(string.digits, k=4))
                self.codigo_reserva = f'RES-{date_str}-{random_str}'
        
        super().save(*args, **kwargs)
