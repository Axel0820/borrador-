from django.contrib import admin
from app.models import Clientes  # Usamos el modelo de la app principal

# Register your models here.

@admin.register(Clientes)
class ClienteAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Clientes"""
    
    list_display = [
        'nombre_cliente', 'apellido_cliente', 'correo_clientes', 'telefono_cliente', 'dni_cliente', 
        'estado_cliente', 'id_cliente'
    ]
    
    list_filter = [
        'estado_cliente'
    ]
    
    search_fields = [
        'nombre_cliente', 'apellido_cliente', 'correo_clientes', 'dni_cliente', 'telefono_cliente'
    ]
    
    list_editable = ['estado_cliente']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre_cliente', 'apellido_cliente', 'dni_cliente')
        }),
        ('Información de Contacto', {
            'fields': ('correo_clientes', 'telefono_cliente')
        }),
        ('Estado', {
            'fields': ('estado_cliente',)
        }),
    )
    
    ordering = ['-id_cliente']
    
    list_per_page = 25
    
    actions = ['activar_clientes', 'desactivar_clientes']
    
    def activar_clientes(self, request, queryset):
        """Acción para activar clientes seleccionados"""
        updated = queryset.update(estado_cliente=1)
        self.message_user(
            request,
            f'{updated} cliente(s) activado(s) exitosamente.'
        )
    activar_clientes.short_description = "Activar clientes seleccionados"
    
    def desactivar_clientes(self, request, queryset):
        """Acción para desactivar clientes seleccionados"""
        updated = queryset.update(estado_cliente=0)
        self.message_user(
            request,
            f'{updated} cliente(s) desactivado(s) exitosamente.'
        )
    desactivar_clientes.short_description = "Desactivar clientes seleccionados"
