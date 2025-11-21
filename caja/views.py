from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from app.models import Cajas, Empleados, Productos, Compras, DetalleCompras, Clientes, MovimientosCaja
from .forms import AperturaCajaForm, CierreCajaForm, MovimientoCajaForm, FiltroMovimientosForm, FiltroHistorialCajaForm
from decimal import Decimal
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from app.decorators import acceso_caja
from django.db.models import Q, Sum
from datetime import datetime, date


@login_required
@acceso_caja
def caja_principal(request):
    """Vista principal del módulo de caja"""
    try:
        empleado = request.user.empleados
        
        # Si es Gerente, puede ver cualquier caja abierta
        # Si es Cajero/Vendedor, solo su propia caja
        if request.user.groups.filter(name='Gerente').exists():
            caja_activa = Cajas.objects.filter(estado_caja=1).first()
        else:
            caja_activa = Cajas.objects.filter(
                estado_caja=1, 
                id_emp_cj=empleado
            ).first()
    except Empleados.DoesNotExist:
        context = {'error': 'Usuario no tiene empleado asociado'}
        return render(request, 'caja/caja_ajax.html', context)
    
    form_apertura = AperturaCajaForm() if not caja_activa else None
    form_cierre = CierreCajaForm() if caja_activa else None
    # form_venta = VentaForm() if caja_activa else None

    Productos_disponibles = Productos.objects.filter(
        estado_prod=1,
        stock_prod__gt=0,
        eliminado=False
    ).order_by('nombre_prod')
    
    # Obtener movimientos del día si hay caja activa
    ventas_hoy = []
    otros_movimientos = []
    total_ventas = Decimal('0.00')
    total_otros_ingresos = Decimal('0.00')
    total_otros_egresos = Decimal('0.00')
    
    if caja_activa:
        from django.utils import timezone as tz
        from datetime import datetime, time
        
        # Obtener inicio y fin del día actual en la zona horaria local
        ahora = tz.localtime(tz.now())
        inicio_dia = tz.make_aware(datetime.combine(ahora.date(), time.min))
        fin_dia = tz.make_aware(datetime.combine(ahora.date(), time.max))
        
        # Ventas (movimientos automáticos)
        ventas_hoy = MovimientosCaja.objects.filter(
            id_caja_fk=caja_activa,
            fecha_movimiento__gte=inicio_dia,
            fecha_movimiento__lte=fin_dia,
            estado=True,
            es_automatico=True,
            categoria='venta'
        ).select_related('id_compra_fk', 'id_compra_fk__id_cliente_fk').order_by('-fecha_movimiento')
        
        # Otros movimientos (manuales)
        otros_movimientos = MovimientosCaja.objects.filter(
            id_caja_fk=caja_activa,
            fecha_movimiento__gte=inicio_dia,
            fecha_movimiento__lte=fin_dia,
            estado=True,
            es_automatico=False
        ).order_by('-fecha_movimiento')
        
        # Calcular totales
        total_ventas = ventas_hoy.aggregate(total=Sum('monto'))['total'] or Decimal('0.00')
        
        totales_otros = otros_movimientos.aggregate(
            ingresos=Sum('monto', filter=Q(tipo_movimiento='ingreso')),
            egresos=Sum('monto', filter=Q(tipo_movimiento='egreso'))
        )
        total_otros_ingresos = totales_otros['ingresos'] or Decimal('0.00')
        total_otros_egresos = totales_otros['egresos'] or Decimal('0.00')
    
    # Pasar la fecha para formatear en template
    ahora_local = tz.localtime(tz.now()) if caja_activa else timezone.now()
    
    # Obtener historial de cajas si el usuario es Gerente
    historial_cajas = []
    form_filtro_historial = None
    es_gerente = request.user.groups.filter(name='Gerente').exists()
    if es_gerente:
        # Inicializar formulario de filtros
        form_filtro_historial = FiltroHistorialCajaForm(request.GET or None)
        
        # Base query
        historial_cajas = Cajas.objects.select_related('id_emp_cj').order_by('-fecha_apertura')
        
        # Aplicar filtros si el formulario es válido
        if form_filtro_historial.is_valid():
            empleado_id = form_filtro_historial.cleaned_data.get('empleado')
            fecha_desde = form_filtro_historial.cleaned_data.get('fecha_desde')
            fecha_hasta = form_filtro_historial.cleaned_data.get('fecha_hasta')
            
            if empleado_id:
                historial_cajas = historial_cajas.filter(id_emp_cj_id=empleado_id)
            
            if fecha_desde:
                from django.utils import timezone as tz
                from datetime import datetime, time
                # Convertir fecha a datetime con hora 00:00:00
                inicio_dia = tz.make_aware(datetime.combine(fecha_desde, time.min))
                historial_cajas = historial_cajas.filter(fecha_apertura__gte=inicio_dia)
            
            if fecha_hasta:
                from django.utils import timezone as tz
                from datetime import datetime, time
                # Incluir todo el día hasta las 23:59:59
                fin_dia = tz.make_aware(datetime.combine(fecha_hasta, time.max))
                historial_cajas = historial_cajas.filter(fecha_apertura__lte=fin_dia)
        
        # Limitar resultados a las últimas 50 cajas
        historial_cajas = historial_cajas[:50]
    
    context = {
        'caja_activa': caja_activa,
        'form_apertura': form_apertura,
        'form_cierre': form_cierre,
        # 'form_venta': form_venta,
        'productos' : Productos_disponibles,
        'usuario': request.user,
        'ventas_hoy': ventas_hoy,
        'otros_movimientos': otros_movimientos,
        'total_ventas': total_ventas,
        'total_otros_ingresos': total_otros_ingresos,
        'total_otros_egresos': total_otros_egresos,
        'fecha_hoy': ahora_local,
        'form_movimiento': MovimientoCajaForm() if caja_activa else None,
        'historial_cajas': historial_cajas,
        'es_gerente': es_gerente,
        'form_filtro_historial': form_filtro_historial
    }
    
    return render(request, 'caja/caja_ajax.html', context)

