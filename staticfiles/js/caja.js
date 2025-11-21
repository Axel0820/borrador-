// Archivo JavaScript para funcionalidad de caja
$(document).ready(function() {
    console.log('Sistema de Caja iniciado');
    
    // Event Listeners con delegación de eventos
    $(document).on('submit', '#formApertura', handleAperturaCaja);
    $(document).on('submit', '#formCierre', handleCierreCaja);
    $(document).on('submit', '#formVenta', handleRegistrarVenta);
    $(document).on('change', '#producto_id', actualizarPrecioProducto);
    $(document).on('input', '#id_cantidad', calcularTotalVenta);
    
    // Event Listeners para el modal de productos
    $(document).on('click', '#btnSeleccionarProducto', abrirModalProductos);
    $(document).on('input', '#buscarProducto', filtrarProductos);
    $(document).on('click', '.btn-seleccionar-producto', seleccionarProducto);
    $(document).on('shown.bs.modal', '#modalProductos', function() {
        $('#buscarProducto').focus();
    });

});

function handleAperturaCaja(e) {
    e.preventDefault();
    
    const formData = new FormData($('#formApertura')[0]);
    
    $.ajax({
        url: '/caja/abrir/',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.success) {
                alert('Éxito: ' + response.message);
                cargarContenido('/caja/', '#main-content');
            } else {
                alert('Error: ' + response.message);
            }
        },
        error: function(xhr, status, error) {
            alert('Error de conexión');
        }
    });
}

function handleCierreCaja(e) {
    e.preventDefault();
    
    if (confirm('¿Confirmar cierre de caja? Esta acción no se puede deshacer')) {
        const formData = new FormData($('#formCierre')[0]);
        
        $.ajax({
            url: '/caja/cerrar/',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.success) {
                    let mensaje = response.message;
                    if (response.diferencia && response.diferencia !== '0.00') {
                        mensaje += '\n\nDiferencia encontrada: $' + response.diferencia;
                        mensaje += '\nSaldo calculado: $' + response.saldo_calculado;
                        mensaje += '\nSaldo declarado: $' + response.saldo_declarado;
                    }
                    
                    alert(mensaje);
                    cargarContenido('/caja/', '#main-content');
                } else {
                    alert('Error: ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                alert('Error de conexión');
            }
        });
    }
}

function handleRegistrarVenta(e) {
    e.preventDefault();
    
    const producto = $('#producto_id').val();
    const cantidad = $('#id_cantidad').val();
    
    if (!producto || !cantidad) {
        alert('Por favor seleccione un producto y ingrese la cantidad');
        return;
    }
    
    if (cantidad <= 0) {
        alert('La cantidad debe ser mayor a 0');
        return;
    }
    
    const formData = new FormData($('#formVenta')[0]);
    
    $.ajax({
        url: '/caja/venta/',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.success) {
                alert('¡Venta registrada exitosamente!\n' + response.mensaje);
                
                // Limpiar formulario y campos
                $('#formVenta')[0].reset();
                $('#producto_id').val('');
                $('#productoSeleccionado').text('Seleccionar Producto');
                $('#infoProductoSeleccionado').hide();
                $('#precio_display').val('');
                $('#stock_display').val('');
                $('#total_display').val('');
                $('#btnRegistrarVenta').prop('disabled', true);
                
                // Recargar contenido para actualizar saldo
                cargarContenido('/caja/', '#main-content');
            } else {
                alert('Error: ' + response.message);
            }
        },
        error: function(xhr, status, error) {
            alert('Error de conexión');
        }
    });
}

