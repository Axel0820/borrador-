// Librerías que ya están cargadas globalmente (no recargar)
const libreriasGlobales = [
    'jquery',
    'bootstrap',
    'dataTables',
    'popper'
];

function cargarContenido(url) {
    $.ajax({
        url: url,
        type: 'GET',
        headers: {'X-Requested-With': 'XMLHttpRequest'},
        success: function(data) {
            $('#contenidoDinamico').html(data);

            // Limpiar calendario anterior si existe
            if (typeof window.calendarCli !== 'undefined' && window.calendarCli) {
                window.calendarCli.destroy();
                window.calendarCli = null;
            }

            // Cargar scripts específicos para turnos si la URL contiene 'turnos'
            if (url.includes('turnos')) {
                // Cargar FullCalendar JS
                $.getScript('https://cdn.jsdelivr.net/npm/fullcalendar@6.1.11/index.global.min.js', function() {
                    // Cargar locales después de FullCalendar
                    $.getScript('https://cdn.jsdelivr.net/npm/fullcalendar@6.1.11/locales-all.min.js', function() {
                        // Cargar script local de turnos
                        $.getScript('/static/js/turnos/turnosCli.js');
                    });
                });
            }

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
    
    if (url.includes('productocli') || url.includes('catalogo')) {
        elementoActivado = $('#btnCatalogo').first();
    } else if (url.includes('turnos')) {
        elementoActivado = $('#btnPeluqueria').first();
    } else if (url.includes('nosotros')) {
        elementoActivado = $('#btnHistoria').first();
    } else if (url.includes('perfil')) {
        elementoActivado = $('#btnPerfil').first();
    } else {
        elementoActivado = $('#btnInicio').first();
    }
    
    if (elementoActivado && elementoActivado.length > 0) {
        elementoActivado.addClass('active');
    }
}

// Función para activar navegación visual basada en contenido AJAX
function activarNavegacionPorContenido(urlCargada) {
    $('.nav-link').removeClass('active');
    
    let elementoActivado = null;
    
    if (urlCargada.includes('productocli') || urlCargada.includes('catalogo')) {
        elementoActivado = $('#btnCatalogo').first();
    } else if (urlCargada.includes('turnos')) {
        elementoActivado = $('#btnPeluqueria').first();
    } else if (urlCargada.includes('nosotros')) {
        elementoActivado = $('#btnHistoria').first();
    } else if (urlCargada.includes('perfil')) {
        elementoActivado = $('#btnPerfil').first();
    } else {
        elementoActivado = $('#btnInicio').first();
    }
    
    if (elementoActivado && elementoActivado.length > 0) {
        elementoActivado.addClass('active');
    }
}

$(document).ready(function() {
    // Inicializar navegación visual al cargar la página
    activarNavegacionPorURL();

    // Evento para el botón Catálogo
    $(document).on('click', '#btnCatalogo', function(e) {
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

    // Evento para el botón Peluqueria
    $(document).on('click', '#btnPeluqueria', function(e) {
        e.preventDefault();
        // Redirigir con AJAX a la vista de turnos
        var url = '/turnoscli/turnos';
        cargarContenido(url);
    });

    // Evento para el botón Historia
    $(document).on('click', '#btnHistoria', function(e) {
        e.preventDefault();
        var url = '/nosotros/';
        cargarContenido(url);
    });

    // Puedes agregar más eventos para otros botones del nav si es necesario
    $(document).on('click', '#btnPerfil', function(e) {
        e.preventDefault();
        var url = $(this).attr('href');
        cargarContenido(url);
    });
});
