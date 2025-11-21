from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q
from app.models import Proveedoress
from .forms import ProveedorForm
from app.decorators import solo_gerente
from datetime import datetime
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# Vista principal - Listar proveedores
@login_required
@solo_gerente
def listar_proveedores(request):
    """Vista principal para listar proveedores"""
    proveedores = Proveedoress.objects.all().order_by('-id_prov')
    
    estado = request.GET.get('estado', '')
    buscar = request.GET.get('buscar', '')
    
    if estado:
        proveedores = proveedores.filter(estado_prov=int(estado))
    
    if buscar:
        proveedores = proveedores.filter(
            Q(nombre_prov__icontains=buscar) |
            Q(cuit_prov__icontains=buscar) |
            Q(correo_prov__icontains=buscar)
        )
    
    total_proveedores = Proveedoress.objects.count()
    proveedores_activos = Proveedoress.objects.filter(estado_prov=1).count()
    proveedores_inactivos = Proveedoress.objects.filter(estado_prov=0).count()
    
    context = {
        'proveedores': proveedores,
        'total_proveedores': total_proveedores,
        'proveedores_activos': proveedores_activos,
        'proveedores_inactivos': proveedores_inactivos,
    }
    return render(request, 'proveedores/listar.html', context)

@login_required
@solo_gerente
def crear_proveedor(request):
    """Vista para crear nuevo proveedor"""
    if request.method == "POST":
        form = ProveedorForm(request.POST)
        if form.is_valid():
            proveedor = form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Proveedor {proveedor.nombre_prov} creado exitosamente'
                })
            messages.success(request, f'Proveedor creado exitosamente')
            return redirect('proveedores:listar')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors_dict = {field: errors[0] for field, errors in form.errors.items()}
                return JsonResponse({
                    'success': False,
                    'errors': errors_dict
                })
    else:
        form = ProveedorForm()
    
    for field in form.fields.values():
        if 'class' not in field.widget.attrs:
            field.widget.attrs['class'] = 'form-control'
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, "proveedores/form.html", {"form": form})
    
    return render(request, 'proveedores/form.html', {"form": form})

@login_required
@solo_gerente
def editar_proveedor(request, proveedor_id):
    """Vista para editar proveedor existente"""
    proveedor = get_object_or_404(Proveedoress, pk=proveedor_id)
    
    if request.method == "POST":
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            proveedor = form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Proveedor actualizado exitosamente'
                })
            messages.success(request, f'Proveedor actualizado exitosamente')
            return redirect('proveedores:listar')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors_dict = {field: errors[0] for field, errors in form.errors.items()}
                return JsonResponse({
                    'success': False,
                    'errors': errors_dict
                })
    else:
        form = ProveedorForm(instance=proveedor)
    
    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-control'
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, "proveedores/editar.html", {"form": form, "proveedor": proveedor})
    
    return render(request, 'proveedores/editar.html', {'form': form, 'proveedor': proveedor})

@login_required
@solo_gerente
@require_POST
def eliminar_proveedor(request, proveedor_id):
    """Vista para desactivar o eliminar proveedor"""
    proveedor = get_object_or_404(Proveedoress, pk=proveedor_id)
    
    try:
        # Si el proveedor está activo, solo desactivarlo
        if proveedor.estado_prov == 1:
            proveedor.estado_prov = 0
            proveedor.save()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Proveedor {proveedor.nombre_prov} desactivado exitosamente'
                })
            
            messages.success(request, 'Proveedor desactivado exitosamente')
            return redirect('proveedores:listar')
        
        # Si el proveedor ya está inactivo, eliminarlo permanentemente
        else:
            nombre_completo = f'{proveedor.nombre_prov}'
            proveedor.delete()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Proveedor {nombre_completo} eliminado permanentemente'
                })
            
            messages.success(request, 'Proveedor eliminado permanentemente')
            return redirect('proveedores:listar')
            
    except Exception as e:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error al procesar: {str(e)}'
            })
        messages.error(request, f'Error al procesar proveedor')
        return redirect('proveedores:listar')

