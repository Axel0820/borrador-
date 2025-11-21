// proveedores.js - Manejo de modales y AJAX para proveedores
// NO usar $(document).ready() porque se ejecuta solo una vez
// Usar delegación de eventos para que funcione con contenido AJAX

// Modal para AGREGAR proveedor - usar off/on para evitar duplicados
$(document).off('show.bs.modal', '#modalAgregarProveedor').on('show.bs.modal', '#modalAgregarProveedor', function () {
        $.ajax({
            url: "/proveedores/crear/",
            type: "GET",
            success: function(data) {
                $('#modal-body-content').html(data); 
            },
            error: function() {
                $('#modal-body-content').html('<p class="text-danger">Error al cargar el formulario.</p>');
            }
        });
    });

    // Modal para EDITAR proveedor - usar off/on para evitar duplicados
    $(document).off('show.bs.modal', '#modalEditarProveedor').on('show.bs.modal', '#modalEditarProveedor', function(event) {
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
    $("#tablaProveedores tbody tr").each(function() {
        let textoFila = $(this).text().toLowerCase();
        $(this).toggle(textoFila.includes(filtro));
    });
});

// Confirmación de ELIMINAR con SweetAlert2 - SOLO para proveedores
$(document).on("click", "#tablaProveedores .btn-eliminar", function (e) {
        e.preventDefault();
        const url = $(this).attr("href");
        const nombreProveedor = $(this).data("nombre");
        const estado = $(this).data("estado");
        
        // Mensajes diferentes según el estado
        let title, text, confirmText, successTitle;
        
        if (estado === 'activo') {
            title = '¿Desactivar proveedor?';
            text = `El proveedor "${nombreProveedor}" será desactivado.`;
            confirmText = 'Sí, desactivar';
            successTitle = '¡Desactivado!';
        } else {
            title = '¿Eliminar permanentemente?';
            text = `El proveedor "${nombreProveedor}" será eliminado de forma permanente. Esta acción no se puede deshacer.`;
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
                        // Recargar la lista de proveedores sin cambiar de vista
                        $.ajax({
                            url: '/proveedores/',
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
                            text: 'No se pudo desactivar el proveedor'
                        });
                    }
                });
            }
        });
    });

    // Envío del formulario de AGREGAR con AJAX
    $(document).on('submit', '#formAgregarProveedor', function(e) {
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
            url: "/proveedores/crear/",
            type: "POST",
            data: formData,
            success: function(response) {
                if (response.success) {
                    // Cerrar modal correctamente
                    const modalElement = document.getElementById('modalAgregarProveedor');
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
                        // Recargar la lista de proveedores sin cambiar de vista
                        $.ajax({
                            url: '/proveedores/',
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
                    text: 'No se pudo guardar el proveedor. Verifique los datos ingresados.'
                });
                $(this).data('submitting', false);  // Resetear en caso de error
            }
        });
    });

    // Envío del formulario de EDITAR con AJAX
    $(document).on('submit', '#formEditarProveedor', function(e) {
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
                    const modalElement = document.getElementById('modalEditarProveedor');
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
                        // Recargar la lista de proveedores sin cambiar de vista
                        $.ajax({
                            url: '/proveedores/',
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
                    text: 'No se pudo actualizar el proveedor'
                });
            }
        });
    });

    // Validación en tiempo real para CUIT - solo números y guión
    $(document).on('input', 'input[name="cuit_prov"]', function() {
        const cuit = $(this).val();
        // Solo permitir números y guión
        const cuitLimpio = cuit.replace(/[^0-9-]/g, '');
        $(this).val(cuitLimpio);
        
        // Validar formato (eliminar guiones para contar dígitos)
        const soloNumeros = cuitLimpio.replace(/-/g, '');
        if (soloNumeros.length > 0 && soloNumeros.length !== 11) {
            $(this).addClass('is-invalid');
            if (!$(this).next('.invalid-feedback').length) {
                $(this).after('<div class="invalid-feedback">El CUIT debe tener 11 dígitos (formato: 20-12345678-9)</div>');
            }
        } else {
            $(this).removeClass('is-invalid');
            $(this).next('.invalid-feedback').remove();
        }
    });
    
    // Prevenir ingreso de letras en CUIT
    $(document).on('keypress', 'input[name="cuit_prov"]', function(e) {
        const char = String.fromCharCode(e.which);
        const soloNumerosGuion = /^[0-9-]$/;
        
        if (!soloNumerosGuion.test(char)) {
            e.preventDefault();
            return false;
        }
    });

    // Validación en tiempo real para teléfono
    $(document).on('input', 'input[name="telefono_prov"]', function() {
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
    $(document).on('blur', 'input[name="correo_prov"]', function() {
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
    $(document).on('input', 'input[name="nombre_prov"]', function() {
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

    // Prevenir ingreso de números en nombre
    $(document).on('keypress', 'input[name="nombre_prov"]', function(e) {
        const char = String.fromCharCode(e.which);
        const soloLetras = /^[A-Za-záéíóúÁÉÍÓÚñÑ\s]$/;
        
        if (!soloLetras.test(char)) {
            e.preventDefault();
            return false;
        }
    });
