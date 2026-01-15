"""
Serializers do app reserveme.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
import re

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer para leitura de usuário."""
    
    full_name = serializers.SerializerMethodField()
    
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
        """Valida formato e unicidade do CPF."""
        if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', value):
            raise serializers.ValidationError(
                "CPF deve estar no formato: 999.999.999-99"
            )
        
        if User.objects.filter(cpf=value).exists():
            raise serializers.ValidationError(
                "Este CPF já está cadastrado."
            )
        
        return value
    
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
