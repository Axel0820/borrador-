// turnosCli.js - Manejo del calendario para clientes de turnos
// Inspirado en turnosAdm.js para mejor responsividad

// Variables globales para el calendario
window.calendarCli = null;

// Función para inicializar el calendario de clientes
function inicializarCalendarioCli() {
  const calendarEl = document.getElementById('calendar');

  if (calendarEl && typeof FullCalendar !== 'undefined') {
    // Detectar si es móvil (ancho < 768px)
    const isMobile = window.innerWidth < 768;

    calendarCli = new FullCalendar.Calendar(calendarEl, {
      locales: FullCalendar.globalLocales,
      locale: 'es',
      initialView: isMobile ? 'timeGridWeek' : 'dayGridMonth',
      headerToolbar: isMobile ? {
        left: 'prev,next',
        center: 'title',
        right: 'today'
      } : {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek'
      },
      buttonText: {
        today: 'Hoy',
        month: 'Mes',
        week: 'Semana'
      },
      dayHeaderFormat: { weekday: 'short' },
      allDaySlot: false,
      events: '/turnoscli/turnos-json/',
      selectable: true,
      slotMinTime: "10:00:00",
      slotMaxTime: "21:00:00",
      slotDuration: "01:00:00",
      slotLabelFormat: {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      },
      height: 'auto',
      aspectRatio: 1.8,

      eventDidMount: function(info) {
        // Agregar tooltip con información básica
        const tooltip = `Turno: ${info.event.title}`;
        info.el.setAttribute('title', tooltip);

        const date = info.event.start.toISOString().split('T')[0];
        const allEvents = calendarCli.getEvents();
        const eventsOnSameDay = allEvents.filter(event =>
          event.start.toISOString().split('T')[0] === date
        ).length;

        // Verificar si es el primer evento del día
        const eventTime = info.event.start.getTime();
        const isFirstEvent = !allEvents.some(event =>
          event.start.toISOString().split('T')[0] === date &&
          event.start.getTime() < eventTime
        );

        if (calendarCli.view.type === 'dayGridMonth') {
          // En vista mes, ocultar todos los eventos por defecto
          info.el.style.display = 'none';

          // Solo mostrar "Agenda Completa" si hay 11+ eventos y es el primer evento del día
          if (eventsOnSameDay >= 11 && isFirstEvent) {
            info.el.style.display = 'inline-block';
            info.el.innerHTML = 'Agenda<br><span style="font-weight:700;">Completa</span>';
            info.el.style.backgroundColor = 'rgba(216, 180, 254, 0.35)';
            info.el.style.color = '#4a148c';
            info.el.style.border = '1px solid #d1c4e9';
            info.el.style.fontWeight = '600';
            info.el.style.fontSize = '0.8rem';
            info.el.style.textAlign = 'center';
            info.el.style.borderRadius = '5px';
            info.el.style.margin = '4px auto';
            info.el.style.padding = '6px 10px';
            info.el.style.maxWidth = '80%';
          }
        } else if (calendarCli.view.type === 'timeGridWeek') {
          // En vista semana, mostrar eventos normalmente
          if (eventsOnSameDay >= 1) {
            // Si hay 11+ eventos, mostrar "Ocupado" para todos
            info.el.innerHTML = 'Ocupado';
            info.el.style.backgroundColor = 'rgba(216, 180, 254, 0.35)';
            info.el.style.color = '#4a148c';
            info.el.style.border = '1px solid #d1c4e9';
            info.el.style.fontWeight = '600';
            info.el.style.textAlign = 'center';
            info.el.style.borderRadius = '5px';
          }
        }
      },

      dateClick: function (info) {
        // Verificar si el día está completamente ocupado (11+ eventos)
        const clickedDate = info.dateStr;
        const allEvents = calendarCli.getEvents();
        const eventsOnClickedDay = allEvents.filter(event =>
          event.start.toISOString().split('T')[0] === clickedDate
        ).length;

        // Si hay 11+ eventos, no permitir selección
        if (eventsOnClickedDay >= 11) {
          mostrarMensaje('❌ Esta fecha está completamente ocupada');
          return;
        }

        const fechaInput = document.getElementById('fechaSeleccionada');
        if (fechaInput) {
          // Asegurar que solo se envíe la fecha sin hora ni zona horaria
          fechaInput.value = info.dateStr.split('T')[0] || info.dateStr;
        }

        const calendarWrapper = document.getElementById('calendar');
        if (calendarWrapper) {
          calendarWrapper.classList.remove('fc-transicion-activa');
          calendarWrapper.classList.add('fc-transicion');

          setTimeout(() => {
            calendarCli.changeView('timeGridWeek', info.date);
            requestAnimationFrame(() => {
              calendarWrapper.classList.add('fc-transicion-activa');
            });
          }, 100);
        }

        const formulario = document.getElementById('formularioMascota');
        if (formulario) {
          formulario.classList.remove('d-none');
        }
        mostrarMensaje(`📅 Fecha seleccionada: ${info.dateStr}`);
      },

      select: function(info) {
        const fechaInput = document.getElementById('fechaSeleccionada');
        const horaInput = document.getElementById('horaSeleccionada');

        // Asegurar que solo se envíe la fecha sin hora ni zona horaria
        const fecha = info.startStr.split('T')[0] || info.startStr.slice(0, 10);
        const hora = info.startStr.slice(11, 16);

        if (fechaInput) fechaInput.value = fecha;
        if (horaInput) horaInput.value = hora;

        mostrarMensaje(`Turno: ${fecha} a las ${hora}`);
      },

      selectAllow: function(selectInfo) {
        const events = calendarCli.getEvents().filter(event => {
          return event.start < selectInfo.end && event.end > selectInfo.start;
        });
        return events.length === 0;
      }
    });

    calendarCli.render();
    console.log('Calendario de turnosCli inicializado');
  } else {
    console.log('Elemento #calendar o FullCalendar no encontrado');
  }
}

