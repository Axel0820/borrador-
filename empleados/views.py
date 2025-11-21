from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from app.models import Empleados
from .forms import EmpleadoForm
from app.decorators import solo_gerente
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime


@login_required
@solo_gerente
def listar_empleados(request):
    """Vista principal para listar empleados - Solo Gerente"""
    # Por defecto mostrar solo empleados activos
    empleados = Empleados.objects.filter(activo=True).order_by('-id_emp')
    
    estado = request.GET.get('estado', '')
    buscar = request.GET.get('buscar', '')
    cargo = request.GET.get('cargo', '')
    
    # Permitir ver todos si se solicita explícitamente
    if estado == '':
        empleados = Empleados.objects.filter(activo=True).order_by('-id_emp')
    elif estado:
        empleados = Empleados.objects.filter(activo=bool(int(estado))).order_by('-id_emp')
    
    # Filtrar por cargo si se especifica
    if cargo:
        empleados = empleados.filter(cargo__iexact=cargo)
    
    # Filtrar por búsqueda usando Q para múltiples campos
    if buscar:
        from django.db.models import Q
        empleados = empleados.filter(
            Q(nombre_emp__icontains=buscar) |
            Q(apellido_emp__icontains=buscar) |
            Q(dni_emp__icontains=buscar) |
            Q(email__icontains=buscar) |
            Q(cargo__icontains=buscar)
        )
    
    # Contar estadísticas
    total = Empleados.objects.count()
    activos = Empleados.objects.filter(activo=True).count()
    inactivos = Empleados.objects.filter(activo=False).count()
    
    context = {
        'empleados': empleados,
        'total': total,
        'activos': activos,
        'inactivos': inactivos,
        'estado_filtro': estado,
        'buscar': buscar,
        'cargo_filtro': cargo,
    }
    
    return render(request, 'empleados/listar.html', context)

# @login_required  # Comentado temporalmente para debug
@login_required
@solo_gerente
def crear_empleado(request):
    """Vista para crear nuevo empleado - Solo Gerente"""
    if request.method == "POST":
        form = EmpleadoForm(request.POST, request.FILES)
        if form.is_valid():
            empleado = form.save(request=request)  # Pasar request para el email
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                response_data = {
                    'success': True,
                    'message': f'Empleado {empleado.nombre_emp} {empleado.apellido_emp} creado exitosamente'
                }
                
                # Agregar credenciales si se creó usuario
                if hasattr(form, 'temp_username') and hasattr(form, 'temp_password'):
                    response_data['credenciales'] = {
                        'usuario': form.temp_username,
                        'password': form.temp_password,
                        'mensaje': f'Se han generado las credenciales de acceso'
                    }
                    
                    if hasattr(form, 'email_sent'):
                        if form.email_sent:
                            response_data['credenciales']['email_status'] = 'enviado'
                            response_data['credenciales']['email_mensaje'] = 'Las credenciales se han enviado al correo'
                        else:
                            response_data['credenciales']['email_status'] = 'error'
                            response_data['credenciales']['email_mensaje'] = 'No se pudo enviar el correo. Entrega las credenciales manualmente.'
                
                return JsonResponse(response_data)
            
            messages.success(request, f'Empleado creado exitosamente')
            return redirect('empleados:listar')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors_dict = {field: errors[0] for field, errors in form.errors.items()}
                return JsonResponse({
                    'success': False,
                    'errors': errors_dict
                })
    else:
        form = EmpleadoForm()
    
    for field in form.fields.values():
        if 'class' not in field.widget.attrs:
            field.widget.attrs['class'] = 'form-control'
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, "empleados/form.html", {"form": form})
    
    return render(request, 'empleados/form.html', {"form": form})