@login_required
def abrir_caja(request):
    """Vista AJAX para abrir caja"""
    if request.method == 'POST':
        try:
            # Obtener empleado del usuario actual
            try:
                empleado = request.user.empleados
            except Empleados.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Usuario no tiene empleado asociado'
                })
            
            # Verificar que no haya ninguna caja abierta en el sistema
            caja_existente = Cajas.objects.filter(estado_caja=1).first()
            
            if caja_existente:
                return JsonResponse({
                    'success': False, 
                    'message': f'Ya hay una caja abierta (Caja #{caja_existente.id_caja}, empleado: {caja_existente.id_emp_cj.nombre_emp} {caja_existente.id_emp_cj.apellido_emp})'
                })
            
            form = AperturaCajaForm(request.POST)
            if form.is_valid():
                caja = form.save(commit=False)
                caja.id_emp_cj = empleado
                
                caja.fecha_apertura = timezone.now()
                caja.saldo_anterior = Decimal('0.00')
                caja.saldo_actual = caja.saldo_inicial
                caja.saldo_final = Decimal('0.00')
                caja.estado_caja = 1  # Abierta
                caja.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Caja abierta exitosamente'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Error en el formulario'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

@login_required
def cerrar_caja(request):
    """Vista AJAX para cerrar caja"""
    if request.method == 'POST':
        try:
            # Obtener empleado del usuario actual
            try:
                empleado = request.user.empleados
            except Empleados.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Usuario no tiene empleado asociado'
                })
            
            # Buscar caja activa
            caja_activa = Cajas.objects.filter(estado_caja=1).first()
            
            if not caja_activa:
                return JsonResponse({
                    'success': False,
                    'message': 'No hay una caja abierta'
                })
            
            # Verificar permisos: Gerente puede cerrar cualquiera, empleados solo la suya
            es_gerente = request.user.groups.filter(name='Gerente').exists()
            
            if not es_gerente and caja_activa.id_emp_cj != empleado:
                return JsonResponse({
                    'success': False,
                    'message': f'No puedes cerrar esta caja. Fue abierta por {caja_activa.id_emp_cj.nombre_emp} {caja_activa.id_emp_cj.apellido_emp}'
                })
            
            form = CierreCajaForm(request.POST)
            if form.is_valid():
                caja_activa.saldo_final = form.cleaned_data['saldo_final']
                caja_activa.fecha_cierre = timezone.now()
                caja_activa.estado_caja = 0  # Cerrada
                caja_activa.save()

                # calcular diferencia
                diferencia = caja_activa.saldo_final - caja_activa.saldo_actual
                
                return JsonResponse({
                    'success': True,
                    'message': 'Caja cerrada exitosamente',
                    'saldo_calculado': str(caja_activa.saldo_actual),
                    'saldo_declarado': str(caja_activa.saldo_final),
                    'diferencia': str(diferencia)
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Error en el formulario'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

# Las vistas de ventas se han movido a la app 'ventas'


@login_required
def listar_movimientos(request):
    """Vista para listar movimientos de caja con filtros"""
    caja_activa = Cajas.objects.filter(estado_caja=1).first()
    
    if not caja_activa:
        context = {'error': 'No hay caja abierta'}
        return render(request, 'caja/error_caja_cerrada.html', context)
    
    # Obtener movimientos de la caja activa
    movimientos = MovimientosCaja.objects.filter(
        id_caja_fk=caja_activa,
        estado=True
    )
    
    # Aplicar filtros si existen
    form_filtro = FiltroMovimientosForm(request.GET or None)
    
    if form_filtro.is_valid():
        fecha_desde = form_filtro.cleaned_data.get('fecha_desde')
        fecha_hasta = form_filtro.cleaned_data.get('fecha_hasta')
        tipo = form_filtro.cleaned_data.get('tipo_movimiento')
        categoria = form_filtro.cleaned_data.get('categoria')
        buscar = form_filtro.cleaned_data.get('buscar')
        
        if fecha_desde:
            movimientos = movimientos.filter(fecha_movimiento__date__gte=fecha_desde)
        if fecha_hasta:
            movimientos = movimientos.filter(fecha_movimiento__date__lte=fecha_hasta)
        if tipo:
            movimientos = movimientos.filter(tipo_movimiento=tipo)
        if categoria:
            movimientos = movimientos.filter(categoria=categoria)
        if buscar:
            movimientos = movimientos.filter(
                Q(descripcion__icontains=buscar) | Q(observaciones__icontains=buscar)
            )
    
    # Calcular totales
    totales = movimientos.aggregate(
        total_ingresos=Sum('monto', filter=Q(tipo_movimiento='ingreso')),
        total_egresos=Sum('monto', filter=Q(tipo_movimiento='egreso'))
    )
    
    total_ingresos = totales['total_ingresos'] or Decimal('0.00')
    total_egresos = totales['total_egresos'] or Decimal('0.00')
    balance = total_ingresos - total_egresos
    
    context = {
        'caja_activa': caja_activa,
        'movimientos': movimientos,
        'form_filtro': form_filtro,
        'total_ingresos': total_ingresos,
        'total_egresos': total_egresos,
        'balance': balance,
        'usuario': request.user
    }
    
    return render(request, 'caja/movimientos_lista.html', context)


@login_required
def registrar_movimiento(request):
    """Vista AJAX para registrar un movimiento manual de caja"""
    if request.method == 'POST':
        try:
            # Verificar caja abierta
            caja_activa = Cajas.objects.filter(estado_caja=1).first()
            if not caja_activa:
                return JsonResponse({
                    'success': False,
                    'message': 'No hay caja abierta'
                })
            
            # Obtener empleado del usuario actual
            try:
                empleado = request.user.empleados
            except Empleados.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Usuario no tiene empleado asociado'
                })
            
            form = MovimientoCajaForm(request.POST)
            if form.is_valid():
                movimiento = form.save(commit=False)
                movimiento.id_caja_fk = caja_activa
                movimiento.id_empleado_fk = empleado
                movimiento.es_automatico = False
                movimiento.save()
                
                # Actualizar saldo de caja
                if movimiento.tipo_movimiento == 'ingreso':
                    caja_activa.saldo_actual += movimiento.monto
                else:  # egreso
                    caja_activa.saldo_actual -= movimiento.monto
                caja_activa.save()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Movimiento registrado exitosamente',
                    'movimiento_id': movimiento.id_movimiento,
                    'nuevo_saldo': str(caja_activa.saldo_actual)
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Error en el formulario',
                    'errors': form.errors
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


