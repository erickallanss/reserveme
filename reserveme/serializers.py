"""
Serializers do app reserveme.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from core.utils.helpers import validate_cpf, format_cpf
from reserveme.models import Hotel, Room, Booking
import re

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer para leitura de usuário."""
    
    full_name = serializers.SerializerMethodField()
    cpf = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 
            'full_name', 'cpf', 'telefone', 'data_nascimento', 
            'avatar', 'role', 'email_verified',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'email_verified', 'created_at', 
            'updated_at', 'role'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_cpf(self, obj):
        return format_cpf(obj.cpf) if obj.cpf else None


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer para registro de novo usuário."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    cpf = serializers.CharField(required=True, max_length=14)
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'password_confirm',
            'first_name', 'last_name', 'cpf', 'telefone', 'data_nascimento'
        ]
    
    def validate_email(self, value):
        """Valida unicidade do email."""
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError(
                "Este email já está cadastrado."
            )
        return value.lower()
    
    def validate_username(self, value):
        """Valida unicidade do username."""
        if User.objects.filter(username=value.lower()).exists():
            raise serializers.ValidationError(
                "Este nome de usuário já está em uso."
            )
        return value.lower()
    
    def validate_cpf(self, value):
        if not value:
            raise serializers.ValidationError("CPF é obrigatório.")
        
        cpf_clean = ''.join(filter(str.isdigit, value))
        
        if not cpf_clean or len(cpf_clean) != 11:
            raise serializers.ValidationError("CPF deve conter 11 dígitos.")
        
        if not validate_cpf(cpf_clean):
            raise serializers.ValidationError("CPF inválido.")
        
        if User.objects.filter(cpf=cpf_clean).exists():
            raise serializers.ValidationError("Este CPF já está cadastrado.")
        
        return cpf_clean
    
    def validate_telefone(self, value):
        """Valida formato do telefone."""
        if value and not re.match(r'^\(\d{2}\)\s\d{4,5}-\d{4}$', value):
            raise serializers.ValidationError(
                "Telefone deve estar no formato: (99) 99999-9999"
            )
        return value
    
    def validate(self, attrs):
        """Validações gerais."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'As senhas não coincidem.'
            })
        
        password = attrs.get('password')
        user = User(**{
            k: v for k, v in attrs.items() 
            if k not in ['password', 'password_confirm']
        })
        
        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        
        attrs.pop('password_confirm', None)
        
        return attrs
    
    def create(self, validated_data):
        """Cria novo usuário."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            **validated_data,
            is_active=True,
            email_verified=False,
            role='customer'
        )
        user.set_password(password)
        user.save()
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer para login."""
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualização de perfil."""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'telefone', 
            'data_nascimento', 'avatar'
        ]


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer para mudança de senha."""
    
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Valida se as senhas novas coincidem."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'As senhas não coincidem.'
            })
        
        try:
            validate_password(attrs['new_password'])
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})
        
        return attrs


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer para verificação de email."""
    
    token = serializers.CharField(required=True)


