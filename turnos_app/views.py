from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db import transaction, IntegrityError
from django.db.models import Q
from app.models import Turnos, Servicios
from app.decorators import solo_peluquero

@login_required
def turnos(request):
    # Obtener servicios activos para mostrar en el formulario
    servicios = Servicios.objects.filter(estado='Activo').order_by('nombre_servicio')
    context = {
        'servicios': servicios,
    }
    return render(request, 'turnoscli/turnos.html', context)

@login_required
def guardar_turno(request):
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)

            # Obtener el usuario actual (cliente)
            cliente = request.user

            with transaction.atomic():
                # Verificar si ya existe un turno (dentro de la transacción atómica)
                turno_existente = Turnos.objects.filter(
                    id_cliente=cliente.cliente_perfil,
                    fecha_turno=data['fecha_turno'],
                    hora_turno=data['hora_turno']
                ).first()

                if turno_existente:
                    return JsonResponse({
                        'success': False,
                        'error': 'Ya existe un turno para esta fecha y hora'
                    })

                # Crear el turno directamente con la información de la mascota
                turno = Turnos.objects.create(
                    nombre=data['nombre'],
                    tipo_turno=data['tipo'],
                    tamaño_turno=data['tamano'],
                    genero=data['genero'],
                    edad_turno=data.get('edad'),
                    observaciones_turno=data.get('observaciones', ''),
                    fecha_turno=data['fecha_turno'],
                    hora_turno=data['hora_turno'],
                    estado_turno='Pendiente',
                    id_cliente=cliente.cliente_perfil
                )

                # Agregar servicios al turno de forma segura
                servicios_nombres = data.get('servicios', [])
                servicios = []
                for servicio_nombre in servicios_nombres:
                    try:
                        servicio = Servicios.objects.get(nombre_servicio=servicio_nombre)
                        servicios.append(servicio)
                    except Servicios.DoesNotExist:
                        continue

                # Agregar todos los servicios en una sola operación
                if servicios:
                    turno.servicios.add(*servicios)

            return JsonResponse({'success': True, 'message': 'Turno guardado exitosamente'})

        except IntegrityError:
            # Si hay una violación de restricción única, informar que ya existe el turno
            return JsonResponse({'success': False, 'error': 'Turno duplicado detectado (integrity error)'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
@solo_peluquero
def turnosadm(request):
    from datetime import date

    # Obtener todos los turnos con información relacionada sin duplicados
    turnos = Turnos.objects.select_related('id_cliente').prefetch_related('servicios').order_by('fecha_turno', 'hora_turno').distinct()

    # Filtrar por búsqueda (nombre o correo) si se especifica
    busqueda = request.GET.get('busqueda')
    if busqueda:
        # Dividir la búsqueda en palabras individuales
        palabras = busqueda.split()
        query = Q()
        for palabra in palabras:
            query |= (
                Q(id_cliente__nombre_cliente__icontains=palabra) |
                Q(id_cliente__apellido_cliente__icontains=palabra) |
                Q(id_cliente__correo_clientes__icontains=palabra)
            )
        turnos = turnos.filter(query)

    # Filtrar por estado si se especifica
    estado = request.GET.get('estado')
    if estado:
        turnos = turnos.filter(estado_turno=estado)

    # Filtrar por fecha si se especifica, si no, mostrar turnos de hoy por defecto
    fecha = request.GET.get('fecha')
    if fecha:
        turnos = turnos.filter(fecha_turno=fecha)
    else:
        # Si no hay filtros aplicados, mostrar solo turnos de hoy
        turnos = turnos.filter(fecha_turno=date.today())

    # Verificar duplicados en consola
    turnos_list = list(turnos)
    ids_turnos = [t.id_turno for t in turnos_list]
    print(f"IDs de turnos en la consulta: {ids_turnos}")

    # Determinar la fecha para el contador (la fecha que se está mostrando actualmente)
    fecha_contador = fecha if fecha else date.today()

    # Contar turnos de la fecha que se está mostrando
    turnos_fecha_count = Turnos.objects.filter(fecha_turno=fecha_contador).count()

    context = {
        'turnos': turnos_list,
        'estados_turno': ['Pendiente', 'Confirmado', 'En curso', 'Completado', 'Cancelado', 'No asistió'],
        'turnos_fecha_count': turnos_fecha_count,
        'fecha_actual': fecha_contador,
    }
    return render(request, 'turnosAdm/turnoadm.html', context)

@login_required
@solo_peluquero
def detalles_turno(request, turno_id):
    try:
        turno = Turnos.objects.select_related('id_cliente').prefetch_related('servicios').get(id_turno=turno_id)

        data = {
            'success': True,
            'turno': {
                'id_turno': turno.id_turno,
                'cliente': {
                    'nombre': f"{turno.id_cliente.nombre_cliente} {turno.id_cliente.apellido_cliente}",
                    'email': turno.id_cliente.correo_clientes,
                    'telefono': getattr(turno.id_cliente, 'telefono_cliente', None)
                },
                'nombre': turno.nombre,
                'tipo_turno': turno.tipo_turno,
                'tamaño_turno': turno.tamaño_turno,
                'genero': turno.genero,
                'edad_turno': turno.edad_turno,
                'observaciones_turno': turno.observaciones_turno,
                'fecha_turno': turno.fecha_turno.strftime('%d/%m/%Y'),
                'hora_turno': turno.hora_turno.strftime('%H:%M'),
                'estado_turno': turno.estado_turno,
                'servicios': [{'nombre_servicio': s.nombre_servicio} for s in turno.servicios.all()],
                'motivo_cance_turno': turno.motivo_cance_turno
            }
        }
    except Turnos.DoesNotExist:
        data = {'success': False, 'error': 'Turno no encontrado'}
    except Exception as e:
        data = {'success': False, 'error': str(e)}

    return JsonResponse(data)

@login_required
def turnos_json(request):
    if request.method == 'GET':
        try:
            # Obtener todos los turnos que no estén cancelados o completados
            turnos = Turnos.objects.exclude(estado_turno__in=['Cancelado', 'Completado']).values(
                'fecha_turno', 'hora_turno'
            )

            # Formatear para FullCalendar
            events = []
            for turno in turnos:
                # Crear evento de día completo para bloquear la hora
                event = {
                    'title': '',  # Sin título para no mostrar texto
                    'start': f"{turno['fecha_turno']}T{turno['hora_turno']}",
                    'end': f"{turno['fecha_turno']}T{turno['hora_turno']}:59",  # Duración de 1 hora
                    'backgroundColor': 'transparent',  # Transparente para ocultar visualmente
                    'borderColor': 'transparent',
                    'textColor': 'transparent',
                    'display': 'block',  # Mantener bloqueo de selección
                    'editable': False,
                    'selectable': False
                }
                events.append(event)

            return JsonResponse(events, safe=False)

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
@solo_peluquero
def cambiar_estado_turno(request):
    if request.method == 'POST':
        try:
            turno_id = request.POST.get('turno_id')
            nuevo_estado = request.POST.get('estado')
            observaciones = request.POST.get('observaciones', '')

            turno = Turnos.objects.get(id_turno=turno_id)
            turno.estado_turno = nuevo_estado

            # Si se cancela el turno, guardar el motivo
            if nuevo_estado == 'Cancelado' and observaciones:
                turno.motivo_cance_turno = observaciones

            turno.save()

            return JsonResponse({'success': True, 'message': 'Estado del turno actualizado exitosamente'})

        except Turnos.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Turno no encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
@solo_peluquero
def turnosadm_json(request):
    if request.method == 'GET':
        try:
            # Obtener todos los turnos para el calendario de administración
            turnos = Turnos.objects.select_related('id_cliente').prefetch_related('servicios').values(
                'id_turno', 'fecha_turno', 'hora_turno', 'estado_turno', 'nombre',
                'id_cliente__nombre_cliente', 'id_cliente__apellido_cliente'
            )

            # Formatear para FullCalendar
            events = []
            for turno in turnos:
                # Definir colores por estado
                colores = {
                    'Pendiente': {'background': '#ffc107', 'border': '#ff8f00', 'text': '#000'},
                    'Confirmado': {'background': '#28a745', 'border': '#1e7e34', 'text': '#fff'},
                    'En curso': {'background': '#007bff', 'border': '#0056b3', 'text': '#fff'},
                    'Completado': {'background': '#6c757d', 'border': '#545b62', 'text': '#fff'},
                    'Cancelado': {'background': '#dc3545', 'border': '#bd2130', 'text': '#fff'},
                    'No asistió': {'background': '#6c757d', 'border': '#545b62', 'text': '#fff'},
                }

                color = colores.get(turno['estado_turno'], {'background': '#6c757d', 'border': '#545b62', 'text': '#fff'})

                # Crear evento
                event = {
                    'id': turno['id_turno'],
                    'title': f"{turno['estado_turno']} - {turno['nombre']}",
                    'start': f"{turno['fecha_turno']}T{turno['hora_turno']}",
                    'end': f"{turno['fecha_turno']}T{turno['hora_turno']}:59",  # Duración de 1 hora
                    'backgroundColor': color['background'],
                    'borderColor': color['border'],
                    'textColor': color['text'],
                    'extendedProps': {
                        'estado': turno['estado_turno'],
                        'cliente': f"{turno['id_cliente__nombre_cliente']} {turno['id_cliente__apellido_cliente']}",
                        'mascota': turno['nombre'],
                        'turno_id': turno['id_turno']
                    }
                }
                events.append(event)

            return JsonResponse(events, safe=False)

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
@solo_peluquero
def exportar_turnos_pdf(request):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from django.utils import timezone

    # Aplicar los mismos filtros que en turnosadm
    turnos = Turnos.objects.select_related('id_cliente').prefetch_related('servicios').order_by('fecha_turno', 'hora_turno').distinct()

    # Filtrar por búsqueda (nombre o correo) si se especifica
    busqueda = request.GET.get('busqueda')
    if busqueda:
        # Dividir la búsqueda en palabras individuales
        palabras = busqueda.split()
        query = Q()
        for palabra in palabras:
            query |= (
                Q(id_cliente__nombre_cliente__icontains=palabra) |
                Q(id_cliente__apellido_cliente__icontains=palabra) |
                Q(id_cliente__correo_clientes__icontains=palabra)
            )
        turnos = turnos.filter(query)

    # Filtrar por estado si se especifica
    estado = request.GET.get('estado')
    if estado:
        turnos = turnos.filter(estado_turno=estado)

    # Filtrar por fecha si se especifica, si no, mostrar turnos de hoy por defecto
    fecha = request.GET.get('fecha')
    if fecha:
        turnos = turnos.filter(fecha_turno=fecha)
    else:
        # Si no hay filtros aplicados, mostrar solo turnos de hoy
        from datetime import date
        turnos = turnos.filter(fecha_turno=date.today())

    # Crear respuesta PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="turnos_{timezone.now().date()}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, height - 50, "Reporte de Turnos")

    # Encabezados de la tabla
    p.setFont("Helvetica-Bold", 9)
    y = height - 100
    p.drawString(30, y, "Cliente")
    p.drawString(130, y, "Mascota")
    p.drawString(210, y, "Tipo")
    p.drawString(260, y, "Fecha")
    p.drawString(320, y, "Hora")
    p.drawString(370, y, "Estado")
    p.drawString(440, y, "Servicios")

    # Datos
    p.setFont("Helvetica", 8)
    y -= 20
    for turno in turnos:
        # Cliente (truncar si es muy largo)
        cliente = f"{turno.id_cliente.nombre_cliente} {turno.id_cliente.apellido_cliente}"
        cliente = cliente[:25] + "..." if len(cliente) > 25 else cliente
        p.drawString(30, y, cliente)

        # Mascota
        mascota = turno.nombre[:15] + "..." if len(turno.nombre) > 15 else turno.nombre
        p.drawString(130, y, mascota)

        # Tipo
        tipo = turno.tipo_turno[:10] + "..." if len(turno.tipo_turno) > 10 else turno.tipo_turno
        p.drawString(210, y, tipo)

        # Fecha
        p.drawString(260, y, turno.fecha_turno.strftime('%d/%m/%Y'))

        # Hora
        p.drawString(320, y, turno.hora_turno.strftime('%H:%M'))

        # Estado
        p.drawString(370, y, turno.estado_turno)

        # Servicios
        servicios = ", ".join([s.nombre_servicio for s in turno.servicios.all()])
        servicios = servicios[:25] + "..." if len(servicios) > 25 else servicios
        p.drawString(440, y, servicios if servicios else "Sin servicios")

        y -= 18
        if y < 50:  # salto de página
            p.showPage()
            p.setFont("Helvetica-Bold", 9)
            p.drawString(30, height - 50, "Cliente")
            p.drawString(130, height - 50, "Mascota")
            p.drawString(210, height - 50, "Tipo")
            p.drawString(260, height - 50, "Fecha")
            p.drawString(320, height - 50, "Hora")
            p.drawString(370, height - 50, "Estado")
            p.drawString(440, height - 50, "Servicios")
            p.setFont("Helvetica", 8)
            y = height - 70

    p.save()
    return response