function actualizarPrecioProducto() {
    const productoId = $('#producto_id').val();
    
    if (productoId) {
        $.ajax({
            url: '/caja/precio-producto/',
            type: 'GET',
            data: { 'producto_id': productoId },
            success: function(response) {
                if (response.success) {
                    $('#precio_display').val('$' + response.precio);
                    $('#stock_display').val(response.stock + ' unidades');
                    
                    // Habilitar botón de registrar venta si hay producto y cantidad
                    verificarFormularioCompleto();
                    
                    // Calcular total automáticamente si hay cantidad
                    calcularTotalVenta();
                } else {
                    $('#precio_display').val('');
                    $('#stock_display').val('');
                    $('#total_display').val('');
                    $('#btnRegistrarVenta').prop('disabled', true);
                    console.log('Error al obtener precio: ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                $('#precio_display').val('');
                $('#stock_display').val('');
                $('#total_display').val('');
                $('#btnRegistrarVenta').prop('disabled', true);
                console.log('Error de conexión al obtener precio');
            }
        });
    } else {
        // Limpiar campos si no hay producto seleccionado
        $('#precio_display').val('');
        $('#stock_display').val('');
        $('#total_display').val('');
        $('#btnRegistrarVenta').prop('disabled', true);
    }
}

function calcularTotalVenta() {
    const precioText = $('#precio_display').val();
    const cantidad = parseInt($('#id_cantidad').val()) || 0;
    
    if (precioText && cantidad > 0) {
        // Extraer el número del precio (quitar el símbolo $)
        const precio = parseFloat(precioText.replace('$', ''));
        
        if (!isNaN(precio)) {
            const total = precio * cantidad;
            $('#total_display').val('$' + total.toFixed(2));
        } else {
            $('#total_display').val('');
        }
    } else {
        $('#total_display').val('');
    }
    
    // Verificar si el formulario está completo
    verificarFormularioCompleto();
}

// ====== FUNCIONES PARA EL MODAL DE PRODUCTOS ======

function abrirModalProductos() {
    // Mostrar el modal
    $('#modalProductos').modal('show');
    
    // Cargar productos inmediatamente
    cargarProductosModal();
}

function cargarProductosModal(busqueda = '') {
    $.ajax({
        url: '/caja/productos-modal/',
        type: 'GET',
        data: { 'busqueda': busqueda },
        success: function(response) {
            if (response.success) {
                mostrarProductosEnModal(response.productos, response.total);
            } else {
                mostrarErrorEnModal(response.message);
            }
        },
        error: function(xhr, status, error) {
            mostrarErrorEnModal('Error de conexión');
        }
    });
}

function mostrarProductosEnModal(productos, total) {
    const listaContainer = $('#listaProductos');
    const contadorSpan = $('#contadorProductos');
    
    // Actualizar contador
    contadorSpan.text(`${total} producto(s) encontrado(s)`);
    
    if (productos.length === 0) {
        listaContainer.html(`
            <div class="text-center p-4">
                <i class="fas fa-search text-muted" style="font-size: 3rem;"></i>
                <p class="mt-2 text-muted">No se encontraron productos</p>
            </div>
        `);
        return;
    }
    
    let html = '';
    productos.forEach(function(producto) {
        html += `
            <div class="card mb-2 producto-item">
                <div class="card-body p-3">
                    <div class="row align-items-center">
                        <div class="col-md-6">
                            <h6 class="card-title mb-1">${producto.nombre}</h6>
                            <small class="text-muted">${producto.categoria}</small>
                        </div>
                        <div class="col-md-3 text-center">
                            <p class="mb-1"><strong>$${producto.precio}</strong></p>
                            <small class="text-muted">Stock: ${producto.stock}</small>
                        </div>
                        <div class="col-md-3 text-end">
                            <button type="button" class="btn btn-sm btn-primary btn-seleccionar-producto" 
                                    data-id="${producto.id}" 
                                    data-nombre="${producto.nombre}"
                                    data-precio="${producto.precio}"
                                    data-stock="${producto.stock}"
                                    data-categoria="${producto.categoria}">
                                <i class="fas fa-check"></i> Seleccionar
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    listaContainer.html(html);
}

function mostrarErrorEnModal(mensaje) {
    const listaContainer = $('#listaProductos');
    const contadorSpan = $('#contadorProductos');
    
    contadorSpan.text('Error al cargar');
    listaContainer.html(`
        <div class="text-center p-4">
            <i class="fas fa-exclamation-triangle text-warning" style="font-size: 3rem;"></i>
            <p class="mt-2 text-muted">${mensaje}</p>
        </div>
    `);
}

function filtrarProductos() {
    const busqueda = $('#buscarProducto').val().trim();
    cargarProductosModal(busqueda);
}

function seleccionarProducto() {
    const btn = $(this);
    const id = btn.data('id');
    const nombre = btn.data('nombre');
    const precio = btn.data('precio');
    const stock = btn.data('stock');
    const categoria = btn.data('categoria');
    
    // Actualizar campo oculto
    $('#producto_id').val(id);
    
    // Actualizar botón selector
    $('#productoSeleccionado').html(`<i class="fas fa-check-circle text-success"></i> ${nombre}`);
    
    // Mostrar información del producto
    $('#nombreProductoInfo').text(nombre);
    $('#categoriaProductoInfo').text(categoria);
    $('#infoProductoSeleccionado').show();
    
    // Actualizar campos de precio y stock
    $('#precio_display').val('$' + precio);
    $('#stock_display').val(stock + ' unidades');
    
    // Calcular total si hay cantidad
    calcularTotalVenta();
    
    // Cerrar modal
    $('#modalProductos').modal('hide');
    
    // Limpiar búsqueda para próxima vez
    $('#buscarProducto').val('');
}

function verificarFormularioCompleto() {
    const productoId = $('#producto_id').val();
    const cantidad = parseInt($('#id_cantidad').val()) || 0;
    
    const formularioCompleto = productoId && cantidad > 0;
    $('#btnRegistrarVenta').prop('disabled', !formularioCompleto);
}

// Función auxiliar para validar números
function esNumeroValido(valor) {
    return !isNaN(valor) && isFinite(valor) && valor > 0;
}

// Función para formatear números como moneda
function formatearMoneda(numero) {
    return '$' + parseFloat(numero).toFixed(2);
}
