from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from app.models import Cajas, Empleados, Productos, Compras, DetalleCompras, Clientes
from .forms import VentaForm
from decimal import Decimal
import json


@login_required
def nueva_venta(request):
    """Vista para mostrar formulario de venta POS"""
    # Verificar que hay caja abierta
    caja_activa = Cajas.objects.filter(estado_caja=1).first()
    
    if not caja_activa:
        # Siempre mostrar la página de error de caja cerrada, tanto para AJAX como para navegación normal
        return render(request, 'ventas/error_caja_cerrada.html')
    
    # Obtener empleado del usuario actual
    try:
        empleado = request.user.empleados
    except Empleados.DoesNotExist:
        context = {'error': 'Usuario no tiene empleado asociado'}
        return render(request, 'ventas/error_datos.html', context)
    
    # Obtener cliente por defecto
    cliente_defecto = Clientes.objects.first()
    
    # Verificar que existen datos básicos
    if not cliente_defecto:
        context = {'error': 'No hay clientes registrados en el sistema'}
        return render(request, 'ventas/error_datos.html', context)
    
    # Obtener todos los productos disponibles para el POS
    productos_disponibles = Productos.objects.filter(
        estado_prod=1,
        stock_prod__gt=0,
        eliminado=False
    ).order_by('nombre_prod')
    
    # Organizar productos por categoría para filtros
    categorias = {}
    for producto in productos_disponibles:
        categoria = getattr(producto, 'categoria_prod', 'Sin categoría')
        if categoria not in categorias:
            categorias[categoria] = []
        categorias[categoria].append({
            'id': producto.id_prod,
            'nombre': producto.nombre_prod,
            'precio': producto.precio_prod,
            'stock': producto.stock_prod,
            'categoria': categoria,
            'imagen': getattr(producto, 'imagen_prod', None)
        })
    
    context = {
        'form_venta': VentaForm(),
        'empleado_defecto': empleado,
        'cliente_defecto': cliente_defecto,
        'caja_activa': caja_activa,
        'productos_disponibles': productos_disponibles,
        'productos_por_categoria': categorias,
        'total_productos': productos_disponibles.count()
    }
    
    return render(request, 'ventas/venta_form.html', context)