// Función para destruir el calendario si existe
function destruirCalendarioCli() {
  if (window.calendarCli) {
    window.calendarCli.destroy();
    window.calendarCli = null;
  }
}

// Función principal de inicialización
function initTurnosCli() {
  console.log('initTurnosCli ejecutado');

  try {
    const contenido = document.getElementById('contenidoDinamico');
    if (contenido) {
      contenido.style.marginTop = '70px';
    }
  } catch (e) {
    console.warn('No se pudo ajustar margin-top de #contenidoDinamico:', e);
  }

  // Inicializar calendario si no existe
  if (!window.calendarCli) {
    inicializarCalendarioCli();
  }

  const formulario = document.getElementById('formularioTurno');

  // Agregar listener para filtrar entrada en el campo nombre
  const nombreInput = document.getElementById('nombre');
  if (nombreInput && !nombreInput.dataset.nombreListener) {
    nombreInput.dataset.nombreListener = '1';
    nombreInput.addEventListener('input', function(e) {
      // Filtrar solo letras, acentos, ñ y espacios
      const regex = /^[A-Za-zÁÉÍÓÚáéíóúÑñ ]*$/;
      if (!regex.test(e.target.value)) {
        e.target.value = e.target.value.replace(/[^A-Za-zÁÉÍÓÚáéíóúÑñ ]/g, '');
      }
      // Limitar a 30 caracteres
      if (e.target.value.length > 30) {
        e.target.value = e.target.value.substring(0, 30);
      }
    });
  }

  // Agregar listener para filtrar entrada en el campo observaciones
  const observacionesInput = document.getElementById('observaciones');
  if (observacionesInput && !observacionesInput.dataset.observacionesListener) {
    observacionesInput.dataset.observacionesListener = '1';
    observacionesInput.addEventListener('input', function(e) {
      // Filtrar caracteres permitidos: letras, números, acentos, ñ, espacios y puntuación básica
      const regex = /^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s.,;:!?()-]*$/;
      if (!regex.test(e.target.value)) {
        e.target.value = e.target.value.replace(/[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s.,;:!?()-]/g, '');
      }
      // Limitar a 300 caracteres
      if (e.target.value.length > 300) {
        e.target.value = e.target.value.substring(0, 300);
      }
    });
  }

  if (formulario && !formulario.dataset.turnosListener) {
    // Marcar que ya se adjuntó el listener para evitar bindings múltiples
    formulario.dataset.turnosListener = '1';
    let enviando = false;
    formulario.addEventListener('submit', function (e) {
      e.preventDefault();
      if (enviando) return; // protección extra en caso de múltiples listeners
      enviando = true;

      // Deshabilitar el botón de envío para evitar múltiples envíos
      const submitButton = formulario.querySelector('button[type="submit"]');
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = 'Guardando...';
      }

      // Recopilar datos del formulario
      const nombre = document.getElementById('nombre')?.value || '';
      const tipo = document.getElementById('tipo')?.value || '';
      const genero = document.querySelector('input[name="genero"]:checked')?.value || '';
      const tamano = document.getElementById('tamano')?.value || '';
      const edad = document.getElementById('edad')?.value || '';
      const observaciones = document.getElementById('observaciones')?.value || '';
      const fecha = document.getElementById('fechaSeleccionada')?.value || '';
      const hora = document.getElementById('horaSeleccionada')?.value || '';

      // Recopilar servicios seleccionados
      const serviciosSeleccionados = [];
      document.querySelectorAll('.caja input[type="checkbox"]:checked').forEach(checkbox => {
        serviciosSeleccionados.push(checkbox.value);
      });

      // Validar formato del nombre: solo letras, espacios y acentos, máximo 30 caracteres
      const regexNombre = /^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$/;
      if (nombre && (!regexNombre.test(nombre) || nombre.length > 30)) {
        mostrarMensaje('❌ El nombre solo puede contener letras, espacios y acentos, y máximo 30 caracteres');
        // Rehabilitar el botón si hay error de validación
        if (submitButton) {
          submitButton.disabled = false;
          submitButton.textContent = 'Guardar Turno';
        }
        enviando = false;
        return;
      }

      // Validar campos obligatorios
      if (!nombre || !tipo || !genero || !tamano || !fecha || !hora || serviciosSeleccionados.length === 0) {
        mostrarMensaje('❌ Por favor complete todos los campos obligatorios');
        // Rehabilitar el botón si hay error de validación
        if (submitButton) {
          submitButton.disabled = false;
          submitButton.textContent = 'Guardar Turno';
        }
        return;
      }

      // Preparar datos para enviar
      const turnoData = {
        nombre: nombre,
        tipo: tipo,
        genero: genero,
        tamano: tamano,
        edad: parseInt(edad) || null,
        observaciones: observaciones,
        fecha_turno: fecha,
        hora_turno: hora,
        servicios: serviciosSeleccionados
      };

      // Enviar datos al servidor
      fetch('/turnoscli/guardar-turno/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(turnoData)
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          mostrarCartelGuardado(`✅ Turno guardado exitosamente para ${nombre}`);
          setTimeout(() => {
            // Limpiar el formulario
            formulario.reset();
            // Limpiar campos específicos si es necesario
            document.getElementById('fechaSeleccionada').value = '';
            document.getElementById('horaSeleccionada').value = '';
            // Limpiar checkboxes de servicios
            document.querySelectorAll('.caja input[type="checkbox"]').forEach(checkbox => {
              checkbox.checked = false;
            });
            // Rehabilitar el botón después de limpiar el formulario
            if (submitButton) {
              submitButton.disabled = false;
              submitButton.textContent = 'Guardar Turno';
            }
            enviando = false;
            // Recargar los eventos del calendario para mostrar el nuevo turno
            if (window.calendarCli) {
              window.calendarCli.refetchEvents();
            }
          }, 2000);
        } else {
          mostrarMensaje('❌ Error al guardar el turno: ' + (data.error || 'Error desconocido'));
          // Rehabilitar el botón si hay error del servidor
          if (submitButton) {
            submitButton.disabled = false;
            submitButton.textContent = 'Guardar Turno';
          }
          enviando = false;
        }
      })
      .catch(error => {
        console.error('Error:', error);
        mostrarMensaje('❌ Error de conexión al guardar el turno');
        // Rehabilitar el botón si hay error de conexión
        if (submitButton) {
          submitButton.disabled = false;
          submitButton.textContent = 'Guardar Turno';
        }
        enviando = false;
      });
    });
  }

  if (typeof $ !== 'undefined' && typeof $.fn.selectpicker !== 'undefined') {
    $('.selectpicker').selectpicker();
  }
}

