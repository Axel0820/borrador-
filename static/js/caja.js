// Archivo JavaScript para funcionalidad de caja

// Inicializar eventos de caja cuando se carga el contenido
function inicializarEventosCaja() {
    console.log('Inicializando eventos de caja...');
    
    // Restaurar pestaña activa
    restaurarPestanaActiva();
    
    // Inicializar event listeners
    inicializarEventListeners();
}

// Función para inicializar todos los event listeners
function inicializarEventListeners() {
    // Limpiar eventos anteriores para evitar duplicados
    $(document).off('.caja-events');
    
    // Event Listeners básicos
    $(document).on('submit.caja-events', '#formApertura', handleAperturaCaja);
    $(document).on('submit.caja-events', '#formCierre', handleCierreCaja);
    $(document).on('submit.caja-events', '#formVenta', handleRegistrarVenta);
    $(document).on('change.caja-events', '#producto_id', actualizarPrecioProducto);
    $(document).on('input.caja-events', '#id_cantidad', calcularTotalVenta);
    
    // Event Listeners para movimientos
    $(document).on('submit.caja-events', '#formRegistrarMovimiento', handleRegistrarMovimiento);
    $(document).on('click.caja-events', '.btn-anular-movimiento', handleAnularMovimiento);
    $(document).on('change.caja-events', '#id_tipo_movimiento', filtrarCategoriasPorTipo);
    
    // Event Listeners para modal de productos
    $(document).on('click.caja-events', '#btnSeleccionarProducto', abrirModalProductos);
    $(document).on('input.caja-events', '#buscarProducto', filtrarProductos);
    $(document).on('click.caja-events', '.btn-seleccionar-producto', seleccionarProducto);
    
    // Event Listeners para pestañas
    $(document).on('click.caja-events', '#tab-ventas, #tab-movimientos', function() {
        console.log('Click en pestaña - ocultando mensaje inicial');
        $('#mensaje-inicial').hide();
        localStorage.setItem('caja_tab_activa', '#' + this.id);
        console.log('Pestaña guardada:', '#' + this.id);
    });
    
    // Event Listeners para detalle de movimientos
    $(document).on('click.caja-events', '.btn-ver-detalle-movimiento', function() {
        const movimientoId = $(this).data('movimiento-id');
        const tipo = $(this).data('tipo');
        const categoria = $(this).data('categoria');
        const monto = $(this).data('monto');
        const descripcion = $(this).data('descripcion');
        const observaciones = $(this).data('observaciones');
        const fecha = $(this).data('fecha');
        const empleado = $(this).data('empleado');
        const esAutomatico = $(this).data('es-automatico');
        const idCompra = $(this).data('id-compra');
        
        if (idCompra) {
            cargarDetalleVenta(idCompra, tipo, categoria, monto, fecha, empleado);
        } else {
            mostrarDetalleMovimientoManual(movimientoId, tipo, categoria, monto, descripcion, observaciones, fecha, empleado);
        }
        
        $('#modalDetalleMovimiento').modal('show');
    });
    
    // Event Listeners para filtro de historial de cajas
    $(document).on('submit.caja-events', '#filtroFormHistorialCaja', handleFiltroHistorialCaja);
    $(document).on('click.caja-events', '#btnLimpiarHistorialCaja', handleLimpiarHistorialCaja);
    
    console.log('Event listeners de caja inicializados');
}

// Función para restaurar la pestaña activa
function restaurarPestanaActiva() {
    const tabActiva = localStorage.getItem('caja_tab_activa');
    if (tabActiva && $(tabActiva).length > 0) {
        $('#mensaje-inicial').hide();
        const tab = new bootstrap.Tab($(tabActiva)[0]);
        tab.show();
        console.log('Pestaña restaurada:', tabActiva);
    }
}

$(document).ready(function() {
    console.log('Sistema de Caja iniciado');
    
    // Inicializar eventos de caja
    inicializarEventosCaja();
    
    // Observer para detectar cuando se recarga el contenido de caja
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length > 0) {
                // Si se agregaron nodos, verificar si hay pestañas o formularios de caja
                if ($('#tab-ventas').length > 0 || $('#tab-movimientos').length > 0 || $('#formApertura').length > 0) {
                    console.log('Contenido de caja detectado, reinicializando...');
                    setTimeout(inicializarEventosCaja, 100);
                }
            }
        });
    });
    
    // Observar cambios en #contenidoDinamico o #main-content
    const targetNode = document.getElementById('contenidoDinamico') || document.getElementById('main-content');
    if (targetNode) {
        observer.observe(targetNode, { childList: true, subtree: true });
    }
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

// ====== FUNCIONES PARA VER DETALLE DE MOVIMIENTOS ======
// (Movido a event listeners globales)


