// Sistema POS - Punto de Venta
// Variables globales del carrito
let carritoItems = [];
let metodoPagoActual = 'efectivo';
let posYaInicializado = false;
let restaurandoCarrito = false;

// Inicializar carrito POS cuando el DOM y POS_CONFIG estén listos
$(document).ready(function() {
    console.log('Iniciando carrito POS...');
    
    const checkPOSConfig = setInterval(() => {
        if (window.POS_CONFIG && document.querySelector('.pos-container')) {
            clearInterval(checkPOSConfig);
            console.log('POS_CONFIG encontrado, inicializando carrito...');
            inicializarCarritoPOS();
        }
    }, 100);
    
    // Observer para detectar cuando se recarga la vista de ventas
    let timeoutRestaurar = null;
    let ultimaRestauracion = 0;
    const observarVentas = new MutationObserver(function(mutations) {
        // Evitar procesar si ya estamos restaurando
        if (restaurandoCarrito) return;
        
        // Cancelar timeout anterior si existe
        if (timeoutRestaurar) {
            clearTimeout(timeoutRestaurar);
        }
        
        // Esperar a que terminen todos los cambios del DOM (debounce)
        timeoutRestaurar = setTimeout(() => {
            const ahora = Date.now();
            // No restaurar si lo hicimos hace menos de 500ms
            if (ahora - ultimaRestauracion < 500) {
                return;
            }
            
            const posContainer = document.querySelector('.pos-container');
            const carritoContainer = document.getElementById('carrito-items');
            
            if (posContainer && carritoContainer && posYaInicializado && carritoItems.length > 0) {
                // Solo restaurar si el DOM del carrito está vacío pero tenemos items en memoria
                const itemsEnDOM = carritoContainer.querySelectorAll('.carrito-item').length;
                
                if (itemsEnDOM === 0) {
                    restaurandoCarrito = true;
                    ultimaRestauracion = ahora;
                    console.log('Vista de ventas detectada, restaurando carrito...');
                    
                    actualizarCarrito();
                    actualizarDisplayMetodo();
                    console.log('Carrito restaurado con', carritoItems.length, 'items');
                    
                    setTimeout(() => {
                        restaurandoCarrito = false;
                    }, 300);
                } else {
                    console.log('Carrito ya visible en DOM, no es necesario restaurar');
                }
            }
        }, 200);
    });
    
    // Observar cambios en el contenedor principal
    const contenedor = document.getElementById('contenidoDinamico') || document.getElementById('main-content');
    if (contenedor) {
        observarVentas.observe(contenedor, { childList: true, subtree: true });
        console.log('Observer de ventas activado');
    }
});

function inicializarCarritoPOS() {
    console.log('Inicializando carrito POS...');
    
    // Si ya fue inicializado, solo restaurar el carrito sin recrear listeners
    if (posYaInicializado) {
        console.log('POS ya inicializado anteriormente');
        return;
    }
    
    // Marcar como inicializado para evitar duplicar event listeners
    posYaInicializado = true;
    console.log('Primera inicialización - configurando event listeners');
    
    // Event Listeners solo del carrito (se registran UNA SOLA VEZ)
    $(document).on('click', '.btn-add-to-cart', function(e) {
        e.stopPropagation();
        let productoId = $(this).data('producto-id');
        if (!productoId) {
            productoId = $(this).closest('.product-card').data('id');
        }
        console.log('Botón agregar clickeado, producto ID:', productoId);
        agregarAlCarrito(productoId);
    });
    
    // Event Listeners del carrito
    $(document).on('click', '.quantity-btn', ajustarCantidadCarrito);
    $(document).on('click', '.btn-remove-item', eliminarDelCarrito);
    $(document).on('click', '#btn-procesar-venta', procesarVenta);
    $(document).on('click', '#btn-limpiar-carrito', limpiarCarrito);
    $(document).on('click', '#btn-cancelar-venta', cancelarVenta);
    $(document).on('click', '#btn-confirmar-venta', confirmarVenta);
    $(document).on('click', '#btn-confirmar-cantidad', confirmarCantidad);
    
    // Inicializar scroll del POS
    inicializarScrollPOS();
    
    // Restaurar carrito si tiene items
    if (carritoItems.length > 0) {
        actualizarCarrito();
        actualizarDisplayMetodo();
    }
    
    console.log('Carrito POS inicializado correctamente');
}

