// empleados.js - Manejo de modales y AJAX para empleados
// NO usar $(document).ready() porque se ejecuta solo una vez
// Usar delegación de eventos para que funcione con contenido AJAX

// Función para inicializar DataTable de empleados
function initEmpleadosDataTable() {
    // Destruir DataTable existente si ya fue inicializado
    if ($.fn.DataTable.isDataTable("#tablaEmpleados")) {
        $("#tablaEmpleados").DataTable().destroy();
    }
    
    // Inicializar DataTable si existe la tabla
    if ($("#tablaEmpleados").length > 0 && $.fn.DataTable) {
        $("#tablaEmpleados").DataTable({
            language: {
                "decimal": "",
                "emptyTable": "No hay información",
                "info": "Mostrando _START_ a _END_ de _TOTAL_ Entradas",
                "infoEmpty": "Mostrando 0 to 0 of 0 Entradas",
                "infoFiltered": "(Filtrado de _MAX_ total entradas)",
                "infoPostFix": "",
                "thousands": ",",
                "lengthMenu": "Mostrar _MENU_ Entradas",
                "loadingRecords": "Cargando...",
                "processing": "Procesando...",
                "search": "Buscar:",
                "zeroRecords": "Sin resultados encontrados",
                "paginate": {
                    "first": "Primero",
                    "last": "Ultimo",
                    "next": "Siguiente",
                    "previous": "Anterior"
                }
            },
            searching: true,
            paging: true,
            info: true,
            lengthChange: true,
            dom: "lrtip",
            order: [[0, "asc"]],
            columnDefs: [
                { orderable: false, targets: [9] },
                { searchable: false, targets: [9] }
            ]
        });
        
        // Conectar búsqueda personalizada con DataTable
        $("#buscarInput").on("keyup", function() {
            $("#tablaEmpleados").DataTable().search(this.value).draw();
        });
    }
}

// ===== MANEJO DE MODALES =====

// Modal para AGREGAR Empleado
$(document).off("show.bs.modal", "#modalAgregarEmpleado").on("show.bs.modal", "#modalAgregarEmpleado", function () {
    console.log("Modal agregar empleado abierto");
    $.ajax({
        url: "/empleados/crear/",
        type: "GET",
        success: function(data) {
            $("#modal-body-content").html(data);
        },
        error: function() {
            $("#modal-body-content").html("<p class='text-danger'>Error al cargar el formulario.</p>");
        }
    });
});

// Modal para EDITAR empleado
$(document).off("show.bs.modal", "#modalEditarEmpleado").on("show.bs.modal", "#modalEditarEmpleado", function(event) {
    console.log("Modal editar empleado abierto");
    var button = $(event.relatedTarget);
    var url = button.data("url");
    var modalBody = $("#modal-body-editar-content");

    // Mostrar spinner mientras carga
    modalBody.html("<div class='text-center'><div class='spinner-border text-primary' role='status'><span class='visually-hidden'>Cargando...</span></div></div>");

    // Petición AJAX para obtener el formulario de edición
    $.ajax({
        url: url,
        success: function(data) {
            modalBody.html(data);
        },
        error: function() {
            modalBody.html("<p class='text-danger'>Error al cargar el formulario. Inténtelo de nuevo.</p>");
        }
    });
});

