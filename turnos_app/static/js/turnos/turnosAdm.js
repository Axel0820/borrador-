// turnosAdm.js - Manejo de modales, AJAX y calendario para administración de turnos
// NO usar $(document).ready() porque se ejecuta solo una vez
// Usar delegación de eventos para que funcione con contenido AJAX

// Variables globales para el calendario
window.calendarAdm = null;

// Event listeners para botones de cambiar estado
$(document).on('click', '.cambiar-estado', function(e) {
    e.preventDefault();
    const turnoId = $(this).data('turno-id');
    const estadoActual = $(this).data('estado-actual');
    mostrarModalCambiarEstado(turnoId, estadoActual);
});

// Event listeners para botones de ver detalles
$(document).on('click', '.ver-detalles', function(e) {
    e.preventDefault();
    const turnoId = $(this).data('turno-id');
    mostrarDetallesTurno(turnoId);
});

// Event listener para guardar cambios de estado
$(document).on('click', '#btnGuardarEstado', function(e) {
    e.preventDefault();
    guardarCambioEstado();
});

// Event listeners para alternar vistas
$(document).on('click', '#btnVistaLista', function(e) {
    e.preventDefault();
    alternarVista('lista');
});

$(document).on('click', '#btnVistaCalendario', function(e) {
    e.preventDefault();
    alternarVista('calendario');
});

// Event listener para limpiar filtros
$(document).on('click', '#btnLimpiarTurnos', function(e) {
    e.preventDefault();
    limpiarFiltros();
});

// Event listener para búsqueda al presionar Enter
$(document).on('keypress', '#busqueda', function(e) {
    if (e.which === 13) { // Enter key
        e.preventDefault();
        const query = $(this).val().trim();
        buscarTurnos(query);
    }
});

function mostrarModalCambiarEstado(turnoId, estadoActual) {
    // Establecer el ID del turno
    document.getElementById('turnoId').value = turnoId;

    // Seleccionar el estado actual en el select
    const selectEstado = document.getElementById('nuevoEstado');
    selectEstado.value = estadoActual;

    // Limpiar observaciones
    document.getElementById('observaciones').value = '';

    // Mostrar el modal
    const modal = new bootstrap.Modal(document.getElementById('modalCambiarEstado'));
    modal.show();
}

function guardarCambioEstado() {
    const turnoId = $('#turnoId').val();
    const nuevoEstado = $('#nuevoEstado').val();
    const observaciones = $('#observaciones').val();

    // Validación básica
    if (!nuevoEstado) {
        Swal.fire({
            icon: 'warning',
            title: 'Campo requerido',
            text: 'Por favor seleccione un estado'
        });
        return;
    }

    // Deshabilitar botón para evitar múltiples clicks
    const btnGuardar = $('#btnGuardarEstado');
    btnGuardar.prop('disabled', true);
    btnGuardar.html('<i class="bi bi-hourglass-split"></i> Guardando...');

    // Preparar datos para enviar
    const data = {
        turno_id: turnoId,
        estado: nuevoEstado,
        observaciones: observaciones,
        csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
    };

    // Enviar solicitud AJAX
    $.ajax({
        url: '/turnosadm/cambiar-estado/',
        method: 'POST',
        data: data,
        success: function(response) {
            if (response.success) {
                // Cerrar modal
                $('#modalCambiarEstado').modal('hide');

                // Mostrar mensaje de éxito
                Swal.fire({
                    icon: 'success',
                    title: '¡Estado actualizado!',
                    text: 'El estado del turno se ha actualizado exitosamente.',
                    showConfirmButton: false,
                    timer: 1500
                }).then(() => {
                    // Cerrar completamente el modal y limpiar el backdrop
                    $('#modalCambiarEstado').modal('hide');
                    $('.modal-backdrop').remove();
                    $('body').removeClass('modal-open');

                    // Obtener los parámetros actuales de la URL para mantener los filtros
                    const urlParams = new URLSearchParams(window.location.search);
                    const currentParams = urlParams.toString();
                    const baseUrl = '/turnosadm/';
                    const reloadUrl = currentParams ? `${baseUrl}?${currentParams}` : baseUrl;

                    // Recargar el contenido dinámico de turnos en adm2 manteniendo los filtros
                    if (window.parent && window.parent.cargarContenido) {
                        window.parent.cargarContenido(reloadUrl);
                    } else {
                        // Fallback si no está en el contexto de adm2
                        window.location.href = reloadUrl;
                    }
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: response.error || 'Error desconocido al actualizar el estado'
                });
            }
        },
        error: function(xhr, status, error) {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error de conexión',
                text: 'No se pudo actualizar el estado del turno'
            });
        },
        complete: function() {
            // Re-habilitar botón
            btnGuardar.prop('disabled', false);
            btnGuardar.html('<i class="bi bi-check-circle"></i> Guardar Cambios');
        }
    });
}