// Función para agregar producto al carrito
function agregarAlCarrito(productoId) {
    // Obtener datos directamente del DOM
    const $productCard = $(`.product-card[data-id="${productoId}"]`);
    
    if ($productCard.length === 0) {
        console.error('Producto no encontrado en DOM:', productoId);
        return;
    }
    
    const producto = {
        id: parseInt($productCard.data('id')),
        nombre: $productCard.data('nombre') || $productCard.find('.product-name').text().trim(),
        precio: parseFloat($productCard.data('precio')),
        stock: parseInt($productCard.data('stock'))
    };
    
    if (!producto.id || !producto.nombre || isNaN(producto.precio)) {
        console.error('Datos de producto inválidos:', producto);
        return;
    }
    
    if (producto.stock <= 0) {
        Swal.fire({
            title: 'Sin stock',
            text: 'Este producto no tiene stock disponible',
            icon: 'warning',
            confirmButtonText: 'Entendido'
        });
        return;
    }
    
    // Verificar si el producto ya está en el carrito
    const itemExistente = carritoItems.find(item => item.id == productoId);
    
    if (itemExistente) {
        // Verificar stock disponible
        if (itemExistente.cantidad >= producto.stock) {
            Swal.fire({
                title: 'Stock insuficiente',
                text: `Solo hay ${producto.stock} unidades disponibles`,
                icon: 'warning',
                confirmButtonText: 'Entendido'
            });
            return;
        }
        // Incrementar cantidad
        itemExistente.cantidad++;
    } else {
        // Agregar nuevo item al carrito
        carritoItems.push({
            id: producto.id,
            nombre: producto.nombre,
            precio: producto.precio,
            cantidad: 1,
            stock: producto.stock
        });
    }
    
    actualizarCarrito();
    console.log('Producto agregado al carrito:', producto.nombre);
}

function actualizarCarrito() {
    const carritoContainer = $('#carrito-items');
    
    if (carritoItems.length === 0) {
        carritoContainer.html(`
            <div class="carrito-empty">
                <i class="bi bi-cart-x"></i>
                <p>El carrito está vacío</p>
                <small>Agrega productos para comenzar</small>
            </div>
        `);
        $('#btn-procesar-venta').prop('disabled', true);
        actualizarTotales();
        return;
    }
    
    let html = '';
    carritoItems.forEach(item => {
        html += `
            <div class="carrito-item" data-producto-id="${item.id}">
                <div class="carrito-item-info">
                    <h6 class="carrito-item-name">${item.nombre}</h6>
                    <div class="carrito-item-price">$${item.precio.toFixed(2)}</div>
                </div>
                <div class="carrito-item-controls">
                    <button type="button" class="quantity-btn" data-action="decrease" data-producto-id="${item.id}">
                        <i class="bi bi-dash"></i>
                    </button>
                    <span class="quantity-display">${item.cantidad}</span>
                    <button type="button" class="quantity-btn" data-action="increase" data-producto-id="${item.id}">
                        <i class="bi bi-plus"></i>
                    </button>
                    <button type="button" class="btn-remove-item" data-producto-id="${item.id}">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
                <div class="item-total">$${(item.precio * item.cantidad).toFixed(2)}</div>
            </div>
        `;
    });
    
    carritoContainer.html(html);
    $('#btn-procesar-venta').prop('disabled', false);
    actualizarTotales();
}