@login_required
def anular_movimiento(request, movimiento_id):
    """Vista AJAX para anular un movimiento de caja"""
    if request.method == 'POST':
        try:
            # Verificar que el usuario sea Gerente
            if not request.user.groups.filter(name='Gerente').exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Solo los Gerentes pueden anular movimientos'
                })
            
            movimiento = MovimientosCaja.objects.get(
                id_movimiento=movimiento_id,
                estado=True
            )
            
            # Verificar que el movimiento no sea automático (venta)
            if movimiento.es_automatico:
                return JsonResponse({
                    'success': False,
                    'message': 'No se pueden anular movimientos automáticos de ventas'
                })
            
            # Verificar que la caja siga abierta
            caja = movimiento.id_caja_fk
            if caja.estado_caja != 1:
                return JsonResponse({
                    'success': False,
                    'message': 'No se puede anular un movimiento de una caja cerrada'
                })
            
            # Revertir el movimiento en el saldo
            if movimiento.tipo_movimiento == 'ingreso':
                caja.saldo_actual -= movimiento.monto
            else:  # egreso
                caja.saldo_actual += movimiento.monto
            caja.save()
            
            # Marcar como anulado
            movimiento.estado = False
            movimiento.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Movimiento anulado exitosamente',
                'nuevo_saldo': str(caja.saldo_actual)
            })
            
        except MovimientosCaja.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Movimiento no encontrado'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


