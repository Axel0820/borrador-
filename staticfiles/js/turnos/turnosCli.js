// Función para inicializar formulario de turnos
function initTurnosCli() {
  const formulario = document.getElementById('formularioTurno');

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
            location.reload();
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
  const calendarEl = document.getElementById('calendar');
  if (calendarEl && typeof FullCalendar !== 'undefined') {
    // Re-inicializar calendario si cambia el ancho de pantalla
    const isMobile = window.innerWidth < 768;
    const calendar = FullCalendar.getCalendar(calendarEl);
    if (calendar) {
      calendar.setOption('initialView', isMobile ? 'timeGridWeek' : 'dayGridMonth');
      calendar.setOption('headerToolbar', isMobile ? {
        left: 'prev,next',
        center: 'title',
        right: 'today'
      } : {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek'
      });
      calendar.render();
    }
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
