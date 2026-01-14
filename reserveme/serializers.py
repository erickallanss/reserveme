"""
Serializers para ExampleModel.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from reserveme.models import ExampleModel


class UserSerializer(serializers.ModelSerializer):
    """Serializer básico para User."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id', 'username', 'email']


class ExampleSerializer(serializers.ModelSerializer):
    """Serializer completo para ExampleModel."""
    
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = ExampleModel
        fields = [
            'id',
            'name',
            'description',
            'created_at',
            'updated_at',
            'created_by',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']


class ExampleCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de Example."""
    
    class Meta:
        model = ExampleModel
        fields = ['name', 'description']
    
    def validate_name(self, value):
        """Valida o campo name."""
        if not value.strip():
            raise serializers.ValidationError("Nome não pode ser vazio")
        return value.strip()


class ExampleUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualização de Example."""
    
    class Meta:
        model = ExampleModel
        fields = ['name', 'description']
    
    def validate_name(self, value):
        """Valida o campo name."""
        if not value.strip():
            raise serializers.ValidationError("Nome não pode ser vazio")
        return value.strip()
