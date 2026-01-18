#!/usr/bin/env python
"""
Script para verificar se o banco de dados está vazio.
Retorna código 0 se vazio, 1 se tem dados.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from reserveme.models import User, Hotel, Room, Booking

# Verificar se tem algum dado no banco
has_data = (
    User.objects.exists() or
    Hotel.objects.exists() or
    Room.objects.exists() or
    Booking.objects.exists()
)

# Retorna 0 (vazio) ou 1 (tem dados)
sys.exit(1 if has_data else 0)
