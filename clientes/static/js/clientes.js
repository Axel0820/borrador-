// clientes.js - Manejo de modales y AJAX para clientes
// NO usar $(document).ready() porque se ejecuta solo una vez
// Usar delegación de eventos para que funcione con contenido AJAX

// Modal para AGREGAR cliente - usar off/on para evitar duplicados
$(document).off('show.bs.modal', '#modalAgregarCliente').on('show.bs.modal', '#modalAgregarCliente', function () {
        $.ajax({
            url: "/clientes/crear/",
            type: "GET",
            success: function(data) {
                $('#modal-body-content').html(data); 
            },
            error: function() {
                $('#modal-body-content').html('<p class="text-danger">Error al cargar el formulario.</p>');
            }
        });
    });

    // Modal para EDITAR cliente - usar off/on para evitar duplicados
    $(document).off('show.bs.modal', '#modalEditarCliente').on('show.bs.modal', '#modalEditarCliente', function(event) {
        var button = $(event.relatedTarget);
        var url = button.data('url');
        var modalBody = $('#modal-body-editar-content');

        // Mostrar spinner mientras carga
        modalBody.html('<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Cargando...</span></div></div>');

        // Petición AJAX para obtener el formulario de edición
        $.ajax({
            url: url,
            success: function(data) {
                modalBody.html(data);
            },
            error: function() {
                modalBody.html('<p class="text-danger">Error al cargar el formulario. Inténtelo de nuevo.</p>');
            }
        });
    });

// Búsqueda en tiempo real - usar delegación de eventos
$(document).on("keyup", "#buscarInput", function() {
    let filtro = $(this).val().toLowerCase();
    $("#tablaClientes tbody tr").each(function() {
        let textoFila = $(this).text().toLowerCase();
        $(this).toggle(textoFila.includes(filtro));
    });
});