function ajustarCantidadCarrito(e) {
    const productoId = $(e.target).closest('.quantity-btn').data('producto-id');
    const action = $(e.target).closest('.quantity-btn').data('action');
    const item = carritoItems.find(item => item.id == productoId);
    
    if (!item) return;
    
    if (action === 'increase') {
        if (item.cantidad >= item.stock) {
            Swal.fire({
                title: 'Stock insuficiente',
                text: `Solo hay ${item.stock} unidades disponibles`,
                icon: 'warning',
                confirmButtonText: 'Entendido'
            });
            return;
        }
        item.cantidad++;
    } else if (action === 'decrease') {
        if (item.cantidad > 1) {
            item.cantidad--;
        } else {
            // Si cantidad es 1, eliminar el item
            eliminarDelCarrito(e);
            return;
        }
    }
    
    actualizarCarrito();
}

function eliminarDelCarrito(e) {
    const productoId = $(e.target).closest('[data-producto-id]').data('producto-id');
    carritoItems = carritoItems.filter(item => item.id != productoId);
    actualizarCarrito();
}

function actualizarTotales() {
    // Actualizar totales individuales de items existentes
    carritoItems.forEach(item => {
        const total = item.precio * item.cantidad;
        $(`.carrito-item[data-producto-id="${item.id}"] .item-total`).text(`$${total.toFixed(2)}`);
    });
    
    // Calcular totales generales
    const subtotal = carritoItems.reduce((sum, item) => sum + (item.precio * item.cantidad), 0);
    const descuento = 0; // Por ahora sin descuentos
    const total = subtotal - descuento;
    
    // Actualizar siempre los totales, incluso si el carrito está vacío
    $('#carrito-subtotal').text(`$${subtotal.toFixed(2)}`);
    $('#carrito-descuento').text(`$${descuento.toFixed(2)}`);
    $('#carrito-total').text(`$${total.toFixed(2)}`);
}

function procesarVenta() {
    if (carritoItems.length === 0) {
        Swal.fire({
            title: 'Carrito vacío',
            text: 'Agrega productos antes de procesar la venta',
            icon: 'warning',
            confirmButtonText: 'Entendido'
        });
        return;
    }
    
    const total = carritoItems.reduce((sum, item) => sum + (item.precio * item.cantidad), 0);
    
    // Mostrar modal de confirmación
    const itemsList = carritoItems.map(item => 
        `<li>${item.nombre} x${item.cantidad} = $${(item.precio * item.cantidad).toFixed(2)}</li>`
    ).join('');
    
    // Obtener nombre del método de pago
    const nombres = {
        'efectivo': 'Efectivo',
        'transferencia': 'Transferencia',
        'tarjeta': 'Tarjeta'
    };
    
    $('#confirmacion-detalles').html(`
        <div class="venta-resumen">
            <h6>Resumen de la venta:</h6>
            <ul class="list-unstyled">
                ${itemsList}
            </ul>
            <hr>
            <div class="metodo-pago-confirmacion">
                <strong>Método de pago: ${nombres[metodoPagoActual] || 'Efectivo'}</strong>
            </div>
            <div class="total-confirmacion">
                <strong>Total: $${total.toFixed(2)}</strong>
            </div>
        </div>
    `);
    
    $('#modalConfirmacionVenta').modal('show');
}

