from django.shortcuts import render, redirect, get_object_or_404
from app.models import *
from .forms import ProductoForm
from .models import Productos
from django.db.models import Sum, IntegerField, F
from django.db.models.functions import Cast
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.utils import timezone
from django.db import transaction, IntegrityError
from .decorators import acceso_empleados, solo_gerente, solo_peluquero

def index(request):
    imagenes_carrusel = CarruselImagen.objects.filter(activo=True).order_by('id') 
    context = {
        'carrusel_imagenes': imagenes_carrusel # Variable usada en el template
    }
    return render(request, 'inicio.html', context)

def nosotros(request):
    return render(request, 'nosotros.html')

@login_required
def adm(request):
    return render(request, 'vadmin/adm.html')

@login_required
@acceso_empleados
def adm2(request):
    """Panel administrativo - Solo para empleados (no clientes)"""
    return render(request, 'vadmin/adm2.html')


######################################################PRODUCTOS#########################################


# Create views .
#----------------------------------------------------------CONTROL DE STOCK Y Productos-------------------------------------

@login_required
@solo_gerente
def listar_productos(request):
    """Inventario - Solo Gerente y Superadmin"""
    # Obtener todos los productos para calcular estadísticas correctas (excluyendo eliminados)
    todos_los_productos = Productos.objects.filter(eliminado=False)

    # Calcular estadísticas sobre TODOS los productos (sin filtros)
    total_productos = todos_los_productos.count()
    valor_inventario = todos_los_productos.aggregate(total=Sum('precio_prod'))['total'] or 0

    # Calcular productos con stock bajo usando el campo stock minimo de cada producto
    productos_con_stock_bajo = []
    for producto in todos_los_productos:
        try:
            stock_actual = int(producto.stock_prod) if producto.stock_prod is not None else 0
            stock_minimo = int(producto.stock_minimo) if producto.stock_minimo is not None else 10
            if stock_actual <= stock_minimo:
                productos_con_stock_bajo.append(producto)
        except (ValueError, TypeError):
            # Si hay error de conversión, usar valores por defecto
            if producto.stock_prod <= 10:  # fallback al valor por defecto
                productos_con_stock_bajo.append(producto)

    # Ahora aplicar filtros para la tabla (excluyendo eliminados)
    productos = Productos.objects.filter(eliminado=False)

    # Buscar por nombre
    buscar = request.GET.get('buscar')
    if buscar:
        productos = productos.filter(nombre_prod__icontains=buscar)

    # Filtrar por categoría
    categoria = request.GET.get('categoria')
    if categoria:
        productos = productos.filter(categoria_prod=categoria)

    # Filtrar por estado
    estado = request.GET.get('estado')
    if estado != '' and estado is not None:
        productos = productos.filter(estado_prod=estado)

    # Filtrar por stock bajo (usando stock_minimo de cada producto)
    stock_bajo_filter = request.GET.get("stock_bajo")
    if stock_bajo_filter == "1":
        productos = productos.filter(stock_prod__lte=F('stock_minimo'))

    # Ordenar a-z
    orden = request.GET.get('orden')
    if orden == "asc":
        productos = productos.order_by('nombre_prod')
    elif orden == "desc":
        productos = productos.order_by('-nombre_prod')
    else:
        # Por defecto, ordenar por ID descendente (productos nuevos primero)
        productos = productos.order_by('-id_prod')

    # Limitar a 10 productos para mostrar en la tabla
    productos = productos[:10]

    context = {
        "productos": productos,
        "total_productos": total_productos,
        "valor_inventario": valor_inventario,
        "stock_bajo": productos_con_stock_bajo,
    }
    return render(request, "productos/listar.html", context)


