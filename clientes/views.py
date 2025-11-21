from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q
from django import forms
from app.models import Clientes
from .forms import ClienteForm
from app.decorators import solo_gerente
from datetime import datetime
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# Vista principal - Listar clientes
@login_required
@solo_gerente
def listar_clientes(request):
    """Vista principal para listar clientes"""
    clientes = Clientes.objects.all().order_by('-id_cliente')
    
    estado = request.GET.get('estado', '')
    buscar = request.GET.get('buscar', '')
    
    if estado:
        clientes = clientes.filter(estado_cliente=int(estado))
    
    if buscar:
        clientes = clientes.filter(
            Q(nombre_cliente__icontains=buscar) |
            Q(apellido_cliente__icontains=buscar) |
            Q(dni_cliente__icontains=buscar) |
            Q(correo_clientes__icontains=buscar)
        )
    
    total_clientes = Clientes.objects.count()
    clientes_activos = Clientes.objects.filter(estado_cliente=1).count()
    clientes_inactivos = Clientes.objects.filter(estado_cliente=0).count()
    
    context = {
        'clientes': clientes,
        'total_clientes': total_clientes,
        'clientes_activos': clientes_activos,
        'clientes_inactivos': clientes_inactivos,
    }
    return render(request, 'clientes/listar.html', context)

@login_required
@solo_gerente
def crear_cliente(request):
    """Vista para crear nuevo cliente"""
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            try:
                # Intenta guardar, lo que ejecuta form.save() en forms.py
                cliente = form.save() 
                # Si es exitoso (manejo AJAX o normal)
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Cliente {cliente.nombre_cliente} {cliente.apellido_cliente} creado exitosamente'
                        })
                    messages.success(request, f'Cliente creado exitosamente')
                    return redirect('clientes:listar')
            except forms.ValidationError as e:
            # Captura el error de validación lanzado desde form.save()
            # Agrega los errores al formulario para que se muestren
                form.errors = e.message_dict
            else:
            # Si no es válido (manejo AJAX o normal, para errores de clean_field o Meta)
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    errors_dict = {field: errors[0] for field, errors in form.errors.items()}
                    return JsonResponse({
                        'success': False,
                        'errors': errors_dict
                    })
    else:
        form = ClienteForm()
    for field in form.fields.values():
        if 'class' not in field.widget.attrs:
            field.widget.attrs['class'] = 'form-control'
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, "clientes/form.html", {"form": form})
    return render(request, 'clientes/form.html', {"form": form})

@login_required
@solo_gerente
def editar_cliente(request, cliente_id):
    """Vista para editar cliente existente"""
    cliente = get_object_or_404(Clientes, pk=cliente_id)
    
    if request.method == "POST":
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            cliente = form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Cliente actualizado exitosamente'
                })
            messages.success(request, f'Cliente actualizado exitosamente')
            return redirect('clientes:listar')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors_dict = {field: errors[0] for field, errors in form.errors.items()}
                return JsonResponse({
                    'success': False,
                    'errors': errors_dict
                })
    else:
        form = ClienteForm(instance=cliente)
        
        # V-V-V INICIO DEL CÓDIGO NUEVO V-V-V
        # Al editar, ocultamos el campo de contraseña temporal
        # y nos aseguramos de que no sea requerido.
        if 'password_temporal' in form.fields:
            form.fields['password_temporal'].widget = forms.HiddenInput()
            form.fields['password_temporal'].required = False
        # ^-^-^ FIN DEL CÓDIGO NUEVO ^-^-^

        for field in form.fields.values():
            field.widget.attrs['class'] = 'form-control'
    
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return render(request, "clientes/editar.html", {"form": form, "cliente": cliente})

        return render(request, 'clientes/editar.html', {'form': form, 'cliente': cliente})

@login_required
@solo_gerente
@require_POST
def eliminar_cliente(request, cliente_id):
    """Vista para desactivar o eliminar cliente"""
    cliente = get_object_or_404(Clientes, pk=cliente_id)
    
    try:
        # Si el cliente está activo, solo desactivarlo
        if cliente.estado_cliente == 1:
            cliente.estado_cliente = 0
            cliente.save()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Cliente {cliente.nombre_cliente} {cliente.apellido_cliente} desactivado exitosamente'
                })
            
            messages.success(request, 'Cliente desactivado exitosamente')
            return redirect('clientes:listar')
        
        # Si el cliente ya está inactivo, eliminarlo permanentemente
        else:
            nombre_completo = f'{cliente.nombre_cliente} {cliente.apellido_cliente}'
            cliente.delete()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Cliente {nombre_completo} eliminado permanentemente'
                })
            
            messages.success(request, 'Cliente eliminado permanentemente')
            return redirect('clientes:listar')
            
    except Exception as e:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error al procesar: {str(e)}'
            })
        messages.error(request, f'Error al procesar cliente')
        return redirect('clientes:listar')

@login_required
@solo_gerente
def detalle_cliente(request, cliente_id):
    """Vista para mostrar detalle del cliente"""
    cliente = get_object_or_404(Clientes, pk=cliente_id)
    context = {
        'cliente': cliente
    }
    return render(request, 'clientes/detalle.html', context)