function mostrarDetallesTurno(turnoId) {
    // Mostrar el modal con un loader
    const modal = new bootstrap.Modal(document.getElementById('modalDetalles'));
    $('#detallesTurno').html(`
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <p class="text-muted mt-2">Cargando detalles del turno...</p>
        </div>
    `);
    modal.show();

    // Enviar solicitud AJAX para obtener detalles del turno
    $.ajax({
        url: `/turnosadm/detalles/${turnoId}/`,
        method: 'GET',
        success: function(response) {
            if (response.success) {
                // Llenar el modal con los detalles
                const detallesHtml = generarHtmlDetalles(response.turno);
                $('#detallesTurno').html(detallesHtml);
            } else {
                $('#detallesTurno').html(`
                    <div class="alert alert-danger" role="alert">
                        <i class="bi bi-exclamation-triangle"></i>
                        ${response.error || 'Error desconocido al cargar detalles'}
                    </div>
                `);
            }
        },
        error: function(xhr, status, error) {
            console.error('Error:', error);
            $('#detallesTurno').html(`
                <div class="alert alert-danger" role="alert">
                    <i class="bi bi-exclamation-triangle"></i>
                    No se pudieron cargar los detalles del turno
                </div>
            `);
        }
    });
}

function generarHtmlDetalles(turno) {
    const badgeClass = 
        turno.estado_turno === 'Pendiente' ? 'bg-warning' :
        turno.estado_turno === 'Confirmado' ? 'bg-success' :
        turno.estado_turno === 'En curso' ? 'bg-primary' :
        turno.estado_turno === 'Completado' ? 'bg-success' :
        turno.estado_turno === 'Cancelado' ? 'bg-danger' :
        'bg-secondary';

    return `
        <div class="row g-3">
            <div class="col-md-6">
                <div class="card border-0 bg-light">
                    <div class="card-body">
                        <h6 class="card-subtitle mb-3 text-muted">
                            <i class="bi bi-person-circle"></i> Información del Cliente
                        </h6>
                        <p class="mb-2">
                            <strong><i class="bi bi-person"></i> Nombre:</strong><br>
                            ${turno.cliente.nombre}
                        </p>
                        <p class="mb-2">
                            <strong><i class="bi bi-envelope"></i> Email:</strong><br>
                            ${turno.cliente.email}
                        </p>
                        <p class="mb-0">
                            <strong><i class="bi bi-telephone"></i> Teléfono:</strong><br>
                            ${turno.cliente.telefono || '<span class="text-muted">No especificado</span>'}
                        </p>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card border-0 bg-light">
                    <div class="card-body">
                        <h6 class="card-subtitle mb-3 text-muted">
                            <i class="bi bi-heart"></i> Información de la Mascota
                        </h6>
                        <p class="mb-2">
                            <strong><i class="bi bi-tag"></i> Nombre:</strong><br>
                            ${turno.nombre || '<span class="text-muted">No especificado</span>'}
                        </p>
                        <p class="mb-2">
                            <strong><i class="bi bi-info-circle"></i> Tipo:</strong> ${turno.tipo_turno || 'No especificado'}
                        </p>
                        <p class="mb-2">
                            <strong><i class="bi bi-arrows-angle-expand"></i> Tamaño:</strong> ${turno.tamaño_turno || 'No especificado'}
                        </p>
                        <p class="mb-2">
                            <strong><i class="bi bi-gender-ambiguous"></i> Género:</strong> ${turno.genero || 'No especificado'}
                        </p>
                        <p class="mb-0">
                            <strong><i class="bi bi-calendar-event"></i> Edad:</strong> ${turno.edad_turno || 'No especificada'}
                        </p>
                    </div>
                </div>
            </div>
        </div>

        <div class="row g-3 mt-2">
            <div class="col-md-6">
                <div class="card border-0 bg-light">
                    <div class="card-body">
                        <h6 class="card-subtitle mb-3 text-muted">
                            <i class="bi bi-calendar-check"></i> Información del Turno
                        </h6>
                        <p class="mb-2">
                            <strong><i class="bi bi-calendar3"></i> Fecha:</strong><br>
                            ${turno.fecha_turno}
                        </p>
                        <p class="mb-2">
                            <strong><i class="bi bi-clock"></i> Hora:</strong><br>
                            ${turno.hora_turno}
                        </p>
                        <p class="mb-0">
                            <strong><i class="bi bi-check-circle"></i> Estado:</strong><br>
                            <span class="badge ${badgeClass} mt-1">${turno.estado_turno}</span>
                        </p>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card border-0 bg-light">
                    <div class="card-body">
                        <h6 class="card-subtitle mb-3 text-muted">
                            <i class="bi bi-scissors"></i> Servicios Solicitados
                        </h6>
                        ${turno.servicios && turno.servicios.length > 0 ?
                            turno.servicios.map(servicio =>
                                `<span class="badge bg-info text-dark me-1 mb-1">${servicio.nombre_servicio}</span>`
                            ).join('') :
                            '<p class="text-muted mb-0">Sin servicios especificados</p>'
                        }
                    </div>
                </div>
            </div>
        </div>

        ${turno.observaciones_turno ? `
            <div class="row mt-3">
                <div class="col-12">
                    <div class="card border-0 bg-light">
                        <div class="card-body">
                            <h6 class="card-subtitle mb-2 text-muted">
                                <i class="bi bi-chat-left-text"></i> Observaciones
                            </h6>
                            <p class="mb-0">${turno.observaciones_turno}</p>
                        </div>
                    </div>
                </div>
            </div>
        ` : ''}

        ${turno.motivo_cance_turno ? `
            <div class="row mt-3">
                <div class="col-12">
                    <div class="alert alert-danger mb-0" role="alert">
                        <h6 class="alert-heading">
                            <i class="bi bi-exclamation-triangle"></i> Motivo de Cancelación
                        </h6>
                        <p class="mb-0">${turno.motivo_cance_turno}</p>
                    </div>
                </div>
            </div>
        ` : ''}
    `;
}