function confirmarVenta() {
    const ventaData = {
        carrito: carritoItems.map(item => ({
            producto_id: item.id,
            cantidad: item.cantidad,
            precio: item.precio
        })),
        metodo_pago: metodoPagoActual
    };
    
    $.ajax({
        url: window.POS_CONFIG.procesarVentaUrl,
        type: 'POST',
        data: JSON.stringify(ventaData),
        contentType: 'application/json',
        headers: {
            'X-CSRFToken': window.POS_CONFIG.csrfToken
        },
        success: function(response) {
            if (response.success) {
                // Actualizar saldo en la interfaz
                if (response.nuevo_saldo_caja !== undefined) {
                    actualizarSaldoInterfaz(response.nuevo_saldo_caja);
                }
                
                // Actualizar stock de productos vendidos
                if (response.productos_actualizados && response.productos_actualizados.length > 0) {
                    actualizarStockProductos(response.productos_actualizados);
                }
                // aca se hace el estilo del modal
                Swal.fire({
                    icon: 'success',
                    title: '¡Venta exitosa!',
                    html: `
                        <div style="
                            background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
                            border-radius: 12px;
                            padding: 20px;
                            margin: 20px 0;
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        ">
                            <div style="
                                background: white;
                                border-radius: 8px;
                                padding: 15px;
                                margin-bottom: 15px;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                            ">
                                <p style="
                                    font-size: 18px;
                                    margin: 8px 0;
                                    color: #2e7d32;
                                    font-weight: bold;
                                ">
                                    <span style="color: #666;">Total:</span> $${response.total.toFixed(2)}
                                </p>
                                <div style="
                                    display: flex;
                                    justify-content: space-around;
                                    margin-top: 15px;
                                    padding-top: 15px;
                                    border-top: 2px dashed #e0e0e0;
                                ">
                                    <div style="text-align: center;">
                                        <p style="
                                            font-size: 12px;
                                            color: #999;
                                            margin: 0 0 5px 0;
                                            text-transform: uppercase;
                                            letter-spacing: 0.5px;
                                        ">Productos</p>
                                        <p style="
                                            font-size: 20px;
                                            font-weight: bold;
                                            color: #333;
                                            margin: 0;
                                        ">${response.productos_vendidos}</p>
                                    </div>
                                    <div style="
                                        width: 1px;
                                        background: #e0e0e0;
                                    "></div>
                                    <div style="text-align: center;">
                                        <p style="
                                            font-size: 12px;
                                            color: #999;
                                            margin: 0 0 5px 0;
                                            text-transform: uppercase;
                                            letter-spacing: 0.5px;
                                        ">Ticket</p>
                                        <p style="
                                            font-size: 20px;
                                            font-weight: bold;
                                            color: #333;
                                            margin: 0;
                                            font-family: 'Courier New', monospace;
                                        ">#${String(response.compra_id).padStart(5, '0')}</p>
                                    </div>
                                </div>
                            </div>
                            
                            <button 
                                onclick="descargarTicketPDF(${response.compra_id})" 
                                class="swal2-confirm swal2-styled" 
                                style="
                                    background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
                                    border: none;
                                    border-radius: 8px;
                                    padding: 12px 30px;
                                    font-size: 15px;
                                    font-weight: 600;
                                    box-shadow: 0 4px 12px rgba(25, 118, 210, 0.3);
                                    transition: all 0.3s ease;
                                    cursor: pointer;
                                    width: 100%;
                                    margin-top: 5px;
                                "
                                onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 16px rgba(25, 118, 210, 0.4)';"
                                onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(25, 118, 210, 0.3)';"
                            >
                                📄 Descargar Ticket PDF
                            </button>
                        </div>
                        
                        <p style="
                            font-size: 12px;
                            color: #999;
                            margin-top: 15px;
                            font-style: italic;
                        ">El ticket se descargará automáticamente al hacer clic</p>
                    `,
                    showConfirmButton: true,
                    confirmButtonText: 'Continuar',
                    confirmButtonColor: '#4caf50',
                    allowOutsideClick: false,
                    customClass: {
                        popup: 'swal-venta-exitosa',
                        confirmButton: 'btn-continuar-venta'
                    }
                }).then(() => {
                    carritoItems = [];
                    actualizarCarrito();
                    $('#modalConfirmacionVenta').modal('hide');
                });
            } else {
                Swal.fire({
                    title: 'Error en la venta',
                    text: response.error || response.message,
                    icon: 'error',
                    confirmButtonText: 'Entendido'
                });
            }
        },
        error: function() {
            Swal.fire({
                title: 'Error de conexión',
                text: 'No se pudo procesar la venta',
                icon: 'error',
                confirmButtonText: 'Entendido'
            });
        }
    });
}

