from django.contrib import admin
from reserveme.models import User, Hotel, Room, Booking


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'role', 'email_verified', 'is_active']
    list_filter = ['role', 'email_verified', 'is_active', 'created_at']
    search_fields = ['email', 'username', 'first_name', 'last_name', 'cpf']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['nome', 'endereco', 'telefone', 'email', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['nome', 'endereco', 'email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['numero', 'hotel', 'tipo', 'capacidade', 'preco_diaria', 'is_active']
    list_filter = ['tipo', 'is_active', 'hotel']
    search_fields = ['numero', 'hotel__nome']
    readonly_fields = ['created_at', 'updated_at']
    list_select_related = ['hotel']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['codigo_reserva', 'user', 'room', 'data_checkin', 'data_checkout', 'status', 'preco_total']
    list_filter = ['status', 'data_checkin', 'created_at']
    search_fields = ['codigo_reserva', 'user__email', 'room__numero', 'room__hotel__nome']
    readonly_fields = ['codigo_reserva', 'created_at', 'updated_at', 'cancelled_at', 'checked_in_at', 'checked_out_at']
    list_select_related = ['user', 'room', 'room__hotel']
    
    fieldsets = (
        ('Informações da Reserva', {
            'fields': ('codigo_reserva', 'status', 'user', 'room')
        }),
        ('Datas', {
            'fields': ('data_checkin', 'data_checkout', 'numero_diarias')
        }),
        ('Detalhes', {
            'fields': ('numero_hospedes', 'preco_diaria', 'preco_total', 'observacoes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'cancelled_at', 'checked_in_at', 'checked_out_at'),
            'classes': ('collapse',)
        }),
    )
