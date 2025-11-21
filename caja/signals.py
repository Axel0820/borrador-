from django.db.models.signals import post_save
from django.dispatch import receiver
from app.models import Compras, MovimientosCaja


@receiver(post_save, sender=Compras)
def crear_movimiento_desde_venta(sender, instance, created, **kwargs):
    """
    Signal que crea automáticamente un MovimientosCaja 
    cuando se registra una venta (Compras).
    
    Se ejecuta después de guardar una Compra y crea el registro
    de movimiento en caja de forma automática.
    """
    # Solo crear movimiento si:
    # 1. Es una nueva compra (created=True)
    # 2. La compra está activa (estado_compra=1)
    # 3. Aún no existe un movimiento para esta compra
    
    if created and instance.estado_compra == 1:
        try:
            # Verificar que no existe ya un movimiento para esta venta
            existe_movimiento = MovimientosCaja.objects.filter(
                id_compra_fk=instance,
                es_automatico=True
            ).exists()
            
            if not existe_movimiento:
                # Obtener el nombre del método de pago
                metodo_pago_display = instance.get_metodo_pago_display() if hasattr(instance, 'get_metodo_pago_display') else 'Efectivo'
                
                # Usar el nombre_compra como descripción
                # Limpiar el nombre_compra para que solo diga "Venta"
                if instance.nombre_compra:
                    descripcion = instance.nombre_compra.replace('Venta POS - ', 'Venta - ').replace('Venta POS:', 'Venta:')
                else:
                    descripcion = f'Venta #{instance.id_compra}'
                
                # Crear el movimiento automático
                MovimientosCaja.objects.create(
                    tipo_movimiento='ingreso',
                    categoria='venta',
                    monto=instance.precio_compra,
                    descripcion=descripcion,
                    id_caja_fk=instance.id_caja_fk,
                    id_empleado_fk=instance.id_empleado_fk,
                    id_compra_fk=instance,
                    es_automatico=True,
                    observaciones=f'Método de pago: {metodo_pago_display}'
                )
        except Exception:
            # Silenciar errores para no interrumpir el flujo de venta
            pass