@login_required
@solo_gerente
def registrar_producto(request):
    if request.method == "POST":
        print("=== DEBUG REGISTRO PRODUCTO ===")
        print("POST data:", dict(request.POST))
        print("FILES data:", dict(request.FILES))
        print("Imagen en FILES:", 'imagen_prod' in request.FILES)

        if 'imagen_prod' in request.FILES:
            img = request.FILES['imagen_prod']
            print(f"Nombre archivo: {img.name}")
            print(f"Tamaño archivo: {img.size} bytes")
            print(f"Tipo contenido: {img.content_type}")

        form = ProductoForm(request.POST, request.FILES)
        print(f"Form válido: {form.is_valid()}")

        if form.is_valid():
            # Verificar si se ha subido una imagen o si se confirma guardar sin imagen
            if not request.FILES.get('imagen_prod') and not request.POST.get('confirm_no_image'):
                # Si no hay imagen y no se ha confirmado, mostrar confirmación
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'confirm_image': True,
                        'message': '¿Desea guardar este producto sin imagen? El producto se guardará en estado inactivo.'
                    })
                else:
                    # Para solicitudes no AJAX, redirigir con mensaje
                    from django.contrib import messages
                    messages.warning(request, '¿Desea guardar este producto sin imagen? El producto se guardará en estado inactivo.')
                    return render(request, "productos/form.html", {"form": form, "confirm_no_image": True})

            print("Guardando producto...")
            producto = form.save()

            # Si no hay imagen, establecer estado inactivo
            if not producto.imagen_prod:
                producto.estado_prod = 0  # Inactivo
                producto.save()

            print(f"Producto guardado con ID: {producto.id_prod}")
            print(f"Campo imagen_prod: {producto.imagen_prod}")
            print(f"Ruta imagen: {producto.imagen_prod.path if producto.imagen_prod else 'Sin imagen'}")
            print(f"URL imagen: {producto.imagen_prod.url if producto.imagen_prod else 'Sin imagen'}")

            # Verificar si el archivo existe físicamente
            if producto.imagen_prod:
                import os
                ruta_completa = producto.imagen_prod.path
                existe = os.path.exists(ruta_completa)
                print(f"Archivo existe en disco: {existe}")
                print(f"Ruta completa: {ruta_completa}")

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect("listarProductos")
        else:
            print("ERRORES EN EL FORMULARIO:")
            for field, errors in form.errors.items():
                print(f"  {field}: {errors}")
    else:
        form = ProductoForm()

    # Agrega la clase 'form-control' a cada campo
    for field in form.fields.values():
        if 'class' not in field.widget.attrs:
            field.widget.attrs['class'] = 'form-control'

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, "productos/form.html", {"form": form})
    return render(request, "productos/form.html", {"form": form})

# EDITAR PRODUCTO