// Confirmación de ELIMINAR con SweetAlert2 - SOLO para empleados
$(document).on("click", "#tablaEmpleados .btn-eliminar", function (e) {
    e.preventDefault();
    console.log("Botón eliminar empleado clickeado");

    const url = $(this).attr("href");
    const nombreEmpleado = $(this).data("nombre");
    const estado = $(this).data("estado");

    console.log("Estado:", estado, "URL:", url);

    // Mensajes diferentes según el estado
    let title, text, confirmText, successTitle;

    if (estado === "activo") {
        title = "¿Desactivar Empleado?";
        text = `El Empleado "${nombreEmpleado}" será desactivado.`;
        confirmText = "Sí, desactivar";
        successTitle = "¡Desactivado!";
    } else {
        title = "¿Eliminar permanentemente?";
        text = `El Empleado "${nombreEmpleado}" será eliminado de forma permanente. Esta acción no se puede deshacer.`;
        confirmText = "Sí, eliminar";
        successTitle = "¡Eliminado!";
    }

    Swal.fire({
        title: title,
        text: text,
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#d33",
        cancelButtonColor: "#6c757d",
        confirmButtonText: confirmText,
        cancelButtonText: "Cancelar"
    }).then((result) => {
        if (result.isConfirmed) {
            // Hacer petición AJAX para eliminar
            $.ajax({
                url: url,
                type: "POST",
                data: {
                    csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val()
                },
                success: function(response) {
                    if (response.success) {
                        Swal.fire({
                            icon: "success",
                            title: successTitle,
                            text: response.message,
                            showConfirmButton: false,
                            timer: 1500
                        }).then(() => {
                            // Recargar la lista de empleados sin recargar toda la página
                            $.ajax({
                                url: "/empleados/",
                                headers: {"X-Requested-With": "XMLHttpRequest"},
                                success: function(data) {
                                    $("#contenidoDinamico").html(data);
                                }
                            });
                        });
                    } else {
                        Swal.fire({
                            icon: "error",
                            title: "Error",
                            text: response.message || "Ocurrió un error al procesar la solicitud"
                        });
                    }
                },
                error: function() {
                    Swal.fire({
                        icon: "error",
                        title: "Error",
                        text: "No se pudo conectar con el servidor"
                    });
                }
            });
        }
    });
});

// ===== ENVÍO DE FORMULARIOS =====

// Envío del formulario de AGREGAR con AJAX
$(document).off("submit", "#formAgregarEmpleado").on("submit", "#formAgregarEmpleado", function(e) {
    e.preventDefault();

    // Prevenir múltiples envíos
    if ($(this).data("submitting")) {
        return;
    }
    $(this).data("submitting", true);

    // Limpiar errores previos
    $(".is-invalid").removeClass("is-invalid");
    $(".invalid-feedback").remove();

    var formData = $(this).serialize();
    var $form = $(this);

    $.ajax({
        url: "/empleados/crear/",
        type: "POST",
        data: formData,
        success: function(response) {
            if (response.success) {
                // Cerrar modal correctamente
                const modalElement = document.getElementById("modalAgregarEmpleado");
                const modal = bootstrap.Modal.getInstance(modalElement);
                if (modal) {
                    modal.hide();
                }
                
                // Limpiar backdrop y estado
                setTimeout(() => {
                    $("body").removeClass("modal-open");
                    $(".modal-backdrop").remove();
                    $("body").css("overflow", "");
                    $("body").css("padding-right", "");
                }, 200);

                Swal.fire({
                    icon: "success",
                    title: "¡Éxito!",
                    text: response.message,
                    showConfirmButton: false,
                    timer: 1500
                }).then(() => {
                    // Recargar la lista de empleados
                    $.ajax({
                        url: "/empleados/",
                        headers: {"X-Requested-With": "XMLHttpRequest"},
                        success: function(data) {
                            $("#contenidoDinamico").html(data);
                        }
                    });
                });
            } else if (response.errors) {
                // Mostrar errores campo por campo
                for (let campo in response.errors) {
                    let $campo = $form.find(`#id_${campo}`);
                    $campo.addClass("is-invalid");
                    $campo.after(`<div class="invalid-feedback d-block">${response.errors[campo]}</div>`);
                }

                // También mostrar un mensaje general
                Swal.fire({
                    icon: "error",
                    title: "Errores de validación",
                    html: "Por favor corrija los errores marcados en rojo.",
                    confirmButtonText: "OK"
                });
            }

            $form.data("submitting", false);
        },
        error: function(xhr) {
            console.log("Respuesta de error:", xhr.responseText);
            Swal.fire({
                icon: "error",
                title: "Error",
                text: "No se pudo guardar el Empleado. Verifique los datos ingresados."
            });
            $form.data("submitting", false);
        }
    });
});