@login_required
@solo_gerente
def editar_empleado(request, empleado_id):
    """Vista para editar empleado existente - Solo Gerente"""
    empleado = get_object_or_404(Empleados, pk=empleado_id)
    
    if request.method == "POST":
        # Guardar el cargo anterior para detectar cambios
        cargo_anterior = empleado.cargo
        
        form = EmpleadoForm(request.POST, request.FILES, instance=empleado)
        if form.is_valid():
            # Guardar el estado anterior
            estado_anterior = empleado.activo
            
            # Guardar el empleado
            empleado = form.save(commit=False)
            cargo_nuevo = empleado.cargo
            
            # Detectar si cambió el cargo
            cargo_cambio = cargo_anterior != cargo_nuevo
            
            empleado.save()
            
            # Si cambió el cargo y tiene usuario, actualizar grupo y enviar email
            if cargo_cambio and empleado.user and empleado.activo:
                # Eliminar grupos anteriores
                empleado.user.groups.clear()
                
                # Asignar nuevo grupo según el cargo
                form.assign_group_by_cargo(empleado.user, cargo_nuevo)
                
                # Generar nueva contraseña temporal
                nueva_password = form.generate_temporary_password(cargo_nuevo)
                empleado.user.set_password(nueva_password)
                empleado.user.save()
                
                # Marcar que debe cambiar contraseña
                empleado.force_password_change = True
                empleado.save()
                
                # Enviar email con nuevas credenciales solo si está activo
                if empleado.email:
                    form.send_credentials_email(
                        empleado, 
                        empleado.user.username, 
                        nueva_password, 
                        request
                    )
            
            # Si cambió de inactivo a activo, reactivar el usuario también
            if not estado_anterior and empleado.activo and empleado.user:
                empleado.user.is_active = True
                empleado.user.save()
            # Si cambió de activo a inactivo, desactivar el usuario también
            elif estado_anterior and not empleado.activo and empleado.user:
                empleado.user.is_active = False
                empleado.user.save()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Empleado actualizado exitosamente'
                })
            messages.success(request, f'Empleado actualizado exitosamente')
            return redirect('empleados:listar')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors_dict = {field: errors[0] for field, errors in form.errors.items()}
                return JsonResponse({
                    'success': False,
                    'errors': errors_dict
                })
    else:
        form = EmpleadoForm(instance=empleado)
    
    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-control'
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, "empleados/editar.html", {"form": form, "empleado": empleado})
    
    return render(request, 'empleados/editar.html', {'form': form, 'empleado': empleado})

@login_required
@solo_gerente
@require_POST
def eliminar_empleado(request, empleado_id):
    """Vista para desactivar empleado (soft delete) - Solo Gerente"""
    empleado = get_object_or_404(Empleados, pk=empleado_id)
    
    try:
        # Marcar como inactivo sin eliminar de la BD
        empleado.activo = False
        empleado.save()
        
        # También desactivar el usuario asociado si existe
        if empleado.user:
            empleado.user.is_active = False
            empleado.user.save()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Empleado {empleado.nombre_emp} {empleado.apellido_emp} desactivado exitosamente'
            })
        
        messages.success(request, 'Empleado desactivado exitosamente')
        return redirect('empleados:listar')
            
    except Exception as e:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error al desactivar empleado: {str(e)}'
            }, status=500)
        messages.error(request, f'Error al desactivar empleado: {str(e)}')
        return redirect('empleados:listar')

@login_required
@solo_gerente
@require_POST
def reactivar_empleado(request, empleado_id):
    """Vista para reactivar empleado inactivo - Solo Gerente"""
    empleado = get_object_or_404(Empleados, pk=empleado_id)
    
    try:
        # Reactivar empleado
        empleado.activo = True
        empleado.save()
        
        # También reactivar el usuario asociado si existe
        if empleado.user:
            empleado.user.is_active = True
            empleado.user.save()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Empleado {empleado.nombre_emp} {empleado.apellido_emp} reactivado exitosamente'
            })
        
        messages.success(request, 'Empleado reactivado exitosamente')
        return redirect('empleados:listar')
            
    except Exception as e:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error al reactivar empleado: {str(e)}'
            }, status=500)
        messages.error(request, f'Error al reactivar empleado: {str(e)}')
        return redirect('empleados:listar')

@login_required
@solo_gerente
def detalle_empleado(request, empleado_id):
    """Vista para mostrar detalle del empleado - Solo Gerente"""
    empleado = get_object_or_404(Empleados, pk=empleado_id)
    context = {
        'empleado': empleado
    }
    return render(request, 'empleados/detalle.html', context)