@login_required
@solo_gerente
def detalle_proveedor(request, proveedor_id):
    """Vista para ver el detalle de un proveedor"""
    proveedor = get_object_or_404(Proveedoress, pk=proveedor_id)
    form = ProveedorForm(instance=proveedor)
    
    context = {
        'proveedor': proveedor,
        'form': form
    }
    return render(request, 'proveedores/detalle.html', context)

@login_required
@solo_gerente
def exportar_proveedores_pdf(request):
    """Exporta la lista de proveedores a PDF"""
    estado = request.GET.get('estado', '1')
    
    # Filtrar proveedores según estado
    if estado == 'todos':
        proveedores = Proveedoress.objects.all().order_by('nombre_prov')
        titulo = 'Todos los Proveedores'
    elif estado == '0':
        proveedores = Proveedoress.objects.filter(estado_prov=0).order_by('nombre_prov')
        titulo = 'Proveedores Inactivos'
    else:  # estado == '1'
        proveedores = Proveedoress.objects.filter(estado_prov=1).order_by('nombre_prov')
        titulo = 'Proveedores Activos'
    
    # Crear el HttpResponse con el PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="proveedores_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    # Crear el PDF en orientación horizontal
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#6f00b5'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Título
    elements.append(Paragraph(titulo, title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Datos de la tabla
    data = [['Nombre', 'CUIT', 'Email', 'Teléfono', 'Descripción', 'Estado']]
    
    for prov in proveedores:
        estado_texto = 'Activo' if prov.estado_prov == 1 else 'Inactivo'
        descripcion = prov.descripcion_prov[:50] + '...' if len(prov.descripcion_prov) > 50 else prov.descripcion_prov
        data.append([
            prov.nombre_prov,
            prov.cuit_prov,
            prov.correo_prov,
            prov.telefono_prov,
            descripcion,
            estado_texto
        ])
    
    # Crear tabla
    table = Table(data, colWidths=[2*inch, 1.5*inch, 2*inch, 1.3*inch, 2.5*inch, 0.8*inch])
    
    # Estilo de la tabla
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6f00b5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    elements.append(table)
    
    # Construir PDF
    doc.build(elements)
    
    # Obtener el valor del PDF
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response

@login_required
@solo_gerente
def exportar_proveedor_pdf(request, proveedor_id):
    """Exporta el detalle de un proveedor a PDF"""
    proveedor = get_object_or_404(Proveedoress, pk=proveedor_id)
    
    # Crear el HttpResponse con el PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="proveedor_{proveedor.nombre_prov}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    # Crear el PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#6f00b5'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#6f00b5'),
        spaceAfter=10,
        spaceBefore=20
    )
    
    # Título
    elements.append(Paragraph(f'Detalle del Proveedor', title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Información del Proveedor
    elements.append(Paragraph('Información del Proveedor', section_style))
    
    info_data = [
        ['Nombre:', proveedor.nombre_prov],
        ['CUIT:', proveedor.cuit_prov],
        ['Estado:', 'Activo' if proveedor.estado_prov == 1 else 'Inactivo'],
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Contacto
    elements.append(Paragraph('Contacto', section_style))
    
    contacto_data = [
        ['Email:', proveedor.correo_prov],
        ['Teléfono:', proveedor.telefono_prov],
    ]
    
    contacto_table = Table(contacto_data, colWidths=[2*inch, 4*inch])
    contacto_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(contacto_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Descripción
    if proveedor.descripcion_prov:
        elements.append(Paragraph('Descripción', section_style))
        
        desc_data = [[proveedor.descripcion_prov]]
        
        desc_table = Table(desc_data, colWidths=[6*inch])
        desc_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(desc_table)
    
    # Construir PDF
    doc.build(elements)
    
    # Obtener el valor del PDF
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response