// Envío del formulario de EDITAR con AJAX
$(document).off("submit", "#formEditarEmpleado").on("submit", "#formEditarEmpleado", function(e) {
    e.preventDefault();

    // Limpiar errores previos
    $(".is-invalid").removeClass("is-invalid");
    $(".invalid-feedback").remove();

    var formData = $(this).serialize();
    var url = $(this).attr("action");
    var $form = $(this);

    $.ajax({
        url: url,
        type: "POST",
        data: formData,
        success: function(response) {
            if (response.success) {
                // Cerrar modal correctamente
                const modalElement = document.getElementById("modalEditarEmpleado");
                const modal = bootstrap.Modal.getInstance(modalElement);
                if (modal) {
                    modal.hide();
                }
                
                // Limpiar backdrop y estado
                setTimeout(() => {
                    $("body").removeClass("modal-open");
                    $(".modal-backdrop").remove();
                    $("body").css("overflow", "");
                    $("body").css("padding-right", "");
                }, 200);

                Swal.fire({
                    icon: "success",
                    title: "¡Actualizado!",
                    text: response.message,
                    showConfirmButton: false,
                    timer: 1500
                }).then(() => {
                    // Recargar la lista de empleados
                    $.ajax({
                        url: "/empleados/",
                        headers: {"X-Requested-With": "XMLHttpRequest"},
                        success: function(data) {
                            $("#contenidoDinamico").html(data);
                        }
                    });
                });
            } else if (response.errors) {
                // Mostrar errores campo por campo
                for (let campo in response.errors) {
                    let $campo = $form.find(`#id_${campo}`);
                    $campo.addClass("is-invalid");
                    $campo.after(`<div class="invalid-feedback d-block">${response.errors[campo]}</div>`);
                }

                // También mostrar un mensaje general
                Swal.fire({
                    icon: "error",
                    title: "Errores de validación",
                    html: "Por favor corrija los errores marcados en rojo.",
                    confirmButtonText: "OK"
                });
            }
        },
        error: function(xhr) {
            console.log("Respuesta de error:", xhr.responseText);
            Swal.fire({
                icon: "error",
                title: "Error",
                text: "No se pudo actualizar el Empleado. Verifique los datos ingresados."
            });
        }
    });
});

// ===== VALIDACIONES EN TIEMPO REAL =====

// Validación DNI - solo números, exactamente 8 dígitos
$(document).off("input", "input[name='dni_emp']").on("input", "input[name='dni_emp']", function() {
    const dni = $(this).val();
    const soloNumerosRegex = /^[0-9]*$/;

    if (dni && !soloNumerosRegex.test(dni)) {
        $(this).addClass("is-invalid");
        $(this).next(".invalid-feedback").remove();
        $(this).after("<div class='invalid-feedback'>El DNI solo puede contener números</div>");
    } else if (dni && dni.length !== 8) {
        $(this).addClass("is-invalid");
        $(this).next(".invalid-feedback").remove();
        $(this).after("<div class='invalid-feedback'>El DNI debe tener exactamente 8 dígitos</div>");
    } else {
        $(this).removeClass("is-invalid");
        $(this).next(".invalid-feedback").remove();
    }
});

// Prevenir letras en DNI
$(document).off("keypress", "input[name='dni_emp']").on("keypress", "input[name='dni_emp']", function(e) {
    const char = String.fromCharCode(e.which);
    if (!/^[0-9]$/.test(char)) {
        e.preventDefault();
        return false;
    }
});

// Validación NOMBRE - solo letras, máximo 20 caracteres
$(document).off("input", "input[name='nombre_emp']").on("input", "input[name='nombre_emp']", function() {
    const nombre = $(this).val();
    const soloLetrasRegex = /^[A-Za-záéíóúÁÉÍÓÚñÑ\s]*$/;

    if (nombre && !soloLetrasRegex.test(nombre)) {
        $(this).addClass("is-invalid");
        $(this).next(".invalid-feedback").remove();
        $(this).after("<div class='invalid-feedback'>Solo se permiten letras y espacios</div>");
    } else if (nombre && nombre.trim().length < 2) {
        $(this).addClass("is-invalid");
        $(this).next(".invalid-feedback").remove();
        $(this).after("<div class='invalid-feedback'>El nombre debe tener al menos 2 caracteres</div>");
    } else if (nombre && nombre.length > 20) {
        $(this).addClass("is-invalid");
        $(this).next(".invalid-feedback").remove();
        $(this).after("<div class='invalid-feedback'>El nombre no puede tener más de 20 caracteres</div>");
    } else {
        $(this).removeClass("is-invalid");
        $(this).next(".invalid-feedback").remove();
    }
});

