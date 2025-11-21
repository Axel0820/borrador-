
function cargarContenido(url) {
    $.ajax({
        url: url,
        type: 'GET',
        headers: {'X-Requested-With': 'XMLHttpRequest'},
        success: function(data) {
            $('#contenidoDinamico').html(data);
            
            // Librerías que ya están cargadas globalmente (no recargar)
            const libreriasGlobales = [
                'jquery',
                'bootstrap',
                'dataTables',
                'popper'
            ];
            
            // Ejecutar scripts que están en el contenido cargado
            $('#contenidoDinamico').find('script').each(function() {
                if (this.src) {
                    let scriptSrc = this.src;
                    
                    // Verificar si es una librería global que no debe recargarse
                    let esLibreriaGlobal = libreriasGlobales.some(lib => 
                        scriptSrc.toLowerCase().includes(lib.toLowerCase())
                    );
                    
                    // Solo cargar si:
                    // 1. No es una librería global
                    // 2. No está ya cargado en la página
                    if (!esLibreriaGlobal && $('script[src="' + scriptSrc + '"]').length === 0) {
                        $.getScript(scriptSrc).fail(function() {
                            console.warn('No se pudo cargar:', scriptSrc);
                        });
                    }
                } else {
                    // Script inline - ejecutar en un scope aislado
                    try {
                        // Usar Function en lugar de eval para evitar conflictos de scope
                        (new Function($(this).text()))();
                    } catch (e) {
                        console.warn('Error al ejecutar script inline:', e);
                    }
                }
            });
            
            // Actualizar navegación visual después de cargar contenido AJAX
            activarNavegacionPorContenido(url);
        },
        error: function() {
            console.error('Error al cargar el contenido');
        }
    });
}

// Función para activar navegación visual basada en URL
function activarNavegacionPorURL() {
    $('.nav-link').removeClass('active');
    
    const url = window.location.pathname;
    let elementoActivado = null;
    
    if (url.includes('dashboard')) {
        elementoActivado = $('.nav-link[aria-current="page"]').first();
    } else if (url.includes('nueva-venta')) {
        elementoActivado = $('#btnVentas').first();
    } else if (url.includes('caja')) {
        elementoActivado = $('#btnCaja').first();
    } else if (url.includes('productos') || url.includes('inventario')) {
        elementoActivado = $('#btnInventario').first();
    } else if (url.includes('empleados')) {
        elementoActivado = $('#btnEmpleados').first();
    } else if (url.includes('proveedores')) {
        elementoActivado = $('#btnProveedores').first();
    } else if (url.includes('clientes')) {
        elementoActivado = $('#btnClientes').first();
    } else if (url.includes('turnos')) {
        elementoActivado = $('#btnTurnos').first();
    } else if (url.includes('perfil')) {
        elementoActivado = $('#btnPerfil').first();
    } else {
        elementoActivado = $('.nav-link[aria-current="page"]').first();
    }
    
    if (elementoActivado && elementoActivado.length > 0) {
        elementoActivado.addClass('active');
    }
}

// Función para activar navegación visual basada en contenido AJAX
function activarNavegacionPorContenido(urlCargada) {
    $('.nav-link').removeClass('active');
    
    let elementoActivado = null;
    
    if (urlCargada.includes('dashboard')) {
        elementoActivado = $('.nav-link[aria-current="page"]').first();
    } else if (urlCargada.includes('nueva-venta')) {
        elementoActivado = $('#btnVentas').first();
    } else if (urlCargada.includes('caja')) {
        elementoActivado = $('#btnCaja').first();
    } else if (urlCargada.includes('productos') || urlCargada.includes('inventario')) {
        elementoActivado = $('#btnInventario').first();
    } else if (urlCargada.includes('empleados')) {
        elementoActivado = $('#btnEmpleados').first();
    } else if (urlCargada.includes('proveedores')) {
        elementoActivado = $('#btnProveedores').first();
    } else if (urlCargada.includes('clientes')) {
        elementoActivado = $('#btnClientes').first();
    } else if (urlCargada.includes('turnos')) {
        elementoActivado = $('#btnTurnos').first();
    } else if (urlCargada.includes('perfil')) {
        elementoActivado = $('#btnPerfil').first();
    } else {
        elementoActivado = $('.nav-link[aria-current="page"]').first();
    }
    
    if (elementoActivado && elementoActivado.length > 0) {
        elementoActivado.addClass('active');
    }
}