@login_required
@solo_gerente
def exportar_clientes_excel(request):
    """Vista para exportar clientes a PDF (activos, inactivos o todos)"""
    # Obtener el filtro de estado desde la URL (por defecto: activos)
    estado = request.GET.get('estado', '1')  # '1' = activos, '0' = inactivos, 'todos' = todos
    
    # Filtrar clientes según el estado
    if estado == 'todos':
        clientes = Clientes.objects.all().order_by('apellido_cliente', 'nombre_cliente')
        titulo_estado = "Todos los Clientes"
    elif estado == '0':
        clientes = Clientes.objects.filter(estado_cliente=0).order_by('apellido_cliente', 'nombre_cliente')
        titulo_estado = "Clientes Inactivos"
    else:  # Por defecto '1'
        clientes = Clientes.objects.filter(estado_cliente=1).order_by('apellido_cliente', 'nombre_cliente')
        titulo_estado = "Clientes Activos"
    
    # Crear buffer en memoria
    buffer = BytesIO()
    
    # Crear el PDF en orientación horizontal (landscape)
    from reportlab.lib.pagesizes import landscape
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=0.5*inch, bottomMargin=0.5*inch, 
                        leftMargin=0.5*inch, rightMargin=0.5*inch)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#6f00b5'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.grey,
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    # Título
    elements.append(Paragraph("ALMACANINA", title_style))
    elements.append(Paragraph(f"Lista de {titulo_estado}", subtitle_style))
    
    # Información adicional
    fecha_actual = datetime.now().strftime('%d/%m/%Y %H:%M')
    info_text = f"Fecha de generación: {fecha_actual} | Total de clientes: {clientes.count()}"
    elements.append(Paragraph(info_text, subtitle_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Crear datos de la tabla (igual que en la vista web)
    data = [['Nombre', 'Apellido', 'DNI', 'Email', 'Teléfono', 'Estado']]
    
    for cliente in clientes:
        estado = 'Activo' if cliente.estado_cliente == 1 else 'Inactivo'
        data.append([
            cliente.nombre_cliente,
            cliente.apellido_cliente,
            cliente.dni_cliente,
            cliente.correo_clientes if cliente.correo_clientes else 'N/A',
            cliente.telefono_cliente if cliente.telefono_cliente else 'N/A',
            estado
        ])
    
    # Crear tabla con anchos ajustados para landscape
    table = Table(data, colWidths=[1.5*inch, 1.5*inch, 1*inch, 2.2*inch, 1.2*inch, 0.8*inch])
    
    # Estilos de la tabla
    table.setStyle(TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6f00b5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Contenido
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # ID centrado
        ('ALIGN', (1, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        
        # Bordes
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        
        # Filas alternadas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
    ]))
    
    elements.append(table)
    
    # Generar PDF
    doc.build(elements)
    buffer.seek(0)
    
    # Crear respuesta HTTP
    fecha_archivo = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'clientes_almacanina_{fecha_archivo}.pdf'
    
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

@login_required
@solo_gerente
def exportar_cliente_excel(request, cliente_id):
    """Vista para exportar detalle de un cliente específico a PDF"""
    cliente = get_object_or_404(Clientes, pk=cliente_id)
    
    # Crear buffer en memoria
    buffer = BytesIO()
    
    # Crear el PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#6f00b5'),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=16,
        textColor=colors.HexColor('#6f00b5'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#6f00b5'),
        spaceAfter=15,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    # Encabezado
    elements.append(Paragraph("ALMACANINA", title_style))
    elements.append(Paragraph("Detalle de Cliente", subtitle_style))
    
    # Información adicional
    fecha_actual = datetime.now().strftime('%d/%m/%Y %H:%M')
    info_text = f"Fecha de generación: {fecha_actual}"
    info_style = ParagraphStyle('Info', parent=styles['Normal'], fontSize=10, textColor=colors.grey, alignment=TA_CENTER)
    elements.append(Paragraph(info_text, info_style))
    elements.append(Spacer(1, 0.4*inch))
    
    # Información Personal
    elements.append(Paragraph("Información Personal", section_style))
    
    data_personal = [
        ['ID de Cliente:', str(cliente.id_cliente)],
        ['Nombre:', cliente.nombre_cliente],
        ['Apellido:', cliente.apellido_cliente],
        ['DNI:', cliente.dni_cliente],
        ['Estado:', 'Activo' if cliente.estado_cliente else 'Inactivo'],
    ]
    
    table_personal = Table(data_personal, colWidths=[2*inch, 4*inch])
    table_personal.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    elements.append(table_personal)
    elements.append(Spacer(1, 0.3*inch))
    
    # Información de Contacto
    elements.append(Paragraph("Información de Contacto", section_style))
    
    data_contacto = [
        ['Teléfono:', cliente.telefono_cliente if cliente.telefono_cliente else 'No especificado'],
        ['Correo Electrónico:', cliente.correo_clientes if cliente.correo_clientes else 'No especificado'],
        ['Dirección:', cliente.direccion_cliente if cliente.direccion_cliente else 'No especificada'],
    ]
    
    table_contacto = Table(data_contacto, colWidths=[2*inch, 4*inch])
    table_contacto.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    elements.append(table_contacto)
    elements.append(Spacer(1, 0.3*inch))
    
    # Información del Sistema
    elements.append(Paragraph("Información del Sistema", section_style))
    
    fecha_registro = cliente.fecha_registro_cliente.strftime('%d/%m/%Y %H:%M') if cliente.fecha_registro_cliente else 'No disponible'
    
    data_sistema = [
        ['Fecha de Registro:', fecha_registro],
    ]
    
    table_sistema = Table(data_sistema, colWidths=[2*inch, 4*inch])
    table_sistema.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    elements.append(table_sistema)
    
    # Generar PDF
    doc.build(elements)
    buffer.seek(0)
    
    # Crear respuesta HTTP
    fecha_archivo = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'cliente_{cliente.apellido_cliente}_{cliente.nombre_cliente}_{fecha_archivo}.pdf'
    
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response