// Prevenir números en nombre
$(document).off("keypress", "input[name='nombre_emp']").on("keypress", "input[name='nombre_emp']", function(e) {
    const char = String.fromCharCode(e.which);
    if (!/^[A-Za-záéíóúÁÉÍÓÚñÑ\s]$/.test(char)) {
        e.preventDefault();
        return false;
    }
});

// Validación APELLIDO - solo letras, máximo 20 caracteres
$(document).off("input", "input[name='apellido_emp']").on("input", "input[name='apellido_emp']", function() {
    const apellido = $(this).val();
    const soloLetrasRegex = /^[A-Za-záéíóúÁÉÍÓÚñÑ\s]*$/;

    if (apellido && !soloLetrasRegex.test(apellido)) {
        $(this).addClass("is-invalid");
        $(this).next(".invalid-feedback").remove();
        $(this).after("<div class='invalid-feedback'>Solo se permiten letras y espacios</div>");
    } else if (apellido && apellido.trim().length < 2) {
        $(this).addClass("is-invalid");
        $(this).next(".invalid-feedback").remove();
        $(this).after("<div class='invalid-feedback'>El apellido debe tener al menos 2 caracteres</div>");
    } else if (apellido && apellido.length > 20) {
        $(this).addClass("is-invalid");
        $(this).next(".invalid-feedback").remove();
        $(this).after("<div class='invalid-feedback'>El apellido no puede tener más de 20 caracteres</div>");
    } else {
        $(this).removeClass("is-invalid");
        $(this).next(".invalid-feedback").remove();
    }
});

// Prevenir números en apellido
$(document).off("keypress", "input[name='apellido_emp']").on("keypress", "input[name='apellido_emp']", function(e) {
    const char = String.fromCharCode(e.which);
    if (!/^[A-Za-záéíóúÁÉÍÓÚñÑ\s]$/.test(char)) {
        e.preventDefault();
        return false;
    }
});

// Validación TELÉFONO - solo números, máximo 11 dígitos
$(document).off("input", "input[name='telefono']").on("input", "input[name='telefono']", function() {
    const telefono = $(this).val();
    const soloNumeros = telefono.replace(/\D/g, "");
    
    // Limitar a solo números
    $(this).val(soloNumeros);

    if (soloNumeros.length > 11) {
        $(this).addClass("is-invalid");
        $(this).next(".invalid-feedback").remove();
        $(this).after("<div class='invalid-feedback'>El teléfono no puede tener más de 11 dígitos</div>");
    } else if (soloNumeros.length > 0 && soloNumeros.length < 8) {
        $(this).addClass("is-invalid");
        $(this).next(".invalid-feedback").remove();
        $(this).after("<div class='invalid-feedback'>El teléfono debe tener al menos 8 dígitos</div>");
    } else {
        $(this).removeClass("is-invalid");
        $(this).next(".invalid-feedback").remove();
    }
});

// Prevenir letras en teléfono
$(document).off("keypress", "input[name='telefono']").on("keypress", "input[name='telefono']", function(e) {
    const char = String.fromCharCode(e.which);
    if (!/^[0-9\s\-]$/.test(char)) {
        e.preventDefault();
        return false;
    }
});

// Validación EMAIL
$(document).off("blur", "input[name='correo_emp']").on("blur", "input[name='correo_emp']", function() {
    const email = $(this).val();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (email && !emailRegex.test(email)) {
        $(this).addClass("is-invalid");
        if (!$(this).next(".invalid-feedback").length) {
            $(this).after("<div class='invalid-feedback'>Ingrese un correo electrónico válido</div>");
        }
    } else {
        $(this).removeClass("is-invalid");
        $(this).next(".invalid-feedback").remove();
    }
});