// Función para limpiar filtros
function limpiarFiltros() {
    $('#estado').val('');
    $('#fecha').val('');
    $('#busqueda').val('');

    // Recargar la página sin parámetros
    const baseUrl = '/turnosadm/';
    if (window.parent && window.parent.cargarContenido) {
        window.parent.cargarContenido(baseUrl);
    } else {
        window.location.href = baseUrl;
    }
}

// Función para búsqueda en tiempo real
function buscarTurnos(query) {
    // Obtener otros filtros actuales
    const estado = $('#estado').val();
    const fecha = $('#fecha').val();

    // Construir URL con parámetros
    const params = new URLSearchParams();
    if (query) params.append('busqueda', query);
    if (estado) params.append('estado', estado);
    if (fecha) params.append('fecha', fecha);

    const url = params.toString() ? `/turnosadm/?${params.toString()}` : '/turnosadm/';

    // Recargar contenido con filtros aplicados
    if (window.parent && window.parent.cargarContenido) {
        window.parent.cargarContenido(url);
    } else {
        window.location.href = url;
    }
}

// Función para alternar entre vistas lista y calendario
function alternarVista(vista) {
    const btnLista = $('#btnVistaLista');
    const btnCalendario = $('#btnVistaCalendario');
    const vistaLista = $('#vistaLista');
    const vistaCalendario = $('#vistaCalendario');

    if (vista === 'lista') {
        // Mostrar vista lista
        vistaLista.fadeIn(300);
        vistaCalendario.fadeOut(300);

        // Actualizar botones
        btnLista.addClass('active btn-primary').removeClass('btn-outline-primary');
        btnCalendario.removeClass('active btn-secondary').addClass('btn-outline-secondary');

        // Destruir calendario si existe
        if (window.calendarAdm) {
            window.calendarAdm.destroy();
            window.calendarAdm = null;
        }
    } else if (vista === 'calendario') {
        // Mostrar vista calendario
        vistaLista.fadeOut(300);
        vistaCalendario.fadeIn(300);

        // Actualizar botones
        btnCalendario.addClass('active btn-secondary').removeClass('btn-outline-secondary');
        btnLista.removeClass('active btn-primary').addClass('btn-outline-primary');

        // Inicializar calendario si no existe
        setTimeout(() => {
            if (!window.calendarAdm) {
                inicializarCalendario();
            }
        }, 300);
    }
}

