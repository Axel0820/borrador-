// turnosAdm.js - Manejo de modales, AJAX y calendario para administración de turnos
// NO usar $(document).ready() porque se ejecuta solo una vez
// Usar delegación de eventos para que funcione con contenido AJAX

// Variables globales para el calendario
let calendarAdm = null;

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
        }
    });
}

function mostrarDetallesTurno(turnoId) {
    // Enviar solicitud AJAX para obtener detalles del turno
    $.ajax({
        url: `/turnosadm/detalles/${turnoId}/`,
        method: 'GET',
        success: function(response) {
            if (response.success) {
                // Llenar el modal con los detalles
                const detallesHtml = generarHtmlDetalles(response.turno);
                $('#detallesTurno').html(detallesHtml);

                // Mostrar el modal
                $('#modalDetalles').modal('show');
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: response.error || 'Error desconocido al cargar detalles'
                });
            }
        },
        error: function(xhr, status, error) {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error de conexión',
                text: 'No se pudieron cargar los detalles del turno'
            });
        }
    });
}

function generarHtmlDetalles(turno) {
    return `
        <div class="row">
            <div class="col-md-6">
                <h6><i class="bi bi-person"></i> Información del Cliente</h6>
                <p><strong>Nombre:</strong> ${turno.cliente.nombre}</p>
                <p><strong>Email:</strong> ${turno.cliente.email}</p>
                <p><strong>Teléfono:</strong> ${turno.cliente.telefono || 'No especificado'}</p>
            </div>
            <div class="col-md-6">
                <h6><i class="bi bi-heart"></i> Información de la Mascota</h6>
                <p><strong>Nombre:</strong> ${turno.nombre || 'No especificado'}</p>
                <p><strong>Tipo:</strong> ${turno.tipo_turno || 'No especificado'}</p>
                <p><strong>Tamaño:</strong> ${turno.tamaño_turno || 'No especificado'}</p>
                <p><strong>Género:</strong> ${turno.genero || 'No especificado'}</p>
                <p><strong>Edad:</strong> ${turno.edad_turno || 'No especificada'}</p>
                <p><strong>Observaciones:</strong> ${turno.observaciones_turno || 'Sin observaciones'}</p>
            </div>
        </div>
        <hr>
        <div class="row">
            <div class="col-md-6">
                <h6><i class="bi bi-calendar"></i> Información del Turno</h6>
                <p><strong>Fecha:</strong> ${turno.fecha_turno}</p>
                <p><strong>Hora:</strong> ${turno.hora_turno}</p>
                <p><strong>Estado:</strong>
                    <span class="badge
                        ${turno.estado_turno === 'Pendiente' ? 'bg-warning' :
                          turno.estado_turno === 'Confirmado' ? 'bg-success' :
                          turno.estado_turno === 'En curso' ? 'bg-primary' :
                          turno.estado_turno === 'Completado' ? 'bg-success' :
                          turno.estado_turno === 'Cancelado' ? 'bg-danger' :
                          'bg-secondary'}">
                        ${turno.estado_turno}
                    </span>
                </p>
            </div>
            <div class="col-md-6">
                <h6><i class="bi bi-tools"></i> Servicios Solicitados</h6>
                ${turno.servicios && turno.servicios.length > 0 ?
                    turno.servicios.map(servicio =>
                        `<span class="badge bg-info me-1">${servicio.nombre_servicio}</span>`
                    ).join('') :
                    '<p class="text-muted">Sin servicios especificados</p>'
                }
            </div>
        </div>
        ${turno.motivo_cance_turno ? `
            <hr>
            <div class="row">
                <div class="col-12">
                    <h6><i class="bi bi-exclamation-triangle"></i> Motivo de Cancelación</h6>
                    <p class="text-danger">${turno.motivo_cance_turno}</p>
                </div>
            </div>
        ` : ''}
    `;
}

// Función para alternar entre vistas lista y calendario
function alternarVista(vista) {
    const btnLista = $('#btnVistaLista');
    const btnCalendario = $('#btnVistaCalendario');
    const vistaLista = $('#vistaLista');
    const vistaCalendario = $('#vistaCalendario');

    if (vista === 'lista') {
        // Mostrar vista lista
        vistaLista.show();
        vistaCalendario.hide();

        // Actualizar botones
        btnLista.addClass('active btn-primary').removeClass('btn-outline-primary');
        btnCalendario.removeClass('active btn-secondary').addClass('btn-outline-secondary');

        // Destruir calendario si existe
        if (calendarAdm) {
            calendarAdm.destroy();
            calendarAdm = null;
        }
    } else if (vista === 'calendario') {
        // Mostrar vista calendario
        vistaLista.hide();
        vistaCalendario.show();

        // Actualizar botones
        btnCalendario.addClass('active btn-secondary').removeClass('btn-outline-secondary');
        btnLista.removeClass('active btn-primary').addClass('btn-outline-primary');

        // Inicializar calendario si no existe
        if (!calendarAdm) {
            inicializarCalendario();
        }
    }
}

// Función para inicializar el calendario de administración
function inicializarCalendario() {
    const calendarEl = document.getElementById('calendarAdm');

    if (calendarEl && typeof FullCalendar !== 'undefined') {
        calendarAdm = new FullCalendar.Calendar(calendarEl, {
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
                mostrarDetallesTurno(info.event.extendedProps.turno_id);
            },
            dateClick: function(info) {
                // Al hacer clic en una fecha, cambiar a vista lista y filtrar por esa fecha
                const fechaSeleccionada = info.dateStr; // Formato YYYY-MM-DD

                // Cambiar a vista lista
                alternarVista('lista');

                // Establecer la fecha en el formulario y enviar
                $('#fecha').val(fechaSeleccionada);
                $('#estado').val(''); // Limpiar filtro de estado
                $('#filtroFormTurnos').submit();
            },
            eventDidMount: function(info) {
                // Agregar tooltip con información básica
                const tooltip = `${info.event.title}\nCliente: ${info.event.extendedProps.cliente}\nMascota: ${info.event.extendedProps.mascota}`;
                info.el.setAttribute('title', tooltip);
            },
            height: 'auto',
            aspectRatio: 1.8
        });

        calendarAdm.render();
    }
}