// Validación SUELDO - no negativo, máximo 99,999,999.99
$(document).off("input", "input[name='sueldo']").on("input", "input[name='sueldo']", function() {
    const sueldo = parseFloat($(this).val());

    if (sueldo < 0) {
        $(this).addClass("is-invalid");
        $(this).next(".invalid-feedback").remove();
        $(this).after("<div class='invalid-feedback'>El sueldo no puede ser negativo</div>");
        $(this).val(0);
    } else if (sueldo > 99999999.99) {
        $(this).addClass("is-invalid");
        $(this).next(".invalid-feedback").remove();
        $(this).after("<div class='invalid-feedback'>El sueldo no puede ser mayor a 99,999,999.99</div>");
        $(this).val(99999999.99);
    } else {
        $(this).removeClass("is-invalid");
        $(this).next(".invalid-feedback").remove();
    }
});

// Validación FECHA DE INGRESO
$(document).off("change", "input[name='fecha_ingreso']").on("change", "input[name='fecha_ingreso']", function() {
    const fechaIngreso = new Date($(this).val());
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);

    if (fechaIngreso > hoy) {
        $(this).addClass("is-invalid");
        $(this).next(".invalid-feedback").remove();
        $(this).after("<div class='invalid-feedback'>La fecha de ingreso no puede ser posterior a hoy</div>");
    } else {
        $(this).removeClass("is-invalid");
        $(this).next(".invalid-feedback").remove();
    }
});

// ===== INICIALIZACIÓN DEL DATATABLE EN LISTAR =====
// Código movido desde listar.html
(function() {
    // Esperar a que jQuery y DataTables estén disponibles
    function tryInitDataTable() {
        if (typeof $ !== 'undefined' && 
            typeof $.fn !== 'undefined' && 
            typeof $.fn.DataTable !== 'undefined' &&
            typeof initEmpleadosDataTable === 'function') {
            initEmpleadosDataTable();
        } else {
            // Si no están cargados, esperar 100ms e intentar de nuevo
            setTimeout(tryInitDataTable, 100);
        }
    }
    tryInitDataTable();
})();

// ===== BOTÓN EDITAR EN VISTA DETALLE =====
// Código movido desde detalle.html
$(document).ready(function() {
    console.log('Script de detalle cargado');
    
    var btnEditar = $('#btnEditarEmpleado');
    if (btnEditar.length > 0) {
        console.log('Botón editar encontrado:', btnEditar.length);
        
        btnEditar.click(function() {
            console.log('Click en botón editar');
            var empleadoId = $(this).data('empleado-id');
            console.log('Empleado ID:', empleadoId);
            
            // Cargar el formulario de edición mediante AJAX
            $.ajax({
                url: '/empleados/editar/' + empleadoId + '/',
                type: 'GET',
                success: function(response) {
                    // Insertar el formulario en el modal
                    $('#modal-body-editar-content').html(response);
                    // Mostrar el modal
                    var modal = new bootstrap.Modal(document.getElementById('modalEditarEmpleado'));
                    modal.show();
                    
                    // Configurar el evento de submit del formulario dentro del modal
                    $('#modal-body-editar-content form').on('submit', function(e) {
                        e.preventDefault();
                        var form = $(this);
                        var formData = new FormData(this);
                        
                        $.ajax({
                            url: form.attr('action'),
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
                                    }).then(function() {
                                        // Recargar la página para mostrar los cambios
                                        location.reload();
                                    });
                                } else {
                                    // Mostrar errores en el formulario
                                    if (response.errors) {
                                        Object.keys(response.errors).forEach(function(field) {
                                            var input = form.find('[name="' + field + '"]');
                                            input.addClass('is-invalid');
                                            
                                            var feedback = input.siblings('.invalid-feedback');
                                            if (feedback.length === 0) {
                                                input.after('<div class="invalid-feedback">' + response.errors[field] + '</div>');
                                            } else {
                                                feedback.text(response.errors[field]);
                                            }
                                        });
                                    }
                                }
                            },
                            error: function(xhr) {
                                Swal.fire({
                                    icon: 'error',
                                    title: 'Error',
                                    text: 'Ocurrió un error al guardar los cambios'
                                });
                            }
                        });
                    });
                },
                error: function(xhr, status, error) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'No se pudo cargar el formulario de edición'
                    });
                }
            });
        });
    }
});