// Función para inicializar el calendario de administración
function inicializarCalendario() {
    const calendarEl = document.getElementById('calendarAdm');

    if (calendarEl && typeof FullCalendar !== 'undefined') {
        window.calendarAdm = new FullCalendar.Calendar(calendarEl, {
            locales: FullCalendar.globalLocales,
            locale: 'es',
            initialView: 'dayGridMonth',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek'
            },
            buttonText: {
                today: 'Hoy',
                month: 'Mes',
                week: 'Semana'
            },
            events: '/turnosadm/turnos-json/',
            eventClick: function(info) {
                // Mostrar detalles del turno al hacer click en el evento
                info.jsEvent.preventDefault();
                mostrarDetallesTurno(info.event.extendedProps.turno_id);
            },
            dateClick: function(info) {
                // Al hacer clic en una fecha, cambiar a vista lista y filtrar por esa fecha
                const fechaSeleccionada = info.dateStr; // Formato YYYY-MM-DD

                // Cambiar a vista lista
                alternarVista('lista');

                // Establecer la fecha en el formulario y enviar
                setTimeout(() => {
                    $('#fecha').val(fechaSeleccionada);
                    $('#estado').val(''); // Limpiar filtro de estado
                    $('#filtroFormTurnos').submit();
                }, 400);
            },
            eventDidMount: function(info) {
                // Agregar tooltip con información básica
                const tooltip = `${info.event.title}\nCliente: ${info.event.extendedProps.cliente}\nMascota: ${info.event.extendedProps.mascota}`;
                info.el.setAttribute('title', tooltip);
                
                // Añadir cursor pointer
                info.el.style.cursor = 'pointer';
            },
            height: 'auto',
            aspectRatio: 1.8,
            eventColor: '#7c3aed',
            eventTextColor: '#ffffff',
            // Animación al cargar eventos
            eventDidMount: function(info) {
                info.el.style.animation = 'fadeIn 0.3s ease';
            }
        });

        window.calendarAdm.render();
    } else {
        console.error('FullCalendar no está disponible o el elemento calendarAdm no existe');
    }
}

// Agregar animación CSS para los eventos
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: scale(0.95);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
`;
document.head.appendChild(style);