$(document).ready(function() {
    // Inicializar navegación visual al cargar la página
    activarNavegacionPorURL();
    
    // Cargar dashboard al inicializar la página
    cargarContenido('/dashboard/');
    
    // Evento para el botón Inicio (navbar-brand y enlace Inicio específico)
    $(document).on('click', '.navbar-brand', function(e) {
        e.preventDefault();
        cargarContenido('/dashboard/');
    });
    
    // Evento específico para el enlace "Inicio" sin ID
    $(document).on('click', '.nav-link[aria-current="page"]', function(e) {
        e.preventDefault();
        cargarContenido('/dashboard/');
    });

    // Evento para el botón Caja
    $(document).on('click', '#btnCaja', function(e) {
        e.preventDefault();
        var url = $(this).attr('href');
        cargarContenido(url);
    });

    // Evento para el botón Inventario
    $(document).on('click', '#btnInventario', function(e) {
        e.preventDefault();
        var url = $(this).attr('href');
        cargarContenido(url);
    });

    // Evento para el botón Empleados
    $(document).on('click', '#btnEmpleados', function(e) {
        e.preventDefault();
        var url = $(this).attr('href');
        cargarContenido(url);
    });

    // Evento para el botón Proveedores
    $(document).on('click', '#btnProveedores', function(e) {
        e.preventDefault();
        var url = $(this).attr('href');
        cargarContenido(url);
    });

    // Evento para el botón Clientes
    $(document).on('click', '#btnClientes', function(e) {
        e.preventDefault();
        var url = $(this).attr('href');
        cargarContenido(url);
    });
    
    // Evento para el botón Inventario
    $(document).on('click', '#btnPerfil', function(e) {
        e.preventDefault();
        var url = $(this).attr('href');
        cargarContenido(url);
    });
        // -----------------------------Evento para el botón Ventas (CAJA)------------------------------
    $(document).on('click', '#btnVentas', function(e) {
        e.preventDefault();
        var url = $(this).attr('href');
        cargarContenido(url);
    });
    // Evento para el botón Turnos
    $(document).on('click', '#btnTurnos', function(e) {
        e.preventDefault();
        var url = $(this).attr('href');
        cargarContenido(url);
    });

    // Manejar envío del formulario de filtros de turnos
    $(document).on('submit', '#filtroFormTurnos', function(e) {
        e.preventDefault();
        var formData = $(this).serialize();
        var actionUrl = $(this).attr('action');
        cargarContenido(actionUrl + '?' + formData);
    });

    // Manejar envío del formulario de filtros de turnos cuando se hace clic en el botón Filtrar
    $(document).on('click', '#filtroFormTurnos button[type="submit"]', function(e) {
        e.preventDefault();
        var formData = $('#filtroFormTurnos').serialize();
        var actionUrl = $('#filtroFormTurnos').attr('action');
        cargarContenido(actionUrl + '?' + formData);
    });

    // Manejar botón limpiar filtro de turnos
    $(document).on('click', '#btnLimpiarTurnos', function(e) {
        e.preventDefault();
        // Limpiar todos los campos del formulario
        $('#filtroFormTurnos')[0].reset();
        // Recargar la lista de turnos sin filtros usando la función cargarContenido
        cargarContenido("/turnosadm/");
    });

    // Manejar envío del formulario de filtros de empleados
    $(document).on('submit', '#filtroForm', function(e) {
        e.preventDefault();
        var formData = $(this).serialize();
        var actionUrl = $(this).attr('action');
        cargarContenido(actionUrl + '?' + formData);
    });

    // Manejar envío del formulario de filtros de productos
    $(document).on('submit', '#filtroFormProductos', function(e) {
        e.preventDefault();
        var formData = $(this).serialize();
        var actionUrl = $(this).attr('action');
        cargarContenido(actionUrl + '?' + formData);
    });

    // Manejar envío del formulario de filtros de proveedores
    $(document).on('submit', '#filtroFormProveedores', function(e) {
        e.preventDefault();
        var formData = $(this).serialize();
        var actionUrl = $(this).attr('action');
        cargarContenido(actionUrl + '?' + formData);
    });

    // Manejar envío del formulario de filtros de clientes
    $(document).on('submit', '#filtroFormClientes', function(e) {
        e.preventDefault();
        var formData = $(this).serialize();
        var actionUrl = $(this).attr('action');
        cargarContenido(actionUrl + '?' + formData);
    });

    // menajar envio de caja
    $(document).on('submit', '#filtroFormCaja', function(e) {
        e.preventDefault();
        var formData = $(this).serialize();
        var actionUrl = $(this).attr('action');
        cargarContenido(actionUrl + '?' + formData);
    });

    // Manejar botón limpiar filtro de empleados
    $(document).on('click', '#btnLimpiarFiltro', function(e) {
        e.preventDefault();
        // Limpiar todos los campos del formulario
        $('#filtroForm')[0].reset();
        // Recargar la lista de empleados sin filtros
        $.ajax({
            url: "/empleados/",
            headers: {"X-Requested-With": "XMLHttpRequest"},
            success: function(data) {
                $("#contenidoDinamico").html(data);
            }
        });
    });

    // Manejar botón limpiar filtro de productos
    $(document).on('click', '#btnLimpiarProductos', function(e) {
        e.preventDefault();
        // Limpiar todos los campos del formulario
        $('#filtroFormProductos')[0].reset();
        // Recargar la lista de productos sin filtros usando la función cargarContenido
        cargarContenido("{% url 'listarProductos' %}");
    });

    // Manejar botón limpiar filtro de proveedores
    $(document).on('click', '#btnLimpiarProveedores', function(e) {
        e.preventDefault();
        // Limpiar todos los campos del formulario
        $('#filtroFormProveedores')[0].reset();
        // Recargar la lista de proveedores sin filtros
        $.ajax({
            url: "/proveedores/",
            headers: {"X-Requested-With": "XMLHttpRequest"},
            success: function(data) {
                $("#contenidoDinamico").html(data);
            }
        });
    });

    // Manejar botón limpiar filtro de clientes
    $(document).on('click', '#btnLimpiarClientes', function(e) {
        e.preventDefault();
        // Limpiar todos los campos del formulario
        $('#filtroFormClientes')[0].reset();
        // Recargar la lista de clientes sin filtros
        $.ajax({
            url: "/clientes/",
            headers: {"X-Requested-With": "XMLHttpRequest"},
            success: function(data) {
                $("#contenidoDinamico").html(data);
            }
        });
    });

    // Listener genérico para todos los enlaces con clase nav-ajax
    // Útil para botones de detalle, volver, etc.
    $(document).on('click', '.nav-ajax', function(e) {
        e.preventDefault();
        var url = $(this).attr('href');
        if (url && url !== '#') {
            cargarContenido(url);
        }
    });
});
// ===== FUNCIONES PARA EL SISTEMA POS =====