function limpiarCarrito() {
    if (carritoItems.length === 0) {
        Swal.fire({
            title: 'Carrito vacío',
            text: 'No hay productos en el carrito',
            icon: 'info',
            confirmButtonText: 'Entendido',
        });
        return;
    }
    
    Swal.fire({
        title: '¿Limpiar carrito?',
        text: 'Se eliminarán todos los productos del carrito',
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Sí, limpiar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            carritoItems = [];
            actualizarCarrito();
        }
    });
}

function cancelarVenta() {
    $('#modalConfirmacionVenta').modal('hide');
}

function confirmarCantidad() {
    // Esta función se usaría para el modal de cantidad personalizada
    // Por ahora no está implementada en el HTML actual
    console.log('Confirmar cantidad personalizada');
}

// Función para actualizar el saldo en la interfaz después de una venta
function actualizarSaldoInterfaz(nuevoSaldo) {
    console.log('Actualizando saldo en interfaz:', nuevoSaldo);
    
    // Buscar el elemento que contiene el saldo en la información de sesión
    const $saldoContainer = $('.pos-session-info small').filter(function() {
        return $(this).text().includes('Saldo:');
    });
    
    if ($saldoContainer.length > 0) {
        // Formatear el saldo de forma simple
        const saldoFormateado = parseFloat(nuevoSaldo).toFixed(2);
        
        console.log('Saldo recibido:', nuevoSaldo);
        console.log('Saldo formateado:', saldoFormateado);
        console.log('Texto actual completo:', $saldoContainer.html());
        
        // En lugar de usar regex, obtener los datos del elemento y reconstruir
        const empleadoInfo = $saldoContainer.html().match(/<strong>Empleado:<\/strong>\s*([^|]+)\s*\|/);
        const cajaInfo = $saldoContainer.html().match(/<strong>Caja:<\/strong>\s*([^|]+)\s*\|/);
        
        if (empleadoInfo && cajaInfo) {
            const nuevoHTML = `
                <strong>Empleado:</strong> ${empleadoInfo[1].trim()} |
                <strong>Caja:</strong> ${cajaInfo[1].trim()} |
                <strong>Saldo:</strong> $${saldoFormateado}
            `;
            
            console.log('Nuevo HTML completo:', nuevoHTML);
            $saldoContainer.html(nuevoHTML);
        } else {
            console.warn('No se pudo parsear la información existente');
        }
        
        // Efecto visual sutil para indicar la actualización
        $saldoContainer.addClass('saldo-actualizado');
        setTimeout(() => {
            $saldoContainer.removeClass('saldo-actualizado');
        }, 2000);
        
        console.log(`Saldo actualizado exitosamente: $${saldoFormateado}`);
    } else {
        console.warn('No se encontró el elemento del saldo para actualizar');
    }
}

// Función para actualizar el stock de productos después de una venta
function actualizarStockProductos(productosActualizados) {
    console.log('Actualizando stock de productos:', productosActualizados);
    
    productosActualizados.forEach(producto => {
        const $productCard = $(`.product-card[data-id="${producto.id}"]`);
        
        if ($productCard.length > 0) {
            // Actualizar el texto del stock en la card
            const $stockElement = $productCard.find('.product-stock');
            $stockElement.text(`Stock: ${producto.nuevo_stock}`);
            
            // Actualizar el data-attribute para JavaScript
            $productCard.attr('data-stock', producto.nuevo_stock);
            
            // Efecto visual para mostrar la actualización
            $productCard.addClass('stock-actualizado');
            setTimeout(() => {
                $productCard.removeClass('stock-actualizado');
            }, 2000);
            
            // Si el stock llegó a 0, deshabilitar el botón
            const $addButton = $productCard.find('.btn-add-to-cart');
            if (producto.nuevo_stock <= 0) {
                $addButton.prop('disabled', true);
                $addButton.html('<i class="bi bi-x-circle"></i> Sin stock');
                $productCard.addClass('sin-stock');
            }
            
            console.log(`Stock actualizado para ${producto.nombre}: ${producto.nuevo_stock}`);
        } else {
            console.warn(`No se encontró product-card para ID: ${producto.id}`);
        }
    });
}