function mostrarMensaje(texto) {
  const cartel = document.createElement('div');
  cartel.className = 'mensaje-flotante';
  cartel.textContent = texto;

  document.body.appendChild(cartel);

  setTimeout(() => {
    cartel.classList.add('visible');
  }, 100);

  setTimeout(() => {
    cartel.classList.remove('visible');
    setTimeout(() => cartel.remove(), 500);
  }, 3000);
}

function mostrarCartelGuardado(texto) {
  const cartel = document.createElement('div');
  cartel.className = 'mensaje-guardado';
  cartel.innerHTML = texto;

  document.body.appendChild(cartel);

  setTimeout(() => cartel.classList.add('visible'), 50);
  setTimeout(() => {
    cartel.classList.remove('visible');
    setTimeout(() => cartel.remove(), 500);
  }, 1500);
}

// Agregar listener para redimensionar ventana y ajustar calendario
window.addEventListener('resize', () => {
  if (window.calendarCli) {
    // Destruir y reinicializar calendario para responsividad
    destruirCalendarioCli();
    inicializarCalendarioCli();
  }
});

// Función para limpiar el calendario cuando se cambia de vista
function limpiarCalendarioCli() {
  if (window.calendarCli) {
    window.calendarCli.destroy();
    window.calendarCli = null;
  }
}

// Agregar listener para limpiar calendario cuando se cambia de contenido
$(document).on('beforeunload', function() {
  limpiarCalendarioCli();
});

// También limpiar cuando se hace click en navegación
$(document).on('click', 'a[href], button[data-url]', function() {
  // Solo limpiar si no es un enlace interno o si es navegación AJAX
  if ($(this).hasClass('nav-link') || $(this).attr('href') !== '#') {
    limpiarCalendarioCli();
  }
});

// Esperar a que FullCalendar y el elemento #calendar estén disponibles antes de inicializar
function waitForFullCalendar() {
  if (typeof FullCalendar !== 'undefined' && document.getElementById('calendar')) {
    initTurnosCli();
  } else {
    setTimeout(waitForFullCalendar, 50);
  }
}

waitForFullCalendar();

// Función para obtener el token CSRF
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