function cargarDetalleVenta(idCompra, tipo, categoria, monto, fecha, empleado) {
    $('#tituloDetalleMovimiento').html(`<i class="bi bi-receipt"></i> Detalle de Venta #${idCompra}`);
    
    $.ajax({
        url: `/caja/detalle-venta/${idCompra}/`,
        method: 'GET',
        success: function(response) {
            let html = `
                <div class="row mb-3">
                    <div class="col-md-6">
                        <p class="mb-1"><strong>Fecha:</strong> ${fecha}</p>
                        <p class="mb-1"><strong>Empleado:</strong> ${empleado}</p>
                        <p class="mb-1"><strong>Cliente:</strong> ${response.cliente}</p>
                    </div>
                    <div class="col-md-6 text-end">
                        <p class="mb-1"><strong>Categoría:</strong> <span class="badge bg-primary">${categoria}</span></p>
                        <p class="mb-1"><strong>Tipo:</strong> <span class="badge bg-success">${tipo.toUpperCase()}</span></p>
                        <h4 class="text-success">Total: $${parseFloat(monto).toFixed(2)}</h4>
                    </div>
                </div>
                
                <hr>
                
                <h6 class="mb-3">Productos vendidos:</h6>
                <div class="table-responsive">
                    <table class="table table-sm table-bordered">
                        <thead class="table-light">
                            <tr>
                                <th>Producto</th>
                                <th class="text-center">Cantidad</th>
                                <th class="text-end">Precio Unit.</th>
                                <th class="text-end">Subtotal</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            response.detalles.forEach(detalle => {
                html += `
                    <tr>
                        <td>${detalle.producto}</td>
                        <td class="text-center">${detalle.cantidad}</td>
                        <td class="text-end">$${parseFloat(detalle.precio_unitario).toFixed(2)}</td>
                        <td class="text-end fw-bold">$${parseFloat(detalle.subtotal).toFixed(2)}</td>
                    </tr>
                `;
            });
            
            html += `
                        </tbody>
                        <tfoot class="table-light">
                            <tr>
                                <td colspan="3" class="text-end"><strong>TOTAL:</strong></td>
                                <td class="text-end"><strong>$${parseFloat(response.total).toFixed(2)}</strong></td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
                
                ${response.metodo_pago ? `<p class="mt-3 text-muted"><small><i class="bi bi-credit-card"></i> Método de pago: <strong>${response.metodo_pago}</strong></small></p>` : ''}
            `;
            
            $('#contenidoDetalleMovimiento').html(html);
        },
        error: function() {
            $('#contenidoDetalleMovimiento').html(
                '<div class="alert alert-danger"><i class="bi bi-exclamation-triangle"></i> Error al cargar el detalle de la venta</div>'
            );
        }
    });
}

function mostrarDetalleMovimientoManual(movimientoId, tipo, categoria, monto, descripcion, observaciones, fecha, empleado) {
    const tipoBadge = tipo === 'ingreso' ? 'bg-success' : 'bg-danger';
    const tipoIcono = tipo === 'ingreso' ? 'arrow-down-circle' : 'arrow-up-circle';
    const signo = tipo === 'ingreso' ? '+' : '-';
    
    $('#tituloDetalleMovimiento').html(`<i class="bi bi-${tipoIcono}"></i> Detalle de ${tipo.charAt(0).toUpperCase() + tipo.slice(1)}`);
    
    let html = `
        <div class="row mb-3">
            <div class="col-md-6">
                <p class="mb-2"><strong>Fecha:</strong> ${fecha}</p>
                <p class="mb-2"><strong>Empleado:</strong> ${empleado}</p>
                <p class="mb-2"><strong>Categoría:</strong> <span class="badge bg-secondary">${categoria}</span></p>
            </div>
            <div class="col-md-6 text-end">
                <p class="mb-2"><strong>Tipo:</strong> <span class="badge ${tipoBadge}">${tipo.toUpperCase()}</span></p>
                <h3 class="text-${tipo === 'ingreso' ? 'success' : 'danger'}">${signo}$${parseFloat(monto).toFixed(2)}</h3>
            </div>
        </div>
        
        <hr>
        
        <div class="mb-3">
            <h6>Descripción:</h6>
            <p class="border rounded p-3 bg-light">${descripcion || 'Sin descripción'}</p>
        </div>
    `;
    
    if (observaciones) {
        html += `
            <div class="mb-3">
                <h6>Observaciones:</h6>
                <p class="border rounded p-3 bg-light">${observaciones}</p>
            </div>
        `;
    }
    
    html += `
        <div class="alert alert-info mb-0">
            <small><i class="bi bi-info-circle"></i> Movimiento ID: #${movimientoId}</small>
        </div>
    `;
    
    $('#contenidoDetalleMovimiento').html(html);
}

// ====== FUNCIONES PARA MOVIMIENTOS DE CAJA ======

function handleRegistrarMovimiento(e) {
    e.preventDefault();
    
    const formData = new FormData($('#formRegistrarMovimiento')[0]);
    
    $.ajax({
        url: '/caja/movimientos/registrar/',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.success) {
                Swal.fire({
                    icon: 'success',
                    title: '¡Éxito!',
                    text: response.message,
                    showConfirmButton: false,
                    timer: 1500
                });
                
                // Recargar contenido de caja
                setTimeout(function() {
                    cargarContenido('/caja/');
                }, 1500);
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: response.message
                });
            }
        },
        error: function(xhr, status, error) {
            Swal.fire({
                icon: 'error',
                title: 'Error de conexión',
                text: 'No se pudo registrar el movimiento'
            });
        }
    });
}

function handleAnularMovimiento(e) {
    e.preventDefault();
    
    const movimientoId = $(this).data('movimiento-id');
    
    Swal.fire({
        title: '¿Anular movimiento?',
        text: "Esta acción no se puede deshacer",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sí, anular',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: `/caja/movimientos/anular/${movimientoId}/`,
                type: 'POST',
                headers: {
                    'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
                },
                success: function(response) {
                    if (response.success) {
                        Swal.fire({
                            icon: 'success',
                            title: '¡Anulado!',
                            text: response.message,
                            showConfirmButton: false,
                            timer: 1500
                        });
                        
                        // Remover la fila de la tabla
                        $(`tr[data-movimiento-id="${movimientoId}"]`).fadeOut(300, function() {
                            $(this).remove();
                        });
                        
                        // Recargar después de un momento
                        setTimeout(function() {
                            cargarContenido('/caja/');
                        }, 1500);
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: response.message
                        });
                    }
                },
                error: function(xhr, status, error) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error de conexión',
                        text: 'No se pudo anular el movimiento'
                    });
                }
            });
        }
    });
}

// ====== FUNCIÓN PARA FILTRAR CATEGORÍAS SEGÚN TIPO DE MOVIMIENTO ======

function filtrarCategoriasPorTipo() {
    const tipoMovimiento = $('#id_tipo_movimiento').val();
    const selectCategoria = $('#id_categoria');
    
    // Limpiar opciones actuales
    selectCategoria.empty();
    
    // Definir categorías según tipo
    const categoriasIngreso = [
        { value: 'venta', text: 'Venta' },
        { value: 'otros_ingresos', text: 'Otros Ingresos' }
    ];
    
    const categoriasEgreso = [
        { value: 'servicios', text: 'Pago Servicios' },
        { value: 'otros_egresos', text: 'Otros Egresos' }
    ];
    
    // Si no hay tipo seleccionado, deshabilitar categoría
    if (!tipoMovimiento) {
        selectCategoria.append('<option value="">Seleccione un tipo primero</option>');
        selectCategoria.prop('disabled', true);
        return;
    }
    
    // Habilitar el select de categoría
    selectCategoria.prop('disabled', false);
    
    // Seleccionar las categorías apropiadas
    let categorias = [];
    if (tipoMovimiento === 'ingreso') {
        categorias = categoriasIngreso;
    } else if (tipoMovimiento === 'egreso') {
        categorias = categoriasEgreso;
    }
    
    // Agregar opción por defecto
    selectCategoria.append('<option value="">---------</option>');
    
    // Agregar las categorías filtradas
    categorias.forEach(function(categoria) {
        selectCategoria.append(`<option value="${categoria.value}">${categoria.text}</option>`);
    });
    
    console.log('Categorías filtradas para tipo:', tipoMovimiento);
}

// ====== FUNCIONES PARA FILTRO DE HISTORIAL DE CAJAS ======

function handleFiltroHistorialCaja(e) {
    e.preventDefault();
    console.log('Filtrando historial de cajas...');
    
    const formData = $(this).serialize();
    const actionUrl = $(this).attr('action');
    
    console.log('FormData:', formData);
    console.log('Action URL:', actionUrl);
    
    // Usar cargarContenido si existe, sino AJAX directo
    if (typeof cargarContenido === 'function') {
        cargarContenido(actionUrl + '?' + formData);
    } else {
        $.ajax({
            url: actionUrl + '?' + formData,
            type: 'GET',
            headers: {'X-Requested-With': 'XMLHttpRequest'},
            success: function(data) {
                $('#contenidoDinamico').html(data);
            },
            error: function() {
                console.error('Error al cargar el historial filtrado');
            }
        });
    }
}

function handleLimpiarHistorialCaja(e) {
    e.preventDefault();
    console.log('Limpiando filtros de historial...');
    
    // Limpiar formulario
    $('#filtroFormHistorialCaja')[0].reset();
    
    // Recargar sin filtros
    if (typeof cargarContenido === 'function') {
        cargarContenido('/caja/');
    } else {
        $.ajax({
            url: '/caja/',
            type: 'GET',
            headers: {'X-Requested-With': 'XMLHttpRequest'},
            success: function(data) {
                $('#contenidoDinamico').html(data);
            },
            error: function() {
                console.error('Error al recargar la caja');
            }
        });
    }
}