// ===========================
// FUNCIONES MÉTODO DE PAGO
// ===========================

// Función para abrir modal de selección de método
function abrirSeleccionMetodo() {
    console.log('Abriendo selección de método de pago...');
    
    // Marcar el método actual como seleccionado
    $(`input[name="metodo_seleccion"][value="${metodoPagoActual}"]`).prop('checked', true);
    
    // Mostrar modal
    $('#modalSeleccionarMetodo').modal('show');
}

// Función para confirmar método seleccionado
function confirmarMetodoSeleccionado() {
    console.log('Confirmando método de pago...');
    
    // Obtener método seleccionado
    const nuevoMetodo = $('input[name="metodo_seleccion"]:checked').val();
    
    if (nuevoMetodo) {
        metodoPagoActual = nuevoMetodo;
        actualizarDisplayMetodo();
        console.log('Método actualizado a:', metodoPagoActual);
    }
    
    // Cerrar modal
    $('#modalSeleccionarMetodo').modal('hide');
}

// Función para actualizar el display del método en el botón
function actualizarDisplayMetodo() {
    const nombres = {
        'efectivo': 'Efectivo',
        'transferencia': 'Transferencia',
        'tarjeta': 'Tarjeta'
    };
    
    $('#metodo-actual').text(nombres[metodoPagoActual] || 'Efectivo');
}

// Event listeners para método de pago
$(document).on('click', '#btn-seleccionar-metodo', abrirSeleccionMetodo);
$(document).on('click', '#btn-confirmar-metodo-seleccion', confirmarMetodoSeleccionado);

// ===========================
// FUNCIÓN DESCARGAR TICKET PDF
// ===========================

function descargarTicketPDF(compraId) {
    // Abrir PDF en nueva ventana o descargar
    window.open('/ventas/ticket-pdf/' + compraId + '/', '_blank');
    
    // Mostrar notificación de descarga
    Swal.fire({
        icon: 'info',
        title: 'Descargando ticket...',
        text: 'ticket_' + String(compraId).padStart(5, '0') + '.pdf',
        timer: 2000,
        showConfirmButton: false
    });
}

// Event listener para cambio en radio buttons
$(document).on('change', 'input[name="metodo_seleccion"]', function() {
    console.log('Método cambiado a:', $(this).val());
});

// ===========================
// FUNCIONES DE SCROLL POS
// ===========================

function inicializarScrollPOS() {
    console.log('Inicializando scroll POS...');
    
    const $grid = $('.pos-products-grid');
    if ($grid.length === 0) return;
    
    // Hacer el grid enfocable para atajos de teclado
    $grid.attr('tabindex', 0);
    
    // Atajos de teclado para navegación
    $grid.on('keydown', function(e) {
        const element = this;
        switch(e.key) {
            case 'Home':
                e.preventDefault();
                element.scrollTop = 0;
                break;
            case 'End':
                e.preventDefault();
                element.scrollTop = element.scrollHeight;
                break;
            case 'PageUp':
                e.preventDefault();
                element.scrollTop -= element.clientHeight * 0.8;
                break;
            case 'PageDown':
                e.preventDefault();
                element.scrollTop += element.clientHeight * 0.8;
                break;
        }
    });
    
    console.log('Scroll POS inicializado correctamente');
}

// Función para resetear scroll al filtrar
function resetearScrollPOS() {
    const $grid = $('.pos-products-grid');
    if ($grid.length) {
        $grid[0].scrollTop = 0;
    }
}