// Función para inicializar filtros del POS
function inicializarFiltrosPOS() {
    console.log('Inicializando filtros POS...');
    
    // Solo ejecutar si existe el contenedor POS
    if ($('.pos-container').length === 0) {
        return;
    }
    
    // Limpiar eventos anteriores del POS usando namespace
    $(document).off('.pos-filtros');
    $(document).off('.pos-search');
    
    // Variables locales para esta sesión del POS
    let categoriaActiva = 'todas';
    
    // Función para aplicar filtros
    function filtrarProductosPOS() {
        const busqueda = $('#pos-search').val().toLowerCase();
        let productosVisibles = 0;
        
        $('.product-card').each(function() {
            const $card = $(this);
            const categoria = ($card.data('categoria') || 'Sin categoría').toLowerCase();
            const nombre = ($card.data('nombre') || '').toLowerCase();
            
            // Filtro por categoría
            const coincideCategoria = categoriaActiva === 'todas' || 
                                    categoria === categoriaActiva.toLowerCase();
            
            // Filtro por búsqueda
            const coincideBusqueda = !busqueda || nombre.includes(busqueda);
            
            if (coincideCategoria && coincideBusqueda) {
                $card.show();
                productosVisibles++;
            } else {
                $card.hide();
            }
        });
        
        // Actualizar contador
        $('#productos-mostrados').text(productosVisibles);
    }
    
    // Event listener para filtros de categoría
    $(document).on('click.pos-filtros', '.filter-btn', function() {
        $('.filter-btn').removeClass('active');
        $(this).addClass('active');
        categoriaActiva = $(this).data('categoria');
        filtrarProductosPOS();
    });
    
    // Event listener para búsqueda
    $(document).on('input.pos-search', '#pos-search', function() {
        filtrarProductosPOS();
    });
    
    // Mostrar todos los productos inicialmente
    filtrarProductosPOS();
    
    console.log('Filtros POS inicializados correctamente');
}

// Detectar cuando se carga contenido vía AJAX
$(document).ajaxComplete(function(event, xhr, settings) {
    // Si el contenido cargado contiene el POS, inicializar filtros
    if ($('.pos-container').length) {
        setTimeout(inicializarFiltrosPOS, 100); // Pequeño delay para asegurar que el DOM esté listo
    }
});