@login_required
def registrar_venta(request):
    """Vista ajax para registrar una venta"""
    if request.method == 'POST':
        try:
            # Verifica si la caja esta abierta
            caja_activa = Cajas.objects.filter(estado_caja=1).first()
            if not caja_activa:
                return JsonResponse({
                    'success': False,
                    'message': 'No hay una caja abierta'
                })
            
            form = VentaForm(request.POST)
            if form.is_valid():
                producto_id = form.cleaned_data['producto']
                cantidad = form.cleaned_data['cantidad']
                
                # Obtener el producto por ID
                try:
                    producto = Productos.objects.get(id_prod=producto_id)
                except Productos.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': 'Producto no encontrado'
                    })

                #verificar el stock
                if producto.stock_prod < cantidad:
                    return JsonResponse({
                        'success': False,
                        'message': 'Stock insuficiente para el producto seleccionado'
                    })
                # Calcular totales
                precio_unitario = producto.precio_prod
                total_venta = precio_unitario * cantidad
                
                # Crear compra (venta desde perspectiva del sistema)
                # Obtener cliente por defecto (usar el primero disponible)
                cliente_defecto = Clientes.objects.first()
                if not cliente_defecto:
                    return JsonResponse({
                        'success': False,
                        'message': 'No hay clientes registrados en el sistema'
                    })
                
                compra = Compras.objects.create(
                    nombre_compra=f"Venta - {producto.nombre_prod}",
                    cantidad_compra=cantidad,
                    id_empleado_fk=caja_activa.id_emp_cj,
                    id_caja_fk=caja_activa,
                    id_cliente_fk=cliente_defecto,
                    fecha_compra=timezone.now().date(),
                    precio_compra=total_venta,
                    descripcion_compra=f"Venta de {cantidad} {producto.nombre_prod}",
                    estado_compra=1
                )
                
                # DEBUGGING: Intentar crear detalle con información de error detallada
                detalle_creado = False
                error_info = ""
                
                try:
                    # Método 1: SQL directo más simple
                    from django.db import connection
                    cursor = connection.cursor()
                    
                    # Primero, verificar qué campos tiene realmente la tabla
                    cursor.execute("SHOW COLUMNS FROM detalle_compras")
                    columnas = cursor.fetchall()
                    error_info += f"Columnas de la tabla: {columnas} | "
                    
                    # Intentar inserción más básica
                    cursor.execute("""
                        INSERT INTO detalle_compras 
                        (Id_compra_dtc, Id_producto_dtc, Precio_unitario_dtc, 
                         Subtotal_dtc, Descuento_dtc, Total_dtc, 
                         Fecha_entrega_dtc, Descripcion_dtc, Estado_dtc)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                        compra.id_compra, 
                        producto.id_prod, 
                        float(precio_unitario),
                        float(total_venta), 
                        0.0, 
                        float(total_venta),
                        timezone.now().date().strftime('%Y-%m-%d'), 
                        f"Detalle venta: {cantidad} x {producto.nombre_prod}",
                        1
                    ])
                    
                    detalle_creado = True
                    error_info += "SQL directo exitoso"
                    
                except Exception as sql_error:
                    error_info += f"Error SQL: {str(sql_error)} | "
                    
                    # Método 2: Intentar con ORM
                    try:
                        detalle = DetalleCompras.objects.create(
                            id_compra_dtc=compra,
                            id_producto_dtc=producto,
                            precio_unitario_dtc=precio_unitario,
                            subtotal_dtc=total_venta,
                            descuento_dtc=Decimal('0.00'),
                            total_dtc=total_venta,
                            fecha_entrega_dtc=timezone.now().date(),
                            descripcion_dtc=f"Detalle venta: {cantidad} x {producto.nombre_prod}",
                            estado_dtc=1
                        )
                        detalle_creado = True
                        error_info += "ORM exitoso"
                        
                    except Exception as orm_error:
                        error_info += f"Error ORM: {str(orm_error)}"
                
                # Actualizar stock y saldo
                producto.stock_prod -= cantidad
                producto.save()
                
                caja_activa.saldo_actual += total_venta
                caja_activa.save()

                # Respuesta basada en si se creó el detalle o no
                if detalle_creado:
                    return JsonResponse({
                        'success': True,
                        'mensaje': f'¡Venta registrada exitosamente! Total: {total_venta}',
                        'total': str(total_venta),
                        'nuevo_saldo': str(caja_activa.saldo_actual),
                        'stock_restante': producto.stock_prod,
                        'compra_id': compra.id_compra,
                        'debug_info': error_info
                    })
                else:
                    return JsonResponse({
                        'success': True,
                        'mensaje': f'Venta registrada (sin detalle). Total: {total_venta}',
                        'total': str(total_venta),
                        'nuevo_saldo': str(caja_activa.saldo_actual),
                        'stock_restante': producto.stock_prod,
                        'compra_id': compra.id_compra,
                        'warning': 'No se pudo crear el detalle de la venta',
                        'debug_info': error_info
                    })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Error en el formulario'
                })
        except Exception as e:
            import traceback
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}',
                'traceback': traceback.format_exc()
            })
    
    # Manejar GET para mostrar el formulario de ventas
    elif request.method == 'GET':
        # Verificar si hay caja abierta
        caja_activa = Cajas.objects.filter(estado_caja=1).first()
        
        # Obtener empleados y clientes para el formulario
        empleados = Empleados.objects.all()
        clientes = Clientes.objects.all()
        
        context = {
            'form_venta': VentaForm(),
            'empleados': empleados,
            'clientes': clientes,
            'caja_activa': caja_activa
        }
        
        return render(request, 'ventas/venta_form.html', context)
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


@login_required
def obtener_precio_producto(request):
    if request.method == 'GET':
        try:
            producto_id = request.GET.get('producto_id')
            if not producto_id:
                return JsonResponse({
                    'success': False,
                    'message': 'ID de producto no proporcionado'
                })
            
            producto = Productos.objects.get(id_prod=producto_id)
            return JsonResponse({
                'success': True,
                'precio': str(producto.precio_prod),
                'stock': producto.stock_prod,
                'nombre': producto.nombre_prod
            })
        except Productos.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Producto no encontrado'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}'
            })
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


@login_required
def listar_productos_modal(request):
    """Vista AJAX para obtener productos para el modal"""
    if request.method == 'GET':
        try:
            busqueda = request.GET.get('busqueda', '').strip()
            
            # Obtener productos activos con stock
            productos = Productos.objects.filter(
                estado_prod=1,
                stock_prod__gt=0,
                eliminado=False
            ).order_by('nombre_prod')
            
            # Aplicar filtro de búsqueda si existe
            if busqueda:
                productos = productos.filter(
                    nombre_prod__icontains=busqueda
                )
            
            # Convertir a lista de diccionarios
            productos_data = []
            for producto in productos:
                productos_data.append({
                    'id': producto.id_prod,
                    'nombre': producto.nombre_prod,
                    'precio': str(producto.precio_prod),
                    'stock': producto.stock_prod,
                    'categoria': producto.categoria_prod if hasattr(producto, 'categoria_prod') else 'Sin categoría'
                })
            
            return JsonResponse({
                'success': True,
                'productos': productos_data,
                'total': len(productos_data)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}',
                'productos': [],
                'total': 0
            })
    
    return JsonResponse({
        'success': False, 
        'message': 'Método no permitido',
        'productos': [],
        'total': 0
    })


@login_required
def procesar_venta_form(request):
    """Procesar venta desde formulario independiente"""
    if request.method == 'POST':
        try:
            # Verificar caja abierta
            caja_activa = Cajas.objects.filter(estado_caja=1).first()
            if not caja_activa:
                return JsonResponse({
                    'success': False,
                    'error': 'No hay ninguna caja abierta'
                })
            
            # Obtener datos del formulario
            producto_id = request.POST.get('producto')
            cantidad = int(request.POST.get('cantidad', 1))
            
            # Usar valores por defecto para empleado y cliente
            empleado_defecto = Empleados.objects.first()
            cliente_defecto = Clientes.objects.first()
            
            if not empleado_defecto or not cliente_defecto:
                return JsonResponse({
                    'success': False,
                    'error': 'Faltan datos básicos en el sistema (empleados/clientes)'
                })
            
            # Validar producto
            try:
                producto = Productos.objects.get(id_prod=producto_id)
            except Productos.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Producto no encontrado'
                })
            
            # Verificar stock
            if producto.stock_prod < cantidad:
                return JsonResponse({
                    'success': False,
                    'error': 'Stock insuficiente'
                })
            
            # Calcular totales
            precio_unitario = producto.precio_prod
            total_venta = precio_unitario * cantidad
            
            # Crear compra
            compra = Compras.objects.create(
                nombre_compra=f"Venta - {producto.nombre_prod}",
                cantidad_compra=cantidad,
                id_empleado_fk=empleado_defecto,
                id_caja_fk=caja_activa,
                id_cliente_fk=cliente_defecto,
                fecha_compra=timezone.now().date(),
                precio_compra=total_venta,
                descripcion_compra=f"Venta de {cantidad} {producto.nombre_prod}",
                estado_compra=1
            )
            
            # Intentar crear detalle de compra (mismo método que registrar_venta)
            try:
                from django.db import connection
                cursor = connection.cursor()
                
                cursor.execute("""
                    INSERT INTO detalle_compras 
                    (Id_compra_dtc, Id_producto_dtc, Precio_unitario_dtc, 
                     Subtotal_dtc, Descuento_dtc, Total_dtc, 
                     Fecha_entrega_dtc, Descripcion_dtc, Estado_dtc)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    compra.id_compra, 
                    producto.id_prod, 
                    float(precio_unitario),
                    float(total_venta), 
                    0.0, 
                    float(total_venta),
                    timezone.now().date().strftime('%Y-%m-%d'), 
                    f"Detalle venta: {cantidad} x {producto.nombre_prod}",
                    1
                ])
                
                # Actualizar stock
                producto.stock_prod -= cantidad
                producto.save()
                
                return JsonResponse({
                    'success': True,
                    'mensaje': f'Venta registrada correctamente. Total: ${total_venta}',
                    'compra_id': compra.id_compra,
                    'total': float(total_venta)
                })
                
            except Exception as detalle_error:
                # Si falla el detalle, eliminar la compra creada
                compra.delete()
                return JsonResponse({
                    'success': False,
                    'error': f'Error al crear detalle de venta: {str(detalle_error)}'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({
        'success': False, 
        'error': 'Método no permitido'
    })


@login_required
def exportar_ticket_pdf(request, compra_id):
    """
    Genera ticket PDF compacto usando ReportLab
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    
    try:
        compra = Compras.objects.select_related(
            'id_empleado_fk',
            'id_caja_fk'
        ).get(id_compra=compra_id)
        
        detalles = DetalleCompras.objects.filter(
            id_compra_dtc=compra
        ).select_related('id_producto_dtc')
        
    except Compras.DoesNotExist:
        return HttpResponse("Venta no encontrada", status=404)
    
    # Crear respuesta PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="ticket_{compra_id:05d}.pdf"'
    
    # Tamaño compacto: 80mm x altura automática
    ancho = 80 * mm
    alto = 150 * mm
    
    p = canvas.Canvas(response, pagesize=(ancho, alto))
    
    margen = 5 * mm
    y = alto - margen
    
    # ==========================================
    # 1. NOMBRE EMPRESA (centrado, grande)
    # ==========================================
    p.setFont("Helvetica-Bold", 16)
    texto = "ALMACANINA"
    ancho_texto = p.stringWidth(texto, "Helvetica-Bold", 16)
    p.drawString((ancho - ancho_texto) / 2, y, texto)
    y -= 20
    
    # Línea separadora
    p.line(margen, y, ancho - margen, y)
    y -= 15
    
    # ==========================================
    # 2. EMPLEADO
    # ==========================================
    p.setFont("Helvetica", 9)
    empleado = f"{compra.id_empleado_fk.nombre_emp} {compra.id_empleado_fk.apellido_emp}"
    p.drawString(margen, y, f"Empleado: {empleado}")
    y -= 12
    
    # ==========================================
    # 3. FECHA
    # ==========================================
    fecha = f"{compra.fecha_compra.strftime('%d/%m/%Y')} - {compra.hora_compra.strftime('%H:%M')}"
    p.drawString(margen, y, f"Fecha: {fecha}")
    y -= 15
    
    # Línea separadora
    p.line(margen, y, ancho - margen, y)
    y -= 15
    
    # ==========================================
    # 4. PRODUCTOS (compacto)
    # ==========================================
    p.setFont("Helvetica-Bold", 8)
    p.drawString(margen, y, "PRODUCTOS")
    y -= 12
    
    p.setFont("Helvetica", 7)
    for detalle in detalles:
        # Nombre producto
        nombre = str(detalle.id_producto_dtc.nombre_prod)
        if len(nombre) > 30:
            nombre = nombre[:27] + "..."
        
        p.drawString(margen + 2, y, f"{compra.cantidad_compra}x {nombre}")
        y -= 10
    
    y -= 5
    
    # ==========================================
    # 5. SUBTOTAL
    # ==========================================
    p.setFont("Helvetica", 9)
    p.drawString(margen, y, "Subtotal:")
    subtotal_texto = f"${compra.precio_compra:.2f}"
    ancho_subtotal = p.stringWidth(subtotal_texto, "Helvetica", 9)
    p.drawString(ancho - margen - ancho_subtotal, y, subtotal_texto)
    y -= 15
    
    # Línea doble
    p.line(margen, y, ancho - margen, y)
    y -= 2
    p.line(margen, y, ancho - margen, y)
    y -= 12
    
    # ==========================================
    # 6. TOTAL (destacado)
    # ==========================================
    p.setFont("Helvetica-Bold", 12)
    p.drawString(margen, y, "TOTAL:")
    total_texto = f"${compra.precio_compra:.2f}"
    ancho_total = p.stringWidth(total_texto, "Helvetica-Bold", 12)
    p.drawString(ancho - margen - ancho_total, y, total_texto)
    y -= 15
    
    # Línea final
    p.line(margen, y, ancho - margen, y)
    y -= 10
    
    # ==========================================
    # 7. MENSAJE FINAL (pequeño)
    # ==========================================
    p.setFont("Helvetica", 7)
    texto = "Gracias por su compra"
    ancho_texto = p.stringWidth(texto, "Helvetica", 7)
    p.drawString((ancho - ancho_texto) / 2, y, texto)
    
    # Finalizar
    p.showPage()
    p.save()
    
    return response


@login_required
def procesar_venta_pos(request):
    """Procesar venta desde el sistema POS con carrito múltiple"""
    if request.method == 'POST':
        try:
            # Verifica la caja abierta
            caja_activa = Cajas.objects.filter(estado_caja=1).first()
            if not caja_activa:
                return JsonResponse({
                    'success': False,
                    'error': 'No hay ninguna caja abierta'
                })
            
            # Obtener datos del carrito (JSON)
            carrito_data = json.loads(request.body)
            carrito = carrito_data.get('carrito', [])
            metodo_pago = carrito_data.get('metodo_pago', 'efectivo')
            
            if not carrito:
                return JsonResponse({
                    'success': False,
                    'error': 'El carrito está vacío'
                })
            
            # Obtener empleado del usuario actual
            try:
                empleado = request.user.empleados
            except Empleados.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Usuario no tiene empleado asociado'
                })
            
            # Obtener cliente por defecto
            cliente_defecto = Clientes.objects.first()
            if not cliente_defecto:
                return JsonResponse({
                    'success': False,
                    'error': 'No hay clientes registrados en el sistema'
                })
            
            total_venta = Decimal('0.00')
            productos_vendidos = []
            
            # Procesar cada producto del carrito
            for item in carrito:
                producto_id = item.get('producto_id')
                cantidad = int(item.get('cantidad', 1))
                
                # Validar producto
                try:
                    producto = Productos.objects.get(id_prod=producto_id)
                except Productos.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': f'Producto con ID {producto_id} no encontrado'
                    })
                
                # Verificar stock
                if producto.stock_prod < cantidad:
                    return JsonResponse({
                        'success': False,
                        'error': f'Stock insuficiente para {producto.nombre_prod}'
                    })
                
                # Calcular subtotal
                precio_unitario = producto.precio_prod
                subtotal = precio_unitario * cantidad
                total_venta += subtotal
                
                productos_vendidos.append({
                    'producto': producto,
                    'cantidad': cantidad,
                    'precio_unitario': precio_unitario,
                    'subtotal': subtotal
                })
            
            # Crear compra principal
            compra = Compras.objects.create(
                nombre_compra=f"Venta POS - {len(carrito)} productos",
                cantidad_compra=sum(item['cantidad'] for item in productos_vendidos),
                id_empleado_fk=empleado,
                id_caja_fk=caja_activa,
                id_cliente_fk=cliente_defecto,
                fecha_compra=timezone.now().date(),
                precio_compra=total_venta,
                descripcion_compra=f"Venta POS - Método: {metodo_pago.title()}",
                metodo_pago=metodo_pago,
                estado_compra=1
            )
            
            # Crear detalles de compra y actualizar stock
            try:
                from django.db import connection
                cursor = connection.cursor()
                
                for item in productos_vendidos:
                    producto = item['producto']
                    cantidad = item['cantidad']
                    precio_unitario = item['precio_unitario']
                    subtotal = item['subtotal']
                    
                    # Crear detalle
                    cursor.execute("""
                        INSERT INTO detalle_compras 
                        (Id_compra_dtc, Id_producto_dtc, Precio_unitario_dtc, 
                         Subtotal_dtc, Descuento_dtc, Total_dtc, 
                         Fecha_entrega_dtc, Descripcion_dtc, Estado_dtc)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                        compra.id_compra, 
                        producto.id_prod, 
                        float(precio_unitario),
                        float(subtotal), 
                        0.0, 
                        float(subtotal),
                        timezone.now().date().strftime('%Y-%m-%d'), 
                        f"POS: {cantidad} x {producto.nombre_prod}",
                        1
                    ])
                    
                    # Actualizar stock
                    producto.stock_prod -= cantidad
                    producto.save()
                
                # Actualizar saldo de caja
                caja_activa.saldo_actual += total_venta
                caja_activa.save()
                
                # Preparar información de productos con stock actualizado
                productos_actualizados = []
                for item in productos_vendidos:
                    productos_actualizados.append({
                        'id': item['producto'].id_prod,
                        'nombre': item['producto'].nombre_prod,
                        'nuevo_stock': item['producto'].stock_prod,
                        'cantidad_vendida': item['cantidad']
                    })
                
                return JsonResponse({
                    'success': True,
                    'mensaje': f'Venta procesada correctamente. Total: ${total_venta}',
                    'compra_id': compra.id_compra,
                    'total': float(total_venta),
                    'productos_vendidos': len(productos_vendidos),
                    'nuevo_saldo_caja': float(caja_activa.saldo_actual),
                    'productos_actualizados': productos_actualizados
                })
                
            except Exception as detalle_error:
                # Si falla, eliminar la compra creada
                compra.delete()
                return JsonResponse({
                    'success': False,
                    'error': f'Error al procesar detalles de venta: {str(detalle_error)}'
                })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Datos del carrito inválidos'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({
        'success': False, 
        'error': 'Método no permitido'
    })