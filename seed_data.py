#!/usr/bin/env python
"""
Script para popular o banco de dados com dados de teste.

Uso:
    python seed_data.py
    ou
    docker compose exec web python seed_data.py
"""
import os
import django
from datetime import date, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from reserveme.models import Hotel, Room, Booking

User = get_user_model()


def create_users():
    """Cria usuários de teste."""
    print("📝 Criando usuários...")
    
    # Admin
    admin, created = User.objects.get_or_create(
        email='admin@reserveme.com',
        defaults={
            'username': 'admin',
            'first_name': 'Admin',
            'last_name': 'Sistema',
            'cpf': '11111111111',
            'telefone': '(11) 99999-0001',
            'role': 'admin',
            'email_verified': True,
            'is_active': True,
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        print(f"  ✅ Admin criado: {admin.email} / admin123")
    else:
        print(f"  ⏭️  Admin já existe: {admin.email}")
    
    # Staff
    staff, created = User.objects.get_or_create(
        email='staff@reserveme.com',
        defaults={
            'username': 'staff',
            'first_name': 'Carlos',
            'last_name': 'Recepcionista',
            'cpf': '22222222222',
            'telefone': '(11) 99999-0002',
            'role': 'staff',
            'email_verified': True,
            'is_active': True,
        }
    )
    if created:
        staff.set_password('staff123')
        staff.save()
        print(f"  ✅ Staff criado: {staff.email} / staff123")
    else:
        print(f"  ⏭️  Staff já existe: {staff.email}")
    
    # Clientes
    clientes_data = [
        {
            'email': 'joao.silva@example.com',
            'username': 'joao.silva',
            'first_name': 'João',
            'last_name': 'Silva',
            'cpf': '12345678901',
            'telefone': '(11) 98765-4321',
        },
        {
            'email': 'maria.santos@example.com',
            'username': 'maria.santos',
            'first_name': 'Maria',
            'last_name': 'Santos',
            'cpf': '23456789012',
            'telefone': '(21) 98765-4321',
        },
        {
            'email': 'pedro.oliveira@example.com',
            'username': 'pedro.oliveira',
            'first_name': 'Pedro',
            'last_name': 'Oliveira',
            'cpf': '34567890123',
            'telefone': '(31) 98765-4321',
        },
        {
            'email': 'ana.costa@example.com',
            'username': 'ana.costa',
            'first_name': 'Ana',
            'last_name': 'Costa',
            'cpf': '45678901234',
            'telefone': '(41) 98765-4321',
        },
    ]
    
    clientes = []
    for data in clientes_data:
        cliente, created = User.objects.get_or_create(
            email=data['email'],
            defaults={
                **data,
                'data_nascimento': date(1990, 1, 15),
                'role': 'customer',
                'email_verified': True,
                'is_active': True,
            }
        )
        if created:
            cliente.set_password('cliente123')
            cliente.save()
            print(f"  ✅ Cliente criado: {cliente.email} / cliente123")
        else:
            print(f"  ⏭️  Cliente já existe: {cliente.email}")
        clientes.append(cliente)
    
    return admin, staff, clientes


def create_hotel():
    """Cria hotel de teste."""
    print("\n🏨 Criando hotel...")
    
    hotel, created = Hotel.objects.get_or_create(
        nome='Hotel Paradise Beach',
        defaults={
            'descricao': 'Um hotel maravilhoso à beira-mar com vista espetacular, '
                        'serviços de primeira classe e comodidades modernas. '
                        'Perfeito para férias em família ou viagens românticas.',
            'endereco': 'Av. Atlântica, 1500 - Copacabana, Rio de Janeiro - RJ, 22021-000',
            'telefone': '(21) 3500-8000',
            'email': 'contato@paradisebeach.com.br',
            'horario_checkin': '14:00:00',
            'horario_checkout': '12:00:00',
            'is_active': True,
        }
    )
    
    if created:
        print(f"  ✅ Hotel criado: {hotel.nome}")
    else:
        print(f"  ⏭️  Hotel já existe: {hotel.nome}")
    
    return hotel


def create_rooms(hotel):
    """Cria quartos de teste."""
    print("\n🛏️  Criando quartos...")
    
    quartos_data = [
        # Standard
        {
            'numero': '101',
            'tipo': 'single',
            'descricao': 'Quarto individual com cama de solteiro, ideal para viajantes solo.',
            'capacidade': 1,
            'preco_diaria': Decimal('150.00'),
            'tem_varanda': False,
            'tem_banheira': False,
        },
        {
            'numero': '102',
            'tipo': 'double',
            'descricao': 'Quarto duplo com cama de casal e vista para o mar.',
            'capacidade': 2,
            'preco_diaria': Decimal('250.00'),
            'tem_varanda': True,
            'tem_banheira': False,
        },
        {
            'numero': '103',
            'tipo': 'twin',
            'descricao': 'Quarto com duas camas de solteiro, perfeito para amigos.',
            'capacidade': 2,
            'preco_diaria': Decimal('240.00'),
            'tem_varanda': False,
            'tem_banheira': False,
        },
        {
            'numero': '201',
            'tipo': 'double',
            'descricao': 'Quarto duplo superior com varanda e vista panorâmica.',
            'capacidade': 2,
            'preco_diaria': Decimal('300.00'),
            'tem_varanda': True,
            'tem_banheira': False,
        },
        {
            'numero': '202',
            'tipo': 'triple',
            'descricao': 'Quarto triplo espaçoso, ideal para famílias pequenas.',
            'capacidade': 3,
            'preco_diaria': Decimal('350.00'),
            'tem_varanda': True,
            'tem_banheira': False,
        },
        # Suítes
        {
            'numero': '301',
            'tipo': 'suite',
            'descricao': 'Suíte luxuosa com sala de estar separada e varanda privativa.',
            'capacidade': 2,
            'preco_diaria': Decimal('500.00'),
            'tem_varanda': True,
            'tem_banheira': True,
        },
        {
            'numero': '302',
            'tipo': 'deluxe',
            'descricao': 'Suíte Deluxe com jacuzzi, frigobar premium e vista espetacular.',
            'capacidade': 3,
            'preco_diaria': Decimal('750.00'),
            'tem_varanda': True,
            'tem_banheira': True,
        },
        {
            'numero': '401',
            'tipo': 'presidential',
            'descricao': 'Suíte Presidencial com 2 quartos, sala de jantar, cozinha completa e terraço privativo.',
            'capacidade': 4,
            'preco_diaria': Decimal('1500.00'),
            'tem_varanda': True,
            'tem_banheira': True,
        },
    ]
    
    quartos = []
    for data in quartos_data:
        quarto, created = Room.objects.get_or_create(
            hotel=hotel,
            numero=data['numero'],
            defaults={
                **data,
                'tem_ar_condicionado': True,
                'tem_wifi': True,
                'tem_tv': True,
                'tem_frigobar': True,
                'is_active': True,
            }
        )
        
        if created:
            print(f"  ✅ Quarto criado: {quarto.numero} - {quarto.get_tipo_display()} (R$ {quarto.preco_diaria}/dia)")
        else:
            print(f"  ⏭️  Quarto já existe: {quarto.numero}")
        quartos.append(quarto)
    
    return quartos


def create_bookings(quartos, clientes):
    """Cria reservas de teste."""
    print("\n📅 Criando reservas...")
    
    hoje = date.today()
    
    # Reservas variadas
    reservas_data = [
        # Reservas confirmadas (futuras)
        {
            'room': quartos[1],  # 102 - Double
            'user': clientes[0],  # João
            'data_checkin': hoje + timedelta(days=5),
            'data_checkout': hoje + timedelta(days=8),
            'numero_hospedes': 2,
            'status': 'confirmed',
            'observacoes': 'Preferência por andar alto',
        },
        {
            'room': quartos[5],  # 301 - Suite
            'user': clientes[1],  # Maria
            'data_checkin': hoje + timedelta(days=10),
            'data_checkout': hoje + timedelta(days=15),
            'numero_hospedes': 2,
            'status': 'confirmed',
            'observacoes': 'Lua de mel - decoração especial',
        },
        # Reservas pendentes
        {
            'room': quartos[4],  # 202 - Triple
            'user': clientes[2],  # Pedro
            'data_checkin': hoje + timedelta(days=7),
            'data_checkout': hoje + timedelta(days=10),
            'numero_hospedes': 3,
            'status': 'pending',
            'observacoes': 'Viagem em família com criança',
        },
        # Reserva check-in realizado
        {
            'room': quartos[0],  # 101 - Single
            'user': clientes[3],  # Ana
            'data_checkin': hoje - timedelta(days=1),
            'data_checkout': hoje + timedelta(days=2),
            'numero_hospedes': 1,
            'status': 'checked_in',
            'observacoes': 'Viagem a trabalho',
        },
        # Reserva concluída (passada)
        {
            'room': quartos[3],  # 201 - Double superior
            'user': clientes[0],  # João
            'data_checkin': hoje - timedelta(days=10),
            'data_checkout': hoje - timedelta(days=7),
            'numero_hospedes': 2,
            'status': 'checked_out',
            'observacoes': 'Excelente estadia!',
        },
        # Mais reservas futuras
        {
            'room': quartos[6],  # 302 - Deluxe
            'user': clientes[1],  # Maria
            'data_checkin': hoje + timedelta(days=20),
            'data_checkout': hoje + timedelta(days=25),
            'numero_hospedes': 2,
            'status': 'pending',
            'observacoes': 'Aniversário de casamento',
        },
        {
            'room': quartos[2],  # 103 - Twin
            'user': clientes[2],  # Pedro
            'data_checkin': hoje + timedelta(days=15),
            'data_checkout': hoje + timedelta(days=18),
            'numero_hospedes': 2,
            'status': 'confirmed',
            'observacoes': '',
        },
    ]
    
    reservas = []
    for data in reservas_data:
        # Calcular valores
        delta = data['data_checkout'] - data['data_checkin']
        numero_diarias = delta.days
        preco_diaria = data['room'].preco_diaria
        preco_total = preco_diaria * numero_diarias
        
        # Verificar se já existe reserva para este quarto neste período
        existing = Booking.objects.filter(
            room=data['room'],
            data_checkin=data['data_checkin'],
            data_checkout=data['data_checkout'],
            user=data['user']
        ).first()
        
        if existing:
            print(f"  ⏭️  Reserva já existe: {existing.codigo_reserva} - {data['room'].numero}")
            reservas.append(existing)
            continue
        
        # Criar reserva
        reserva = Booking.objects.create(
            room=data['room'],
            user=data['user'],
            data_checkin=data['data_checkin'],
            data_checkout=data['data_checkout'],
            numero_hospedes=data['numero_hospedes'],
            numero_diarias=numero_diarias,
            preco_diaria=preco_diaria,
            preco_total=preco_total,
            status=data['status'],
            observacoes=data['observacoes'],
        )
        
        print(f"  ✅ Reserva criada: {reserva.codigo_reserva} - "
              f"Quarto {reserva.room.numero} - {reserva.user.first_name} "
              f"({reserva.get_status_display()}) - {reserva.data_checkin} a {reserva.data_checkout}")
        reservas.append(reserva)
    
    return reservas


def main():
    """Executa o script de seed."""
    print("=" * 70)
    print("🌱 POPULANDO BANCO DE DADOS COM DADOS DE TESTE")
    print("=" * 70)
    
    try:
        # Criar usuários
        admin, staff, clientes = create_users()
        
        # Criar hotel
        hotel = create_hotel()
        
        # Criar quartos
        quartos = create_rooms(hotel)
        
        # Criar reservas
        reservas = create_bookings(quartos, clientes)
        
        print("\n" + "=" * 70)
        print("✅ DADOS CRIADOS COM SUCESSO!")
        print("=" * 70)
        print(f"\n📊 Resumo:")
        print(f"  • {User.objects.count()} usuários no total")
        print(f"  • {Hotel.objects.count()} hotel(is)")
        print(f"  • {Room.objects.count()} quarto(s)")
        print(f"  • {Booking.objects.count()} reserva(s)")
        
        print(f"\n🔑 Credenciais de Acesso:")
        print(f"  • Admin:   admin@reserveme.com / admin123")
        print(f"  • Staff:   staff@reserveme.com / staff123")
        print(f"  • Cliente: joao.silva@example.com / cliente123")
        print(f"  • Cliente: maria.santos@example.com / cliente123")
        print(f"  • Cliente: pedro.oliveira@example.com / cliente123")
        print(f"  • Cliente: ana.costa@example.com / cliente123")
        
        print(f"\n🌐 URLs:")
        print(f"  • API: http://localhost:8000/api/v1/")
        print(f"  • Admin: http://localhost:8000/admin/")
        print(f"  • Swagger: http://localhost:8000/api/docs/")
        print(f"  • Mailpit: http://localhost:8025/")
        
        print("\n💡 Próximos passos:")
        print("  1. Faça login na API com algum usuário")
        print("  2. Explore os endpoints no Swagger")
        print("  3. Crie novas reservas e teste o sistema!")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