class InternalUserRegisterSerializer(serializers.ModelSerializer):
    """Serializer para registro de usuários internos (admin/staff)."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    cpf = serializers.CharField(required=True, max_length=14)
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'password_confirm',
            'first_name', 'last_name', 'cpf', 'telefone', 
            'data_nascimento', 'role'
        ]
    
    def validate_email(self, value):
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("Este email já está cadastrado.")
        return value.lower()
    
    def validate_username(self, value):
        if User.objects.filter(username=value.lower()).exists():
            raise serializers.ValidationError("Este nome de usuário já está em uso.")
        return value.lower()
    
    def validate_cpf(self, value):
        if not value:
            raise serializers.ValidationError("CPF é obrigatório.")
        
        cpf_clean = ''.join(filter(str.isdigit, value))
        
        if not cpf_clean or len(cpf_clean) != 11:
            raise serializers.ValidationError("CPF deve conter 11 dígitos.")
        
        if not validate_cpf(cpf_clean):
            raise serializers.ValidationError("CPF inválido.")
        
        if User.objects.filter(cpf=cpf_clean).exists():
            raise serializers.ValidationError("Este CPF já está cadastrado.")
        
        return cpf_clean
    
    def validate_telefone(self, value):
        if value and not re.match(r'^\(\d{2}\)\s\d{4,5}-\d{4}$', value):
            raise serializers.ValidationError("Telefone deve estar no formato: (99) 99999-9999")
        return value
    
    def validate_role(self, value):
        if value not in ['admin', 'staff']:
            raise serializers.ValidationError("Role deve ser 'admin' ou 'staff'.")
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'As senhas não coincidem.'
            })
        
        password = attrs.get('password')
        user = User(**{
            k: v for k, v in attrs.items() 
            if k not in ['password', 'password_confirm']
        })
        
        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        
        return attrs



# Hotel Serializers
class HotelSerializer(serializers.ModelSerializer):
    """Serializer para leitura e escrita de Hotel."""
    
    class Meta:
        model = Hotel
        fields = [
            'id', 'nome', 'descricao', 'logo', 'endereco', 
            'telefone', 'email', 'horario_checkin', 'horario_checkout',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_telefone(self, value):
        """Valida formato do telefone."""
        if value and not re.match(r'^\(\d{2}\)\s\d{4,5}-\d{4}$', value):
            raise serializers.ValidationError(
                'Telefone deve estar no formato: (99) 99999-9999'
            )
        return value
    
    def validate_nome(self, value):
        """Valida unicidade do nome (case insensitive)."""
        instance_id = self.instance.id if self.instance else None
        
        queryset = Hotel.objects.filter(nome__iexact=value)
        if instance_id:
            queryset = queryset.exclude(id=instance_id)
        
        if queryset.exists():
            raise serializers.ValidationError('Já existe um hotel com este nome.')
        
        return value
    
    def validate_email(self, value):
        """Valida unicidade do email (case insensitive)."""
        instance_id = self.instance.id if self.instance else None
        
        queryset = Hotel.objects.filter(email__iexact=value)
        if instance_id:
            queryset = queryset.exclude(id=instance_id)
        
        if queryset.exists():
            raise serializers.ValidationError('Já existe um hotel com este email.')
        
        return value.lower()


class HotelCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de Hotel."""
    
    class Meta:
        model = Hotel
        fields = [
            'nome', 'descricao', 'logo', 'endereco', 
            'telefone', 'email', 'horario_checkin', 'horario_checkout'
        ]
    
    def validate_telefone(self, value):
        """Valida formato do telefone."""
        if value and not re.match(r'^\(\d{2}\)\s\d{4,5}-\d{4}$', value):
            raise serializers.ValidationError(
                'Telefone deve estar no formato: (99) 99999-9999'
            )
        return value
    
    def validate_nome(self, value):
        """Valida unicidade do nome."""
        if Hotel.objects.filter(nome__iexact=value).exists():
            raise serializers.ValidationError('Já existe um hotel com este nome.')
        return value
    
    def validate_email(self, value):
        """Valida unicidade do email."""
        if Hotel.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Já existe um hotel com este email.')
        return value.lower()


class HotelUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualização de Hotel."""
    
    class Meta:
        model = Hotel
        fields = [
            'nome', 'descricao', 'logo', 'endereco', 
            'telefone', 'email', 'horario_checkin', 'horario_checkout',
            'is_active'
        ]
    
    def validate_telefone(self, value):
        """Valida formato do telefone."""
        if value and not re.match(r'^\(\d{2}\)\s\d{4,5}-\d{4}$', value):
            raise serializers.ValidationError(
                'Telefone deve estar no formato: (99) 99999-9999'
            )
        return value


# Room Serializers
class RoomSerializer(serializers.ModelSerializer):
    """Serializer para leitura de Room."""
    
    hotel_nome = serializers.CharField(source='hotel.nome', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    nome_completo = serializers.CharField(read_only=True)
    comodidades = serializers.ListField(source='comodidades_list', read_only=True)
    
    class Meta:
        model = Room
        fields = [
            'id', 'hotel', 'hotel_nome', 'numero', 'tipo', 'tipo_display',
            'nome_completo', 'descricao', 'capacidade', 'preco_diaria',
            'tem_ar_condicionado', 'tem_wifi', 'tem_tv', 'tem_frigobar',
            'tem_banheira', 'tem_varanda', 'comodidades',
            'foto_principal', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RoomCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de Room."""
    
    class Meta:
        model = Room
        fields = [
            'hotel', 'numero', 'tipo', 'descricao', 'capacidade', 'preco_diaria',
            'tem_ar_condicionado', 'tem_wifi', 'tem_tv', 'tem_frigobar',
            'tem_banheira', 'tem_varanda', 'foto_principal'
        ]
    
    def validate_capacidade(self, value):
        """Valida capacidade."""
        if value < 1:
            raise serializers.ValidationError("Capacidade deve ser no mínimo 1.")
        if value > 10:
            raise serializers.ValidationError("Capacidade máxima é 10 pessoas.")
        return value
    
    def validate_preco_diaria(self, value):
        """Valida preço da diária."""
        if value <= 0:
            raise serializers.ValidationError("Preço da diária deve ser maior que zero.")
        return value


class RoomUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualização de Room."""
    
    class Meta:
        model = Room
        fields = [
            'numero', 'tipo', 'descricao', 'capacidade', 'preco_diaria',
            'tem_ar_condicionado', 'tem_wifi', 'tem_tv', 'tem_frigobar',
            'tem_banheira', 'tem_varanda', 'foto_principal', 'is_active'
        ]
    
    def validate_capacidade(self, value):
        """Valida capacidade."""
        if value < 1:
            raise serializers.ValidationError("Capacidade deve ser no mínimo 1.")
        if value > 10:
            raise serializers.ValidationError("Capacidade máxima é 10 pessoas.")
        return value
    
    def validate_preco_diaria(self, value):
        """Valida preço da diária."""
        if value <= 0:
            raise serializers.ValidationError("Preço da diária deve ser maior que zero.")
        return value


# Booking Serializers
class BookingSerializer(serializers.ModelSerializer):
    """Serializer para leitura de Booking."""
    
    # Dados do usuário
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    # Dados do quarto
    room_numero = serializers.CharField(source='room.numero', read_only=True)
    room_tipo = serializers.CharField(source='room.get_tipo_display', read_only=True)
    
    # Dados do hotel
    hotel_nome = serializers.CharField(source='room.hotel.nome', read_only=True)
    hotel_endereco = serializers.CharField(source='room.hotel.endereco', read_only=True)
    hotel_telefone = serializers.CharField(source='room.hotel.telefone', read_only=True)
    
    # Status display
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'codigo_reserva', 'status', 'status_display',
            'user', 'user_email', 'user_name',
            'room', 'room_numero', 'room_tipo',
            'hotel_nome', 'hotel_endereco', 'hotel_telefone',
            'data_checkin', 'data_checkout', 'numero_hospedes', 'numero_diarias',
            'preco_diaria', 'preco_total', 'observacoes',
            'created_at', 'updated_at', 'cancelled_at',
            'checked_in_at', 'checked_out_at'
        ]
        read_only_fields = [
            'id', 'codigo_reserva', 'status', 'numero_diarias',
            'preco_diaria', 'preco_total', 'created_at', 'updated_at',
            'cancelled_at', 'checked_in_at', 'checked_out_at'
        ]


class BookingCreateSerializer(serializers.Serializer):
    """Serializer para criação de Booking."""
    
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.filter(is_active=True))
    data_checkin = serializers.DateField()
    data_checkout = serializers.DateField()
    numero_hospedes = serializers.IntegerField(min_value=1)
    observacoes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_numero_hospedes(self, value):
        """Valida número de hóspedes."""
        if value < 1:
            raise serializers.ValidationError("Número de hóspedes deve ser no mínimo 1.")
        if value > 10:
            raise serializers.ValidationError("Número máximo de hóspedes é 10.")
        return value
    
    def validate(self, attrs):
        """Validações gerais."""
        data_checkin = attrs.get('data_checkin')
        data_checkout = attrs.get('data_checkout')
        
        if data_checkout <= data_checkin:
            raise serializers.ValidationError({
                'data_checkout': 'Data de check-out deve ser posterior à data de check-in.'
            })
        
        return attrs


class BookingListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de bookings."""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    room_numero = serializers.CharField(source='room.numero', read_only=True)
    hotel_nome = serializers.CharField(source='room.hotel.nome', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'codigo_reserva', 'status', 'status_display',
            'user_email', 'room_numero', 'hotel_nome',
            'data_checkin', 'data_checkout', 'numero_diarias',
            'preco_total', 'created_at'
        ]