@login_required
@solo_gerente
def exportar_empleados_pdf(request):
    """Vista para exportar empleados a PDF (activos, inactivos o todos)"""
    estado = request.GET.get('estado', '1')
    
    # Filtrar empleados según el estado
    if estado == '1':
        empleados = Empleados.objects.filter(activo=True).order_by('apellido_emp', 'nombre_emp')
        titulo = "Lista de Empleados Activos"
    elif estado == '0':
        empleados = Empleados.objects.filter(activo=False).order_by('apellido_emp', 'nombre_emp')
        titulo = "Lista de Empleados Inactivos"
    else:
        empleados = Empleados.objects.all().order_by('apellido_emp', 'nombre_emp')
        titulo = "Lista de Todos los Empleados"
    
    # Crear buffer en memoria
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilo para el título
    titulo_style = ParagraphStyle(
        'TituloCustom',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#6f00b5'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Título
    elements.append(Paragraph(titulo, titulo_style))
    elements.append(Spacer(1, 12))
    
    # Crear tabla
    data = [['Nombre', 'Apellido', 'DNI', 'Cargo', 'Teléfono', 'Email', 'Estado']]
    
    for emp in empleados:
        data.append([
            emp.nombre_emp,
            emp.apellido_emp,
            emp.dni_emp,
            emp.cargo or 'N/A',
            emp.telefono or 'N/A',
            emp.email or 'N/A',
            'Activo' if emp.activo else 'Inactivo'
        ])
    
    # Crear la tabla
    tabla = Table(data, repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6f00b5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(tabla)
    
    # Información adicional
    elements.append(Spacer(1, 12))
    fecha_actual = datetime.now().strftime('%d/%m/%Y %H:%M')
    info_style = ParagraphStyle('InfoStyle', parent=styles['Normal'], fontSize=8, textColor=colors.grey)
    elements.append(Paragraph(f"Generado el: {fecha_actual} | Total de empleados: {empleados.count()}", info_style))
    
    # Construir PDF
    doc.build(elements)
    
    # Obtener el valor del PDF
    pdf = buffer.getvalue()
    buffer.close()
    
    # Crear respuesta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="empleados_{estado}.pdf"'
    response.write(pdf)
    
    return response

@login_required
@solo_gerente
def exportar_empleado_pdf(request, empleado_id):
    """Vista para exportar detalle de un empleado específico a PDF"""
    empleado = get_object_or_404(Empleados, pk=empleado_id)
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilo para el título
    titulo_style = ParagraphStyle(
        'TituloCustom',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#6f00b5'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Título
    elements.append(Paragraph("Detalle del Empleado", titulo_style))
    elements.append(Spacer(1, 12))
    
    # Agregar foto del empleado si existe
    if empleado.foto:
        try:
            import os
            from django.conf import settings
            
            # Construir la ruta completa de la imagen
            foto_path = os.path.join(settings.MEDIA_ROOT, str(empleado.foto))
            
            if os.path.exists(foto_path):
                # Crear imagen con tamaño fijo
                img = Image(foto_path, width=1.5*inch, height=1.5*inch)
                
                # Centrar la imagen
                img.hAlign = 'CENTER'
                elements.append(img)
                elements.append(Spacer(1, 12))
        except Exception as e:
            # Si hay error al cargar la imagen, continuar sin ella
            print(f"Error al cargar imagen: {e}")
    
    # Información del empleado
    data = [
        ['Nombre Completo:', f'{empleado.nombre_emp} {empleado.apellido_emp}'],
        ['DNI:', empleado.dni_emp],
        ['Sexo:', empleado.sexo_emp or 'N/A'],
        ['Cargo:', empleado.cargo or 'N/A'],
        ['Email:', empleado.email or 'N/A'],
        ['Teléfono:', empleado.telefono or 'N/A'],
        ['Dirección:', empleado.direccion or 'N/A'],
        ['Fecha de Ingreso:', empleado.fecha_ingreso.strftime('%d/%m/%Y') if empleado.fecha_ingreso else 'N/A'],
        ['Sueldo:', f'${empleado.sueldo}' if empleado.sueldo else 'N/A'],
        ['Estado:', 'Activo' if empleado.activo else 'Inactivo'],
    ]
    
    tabla = Table(data, colWidths=[2*inch, 4*inch])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0e6f6')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6f00b5')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(tabla)
    
    # Fecha de generación
    elements.append(Spacer(1, 12))
    fecha_actual = datetime.now().strftime('%d/%m/%Y %H:%M')
    info_style = ParagraphStyle('InfoStyle', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    elements.append(Paragraph(f"Documento generado el: {fecha_actual}", info_style))
    
    doc.build(elements)
    
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="empleado_{empleado.dni_emp}.pdf"'
    response.write(pdf)
    
    return response