@login_required
@solo_gerente
def editar_producto(request, pk):
    """Editar producto - Solo Gerente"""
    producto = get_object_or_404(Productos, pk=pk)

    # Verificar si es una solicitud POST para guardar el formulario IMPORTANTE
    if request.method == "POST":         #img l d abajo
        form = ProductoForm(request.POST,request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('listarProductos')
    else:
        # llamada AJAX) carga el formulario con los datos existentes
        form = ProductoForm(instance=producto)

    # Agrega la clase 'form-control' a cada campo IMPORTANTE
    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-control'

    # Si la solicitud es AJAX, devuelve solo el formulario.
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':

        return render(request, "productos/editar.html", {"form": form})

    #  AJAX,\
    return render(request, 'productos/editar.html', {'form': form})

#eliminar un producto
@login_required
@solo_gerente
def eliminar_producto(request, pk):
    """Eliminar producto lógicamente - Solo Gerente"""
    producto=get_object_or_404(Productos, pk=pk)
    producto.eliminado = True
    producto.save()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('listarProductos')


@login_required
@solo_gerente
def exportar_productos_pdf(request):
    # CREAR PDF productos con los mismos filtros aplicados en listar (excluyendo eliminados)
    productos = Productos.objects.filter(eliminado=False)

    buscar = request.GET.get('buscar')
    if buscar:
        productos = productos.filter(nombre_prod__icontains=buscar)

    categoria = request.GET.get('categoria')
    if categoria:
        productos = productos.filter(categoria_prod=categoria)

    estado = request.GET.get('estado')
    if estado != '' and estado is not None:
        productos = productos.filter(estado_prod=estado)

    # Filtrar por stock bajo (usando stock_minimo de cada producto) - IMPORTANTE: Agregar este filtro al PDF
    stock_bajo = request.GET.get("stock_bajo")
    if stock_bajo == "1":
        productos = productos.filter(stock_prod__lte=F('stock_minimo'))

    orden = request.GET.get('orden')
    if orden == "asc":
        productos = productos.order_by('nombre_prod')
    elif orden == "desc":
        productos = productos.order_by('-nombre_prod')

    # Crear respuesta PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="productos_{timezone.now().date()}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, height - 50, "Reporte de Productos")

    # Encabezados de la tabla (actualizados para coincidir con la tabla HTML)
    p.setFont("Helvetica-Bold", 9)
    y = height - 100
    p.drawString(30, y, "Nombre")
    p.drawString(130, y, "Precio")
    p.drawString(200, y, "Stock")
    p.drawString(260, y, "Categoria")
    p.drawString(330, y, "Unidad")
    p.drawString(420, y, "Proveedor")
    p.drawString(520, y, "Estado")

    # Datos
    p.setFont("Helvetica", 8)
    y -= 20
    for prod in productos:
        estado = "Activo" if prod.estado_prod == 1 else "Inactivo"

        # Nombre (truncar si es muy largo)
        nombre = str(prod.nombre_prod)[:25] + "..." if len(str(prod.nombre_prod)) > 25 else str(prod.nombre_prod)
        p.drawString(30, y, nombre)

        # Precio
        p.drawString(130, y, f"${prod.precio_prod}")

        # Stock
        p.drawString(200, y, str(prod.stock_prod))

        # Categoria
        categoria = str(prod.categoria_prod)[:15] + "..." if len(str(prod.categoria_prod)) > 15 else str(prod.categoria_prod)
        p.drawString(260, y, categoria)

        # Unidad
        if prod.unidad:
            unidad = str(prod.get_unidad_completa())[:25] + "..." if len(str(prod.get_unidad_completa())) > 25 else str(prod.get_unidad_completa())
        else:
            unidad = "Sin unidad"
        p.drawString(330, y, unidad)

        # Proveedor
        if prod.proveedor_prod:
            proveedor = str(prod.proveedor_prod)[:25] + "..." if len(str(prod.proveedor_prod)) > 25 else str(prod.proveedor_prod)
        else:
            proveedor = "Sin proveedor"
        p.drawString(420, y, proveedor)

        # Estado
        p.drawString(520, y, estado)

        y -= 18
        if y < 50:  # salto de página
            p.showPage()
            p.setFont("Helvetica-Bold", 9)
            p.drawString(30, height - 50, "Nombre")
            p.drawString(130, height - 50, "Precio")
            p.drawString(200, height - 50, "Stock")
            p.drawString(260, height - 50, "Categoria")
            p.drawString(330, height - 50, "Unidad")
            p.drawString(420, height - 50, "Proveedor")
            p.drawString(520, height - 50, "Estado")
            p.setFont("Helvetica", 8)
            y = height - 70

    p.save()
    return response
#---------------------------------------FIRNAL DE PRODUCTO--------------------------------------------------------------------
#productos de cliente
def catalogoprod(request):
    # Filtrar solo productos activos (estado_prod=1) que tienen imagen y no eliminados
    productos = Productos.objects.filter(estado_prod=1, imagen_prod__isnull=False, eliminado=False).order_by('categoria_prod', 'nombre_prod')

    # Obtener categorías disponibles para filtros
    categorias = Productos.objects.filter(estado_prod=1, eliminado=False).values_list('categoria_prod', flat=True).distinct().order_by('categoria_prod')

    # Agrupar productos por categoría
    productos_por_categoria = {}
    for categoria in categorias:
        productos_por_categoria[categoria] = productos.filter(categoria_prod=categoria)

    context = {
        'productos': productos,
        'categorias': categorias,
        'productos_por_categoria': productos_por_categoria,
    }
    return render(request, 'productocli/catalogoprod.html', context)

def carrito(request):
    return render(request, 'productocli/carrito.html')

def favorito(request):
    return render(request, 'productocli/favorito.html')

def alimento(request):
    return render(request, 'productocli/alimento.html')

def accesorio(request):
    return render(request, 'productocli/accesorio.html')

def juguete(request):
    return render(request, 'productocli/juguete.html')

def pipeta(request):
    return render(request, 'productocli/pipeta.html')

def pesca(request):
    return render(request, 'productocli/pesca.html')

def detalle_producto(request, producto_id):
    """Vista para mostrar detalles de un producto específico en el catálogo"""
    producto = get_object_or_404(Productos, pk=producto_id, estado_prod=1, eliminado=False)  # Solo productos activos y no eliminados

    # Preparar datos para respuesta JSON
    data = {
        'id': producto.id_prod,
        'nombre': producto.nombre_prod,
        'precio': float(producto.precio_prod),
        'categoria': producto.categoria_prod,
        'unidad': producto.get_unidad_completa(),
        'stock': producto.stock_prod,
        'proveedor': producto.proveedor_prod or '',
        'descripcion': producto.descripcion_prod or '',
        'imagen': producto.imagen_prod.url if producto.imagen_prod else '',
    }

    return JsonResponse(data)

def detalle(request):
    return render(request, 'productocli/detalle.html')