@login_required
def detalle_venta(request, id_compra):
    """Vista AJAX para obtener el detalle de una venta"""
    try:
        compra = Compras.objects.get(id_compra=id_compra)
        detalles = DetalleCompras.objects.filter(id_compra_dtc=compra)
        
        # Obtener método de pago
        metodo_pago = 'Efectivo'
        if hasattr(compra, 'metodo_pago') and compra.metodo_pago:
            metodo_pago = compra.get_metodo_pago_display()
        
        data = {
            'cliente': compra.id_cliente_fk.nombre_cliente if compra.id_cliente_fk else 'Público general',
            'empleado': compra.id_empleado_fk.nombre_emp if compra.id_empleado_fk else 'No especificado',
            'fecha': compra.fecha_compra.strftime('%d/%m/%Y %H:%M'),
            'metodo_pago': metodo_pago,
            'total': str(compra.precio_compra),
            'observaciones': compra.descripcion_compra if hasattr(compra, 'descripcion_compra') and compra.descripcion_compra else '',
            'detalles': [
                {
                    'producto': detalle.id_producto_dtc.nombre_prod,
                    'cantidad': 1,  # El modelo no tiene campo cantidad, usar 1 por defecto
                    'precio_unitario': f"{float(detalle.precio_unitario_dtc):.2f}",
                    'subtotal': f"{float(detalle.subtotal_dtc):.2f}"
                }
                for detalle in detalles
            ]
        }
        
        return JsonResponse(data)
    except Compras.DoesNotExist:
        return JsonResponse({'error': 'Venta no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Error al cargar detalle: {str(e)}'}, status=500)