// Confirmación de ELIMINAR con SweetAlert2 - SOLO para clientes
$(document).on("click", "#tablaClientes .btn-eliminar", function (e) {
        e.preventDefault();
        const url = $(this).attr("href");
        const nombreCliente = $(this).data("nombre");
        const estado = $(this).data("estado");
        
        // Mensajes diferentes según el estado
        let title, text, confirmText, successTitle;
        
        if (estado === 'activo') {
            title = '¿Desactivar cliente?';
            text = `El cliente "${nombreCliente}" será desactivado.`;
            confirmText = 'Sí, desactivar';
            successTitle = '¡Desactivado!';
        } else {
            title = '¿Eliminar permanentemente?';
            text = `El cliente "${nombreCliente}" será eliminado de forma permanente. Esta acción no se puede deshacer.`;
            confirmText = 'Sí, eliminar';
            successTitle = '¡Eliminado!';
        }

        Swal.fire({
            title: title,
            text: text,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#6c757d',
            confirmButtonText: confirmText,
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                // Hacer petición AJAX para eliminar
                $.ajax({
                    url: url,
                    type: 'POST',
                    data: {
                        csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
                    },
                    success: function(response) {
                        if (response.success) {
                            Swal.fire({
                                icon: 'success',
                                title: successTitle,
                                text: response.message,
                                showConfirmButton: false,
                                timer: 1500
                    }).then(() => {
                        // Recargar la lista de clientes sin cambiar de vista
                        $.ajax({
                            url: '/clientes/',
                            headers: {'X-Requested-With': 'XMLHttpRequest'},
                            success: function(data) {
                                $('#contenidoDinamico').html(data);
                            }
                        });
                    });
                        } else {
                            Swal.fire({
                                icon: 'error',
                                title: 'Error',
                                text: response.message
                            });
                        }
                    },
                    error: function() {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: 'No se pudo desactivar el cliente'
                        });
                    }
                });
            }
        });
    });

    // Envío del formulario de AGREGAR con AJAX
    $(document).on('submit', '#formAgregarCliente', function(e) {
        e.preventDefault();

        // Prevenir múltiples envíos
        if ($(this).data('submitting')) {
            return;
        }
        $(this).data('submitting', true);

        // Limpiar errores previos
        $('.is-invalid').removeClass('is-invalid');
        $('.invalid-feedback').remove();

        var formData = $(this).serialize();
        var $form = $(this);

        $.ajax({
            url: "/clientes/crear/",
            type: "POST",
            data: formData,
            success: function(response) {
                if (response.success) {
                    // Cerrar modal correctamente
                    const modalElement = document.getElementById('modalAgregarCliente');
                    const modal = bootstrap.Modal.getInstance(modalElement);
                    if (modal) {
                        modal.hide();
                    }
                    
                    // Limpiar backdrop y estado
                    setTimeout(() => {
                        $('body').removeClass('modal-open');
                        $('.modal-backdrop').remove();
                        $('body').css('overflow', '');
                        $('body').css('padding-right', '');
                    }, 200);
                    
                    Swal.fire({
                        icon: 'success',
                        title: '¡Éxito!',
                        text: response.message,
                        showConfirmButton: false,
                        timer: 1500
                    }).then(() => {
                        // Recargar la lista de clientes sin cambiar de vista
                        $.ajax({
                            url: '/clientes/',
                            headers: {'X-Requested-With': 'XMLHttpRequest'},
                            success: function(data) {
                                $('#contenidoDinamico').html(data);
                            }
                        });
                    });
                } else if (response.errors) {
                    // Mostrar errores campo por campo
                    for (let campo in response.errors) {
                        let $campo = $form.find(`#id_${campo}`);
                        $campo.addClass('is-invalid');
                        $campo.after(`<div class="invalid-feedback d-block">${response.errors[campo]}</div>`);
                    }

                    // También mostrar un mensaje general
                    Swal.fire({
                        icon: 'error',
                        title: 'Errores de validación',
                        html: 'Por favor corrija los errores marcados en rojo.',
                        confirmButtonText: 'OK'
                    });
                }
                $(this).data('submitting', false);  // Resetear en caso de error
            },
            error: function(xhr) {
                console.log('Error response:', xhr.responseText);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'No se pudo guardar el cliente. Verifique los datos ingresados.'
                });
                $(this).data('submitting', false);  // Resetear en caso de error
            }
        });
    });

    // Envío del formulario de EDITAR con AJAX
    $(document).on('submit', '#formEditarCliente', function(e) {
        e.preventDefault();
        
        // Limpiar errores previos
        $('.is-invalid').removeClass('is-invalid');
        $('.invalid-feedback').remove();
        
        var formData = $(this).serialize();
        var url = $(this).attr('action');
        var $form = $(this);
        
        $.ajax({
            url: url,
            type: "POST",
            data: formData,
            success: function(response) {
                if (response.success) {
                    // Cerrar modal correctamente
                    const modalElement = document.getElementById('modalEditarCliente');
                    const modal = bootstrap.Modal.getInstance(modalElement);
                    if (modal) {
                        modal.hide();
                    }
                    
                    // Limpiar backdrop y estado
                    setTimeout(() => {
                        $('body').removeClass('modal-open');
                        $('.modal-backdrop').remove();
                        $('body').css('overflow', '');
                        $('body').css('padding-right', '');
                    }, 200);
                    
                    Swal.fire({
                        icon: 'success',
                        title: '¡Actualizado!',
                        text: response.message,
                        showConfirmButton: false,
                        timer: 1500
                    }).then(() => {
                        // Recargar la lista de clientes sin cambiar de vista
                        $.ajax({
                            url: '/clientes/',
                            headers: {'X-Requested-With': 'XMLHttpRequest'},
                            success: function(data) {
                                $('#contenidoDinamico').html(data);
                            }
                        });
                    });
                } else if (response.errors) {
                    // Mostrar errores campo por campo
                    for (let campo in response.errors) {
                        let $campo = $form.find(`#id_${campo}`);
                        $campo.addClass('is-invalid');
                        $campo.after(`<div class="invalid-feedback d-block">${response.errors[campo]}</div>`);
                    }
                    
                    // También mostrar un mensaje general
                    Swal.fire({
                        icon: 'error',
                        title: 'Errores de validación',
                        html: 'Por favor corrija los errores marcados en rojo.',
                        confirmButtonText: 'OK'
                    });
                }
            },
            error: function(xhr) {
                console.log('Error response:', xhr.responseText);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'No se pudo actualizar el cliente'
                });
            }
        });
    });

    // Validación en tiempo real para DNI
    $(document).on('input', 'input[name="dni_cliente"]', function() {
        const dni = $(this).val().replace(/\D/g, ''); // Solo números
        $(this).val(dni);
        
        if (dni.length > 0 && dni.length !== 8) {
            $(this).addClass('is-invalid');
            if (!$(this).next('.invalid-feedback').length) {
                $(this).after('<div class="invalid-feedback">El DNI debe tener 8 dígitos</div>');
            }
        } else {
            $(this).removeClass('is-invalid');
            $(this).next('.invalid-feedback').remove();
        }
    });

    // Validación en tiempo real para teléfono
    $(document).on('input', 'input[name="telefono_cliente"]', function() {
        const telefono = $(this).val();
        const telefonoLimpio = telefono.replace(/[^\d\s\-\(\)]/g, '');
        $(this).val(telefonoLimpio);
        
        const soloNumeros = telefonoLimpio.replace(/\D/g, '');
        if (soloNumeros.length > 0 && soloNumeros.length < 8) {
            $(this).addClass('is-invalid');
            if (!$(this).next('.invalid-feedback').length) {
                $(this).after('<div class="invalid-feedback">El teléfono debe tener al menos 8 dígitos</div>');
            }
        } else {
            $(this).removeClass('is-invalid');
            $(this).next('.invalid-feedback').remove();
        }
    });

    // Validación para email
    $(document).on('blur', 'input[name="correo_clientes"]', function() {
        const email = $(this).val();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (email && !emailRegex.test(email)) {
            $(this).addClass('is-invalid');
            if (!$(this).next('.invalid-feedback').length) {
                $(this).after('<div class="invalid-feedback">Ingrese un email válido</div>');
            }
        } else {
            $(this).removeClass('is-invalid');
            $(this).next('.invalid-feedback').remove();
        }
    });

    // Validación en tiempo real para NOMBRE - solo letras
    $(document).on('input', 'input[name="nombre_cliente"]', function() {
        const nombre = $(this).val();
        const soloLetrasRegex = /^[A-Za-záéíóúÁÉÍÓÚñÑ\s]*$/;
        
        if (nombre && !soloLetrasRegex.test(nombre)) {
            $(this).addClass('is-invalid');
            $(this).next('.invalid-feedback').remove();
            $(this).after('<div class="invalid-feedback">Solo se permiten letras y espacios</div>');
        } else if (nombre && nombre.trim().length < 2) {
            $(this).addClass('is-invalid');
            $(this).next('.invalid-feedback').remove();
            $(this).after('<div class="invalid-feedback">El nombre debe tener al menos 2 caracteres</div>');
        } else {
            $(this).removeClass('is-invalid');
            $(this).next('.invalid-feedback').remove();
        }
    });

    // Validación en tiempo real para APELLIDO - solo letras
    $(document).on('input', 'input[name="apellido_cliente"]', function() {
        const apellido = $(this).val();
        const soloLetrasRegex = /^[A-Za-záéíóúÁÉÍÓÚñÑ\s]*$/;
        
        if (apellido && !soloLetrasRegex.test(apellido)) {
            $(this).addClass('is-invalid');
            $(this).next('.invalid-feedback').remove();
            $(this).after('<div class="invalid-feedback">Solo se permiten letras y espacios</div>');
        } else if (apellido && apellido.trim().length < 2) {
            $(this).addClass('is-invalid');
            $(this).next('.invalid-feedback').remove();
            $(this).after('<div class="invalid-feedback">El apellido debe tener al menos 2 caracteres</div>');
        } else {
            $(this).removeClass('is-invalid');
            $(this).next('.invalid-feedback').remove();
        }
    });

    // Prevenir ingreso de números en nombre y apellido
    $(document).on('keypress', 'input[name="nombre_cliente"], input[name="apellido_cliente"]', function(e) {
        const char = String.fromCharCode(e.which);
        const soloLetras = /^[A-Za-záéíóúÁÉÍÓÚñÑ\s]$/;
        
        if (!soloLetras.test(char)) {
            e.preventDefault();
            return false;
        }
    });
