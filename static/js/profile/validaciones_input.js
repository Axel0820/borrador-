document.addEventListener("DOMContentLoaded", function() {

    // === SOLO LETRAS ===
    function soloLetras(e) {
        const char = String.fromCharCode(e.which);
        const regex = /^[a-zA-ZÀ-ÿ\s]+$/; // permite letras, acentos y espacios
        if (!regex.test(char)) {
            e.preventDefault();
        }
    }

    // === SOLO NÚMEROS ===
    function soloNumeros(e) {
        const char = String.fromCharCode(e.which);
        const regex = /^[0-9]+$/;
        if (!regex.test(char)) {
            e.preventDefault();
        }
    }

    // === TELÉFONO (permite números y símbolos + - () espacios) ===
    function soloTelefono(e) {
        const char = String.fromCharCode(e.which);
        const regex = /^[0-9+\-\s()]+$/;
        if (!regex.test(char)) {
            e.preventDefault();
        }
    }

    // === Obtener los campos por ID (generados por Django) ===
    const campoNombre = document.getElementById("id_nombre");
    const campoApellido = document.getElementById("id_apellido");
    const campoDniEmp = document.getElementById("id_dni_emp");
    const campoDniCli = document.getElementById("id_dni_cliente");
    const campoTelefono = document.getElementById("id_telefono");

    // === Asignar eventos ===
    if (campoNombre) campoNombre.addEventListener("keypress", soloLetras);
    if (campoApellido) campoApellido.addEventListener("keypress", soloLetras);
    if (campoDniEmp) campoDniEmp.addEventListener("keypress", soloNumeros);
    if (campoDniCli) campoDniCli.addEventListener("keypress", soloNumeros);
    if (campoTelefono) campoTelefono.addEventListener("keypress", soloTelefono);

    // === Evitar pegar valores inválidos (opcional) ===
    [campoDniEmp, campoDniCli, campoTelefono].forEach(campo => {
        if (campo) {
            campo.addEventListener("paste", e => {
                const pastedData = e.clipboardData.getData('text');
                if (!/^[0-9+\-\s()]*$/.test(pastedData)) {
                    e.preventDefault();
                }
            });
        }
    });
});

// === FUNCIONES PARA MANEJO DE MODALES DE PERFIL ===

function showFormErrors(formElement, formErrors) {
    formElement.querySelectorAll('.text-danger.small').forEach(el => el.remove());
    formElement.querySelectorAll('.form-control.is-invalid').forEach(el => {
        el.classList.remove('is-invalid');
    });

    for (const fieldName in formErrors) {
        const fieldElement = formElement.elements[fieldName];

        if (fieldElement) {
            fieldElement.classList.add('is-invalid');
            const fieldDiv = fieldElement.closest('.form-group, .mb-3');

            if (fieldDiv) {
                formErrors[fieldName].forEach(errorObj => {
                    const errorText = document.createElement('div');
                    errorText.className = 'text-danger small';
                    errorText.textContent = errorObj.message || errorObj;
                    fieldDiv.appendChild(errorText);
                });
            }
        } else if (fieldName === '__all__') {
            alert("Error de formulario general: " + formErrors[fieldName].join(' '));
        }
    }
}

function attachProfileSubmitHandler(formElement) {
    const modalElement = formElement.closest('.modal');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const url = formElement.getAttribute('action');

    $(formElement).off('submit', handleFormSubmission);

    function handleFormSubmission(e) {
        e.preventDefault();

        const formData = new FormData(formElement);
        showFormErrors(formElement, {});

        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (response.status === 400) {
                return response.json().then(data => { throw data; });
            }
            if (!response.ok) {
                throw new Error("Error del servidor: " + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                const modal = bootstrap.Modal.getInstance(modalElement);
                if (modal) {
                    modal.hide();
                }
                window.location.reload();
            } else {
                alert(data.message || "Error al actualizar el perfil.");
            }
        })
        .catch(error => {
            if (error && error.errors) {
                showFormErrors(formElement, error.errors);
            } else {
                alert("Ocurrió un error inesperado. Inténtelo de nuevo.");
            }
        });
    }

    $(formElement).on('submit', handleFormSubmission);

    if (window.setupInputValidations) {
        window.setupInputValidations(formElement);
    }
}

function attachPasswordChangeSubmit(form) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const url = form.getAttribute('action') || "/profiles/password_change/";

    $(form).off('submit', handlePasswordSubmission);

    function handlePasswordSubmission(e) {
        e.preventDefault();

        const formData = new FormData(form);
        const submitButton = form.querySelector('button[type="submit"]');

        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = 'Procesando...';
        }

        fetch(url, {
            method: 'POST',
            body: formData,
            headers: { 'X-CSRFToken': csrfToken, }
        })
        .then(response => {
            if (response.redirected && response.url.includes('done')) {
                return { success: true };
            }
            return response.text().then(html => { throw { html: html }; });
        })
        .then(data => {
            if (data.success) {
                const changeModal = bootstrap.Modal.getInstance(document.getElementById('passwordChangeModal'));
                if (changeModal) {
                    changeModal.hide();
                }
                window.location.reload();
            }
        })
        .catch(error => {
            if (error && error.html) {
                document.getElementById('password-change-content').innerHTML = error.html;

                const formWithError = document.getElementById('password-change-content').querySelector('form');
                if (formWithError) {
                    attachPasswordChangeSubmit(formWithError);
                }
            } else {
                alert("Ocurrió un error inesperado al cambiar la contraseña.");
            }

            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = 'Cambiar Contraseña';
            }
        });
    }

    $(form).on('submit', handlePasswordSubmission);
}

function initProfileModals() {
    $(document).on('click', '.btn-cargar-modal', function(e) {
        e.preventDefault();

        var $this = $(this);
        var url = $this.data('url');
        var targetModalId = $this.data('bs-target');

        var $modalBody = $(targetModalId).find('.modal-body');

        $modalBody.html('<div class="text-center py-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Cargando...</span></div></div>');

        $.ajax({
            url: url,
            type: 'GET',
            success: function(data) {
                $modalBody.html(data);

                $(targetModalId).modal('show');

                var formElement = $modalBody.find('form')[0];
                if (formElement) {
                    if ($(formElement).is('#password-change-form')) {
                        attachPasswordChangeSubmit(formElement);
                    } else {
                        attachProfileSubmitHandler(formElement);
                    }
                }
            },
            error: function() {
                var errorMessage = '<div class="alert alert-danger">Error al cargar el formulario. Inténtelo de nuevo.</div>';
                $modalBody.html(errorMessage);
                $(targetModalId).modal('show');
            }
        });
    });
}

// === INICIALIZACIÓN DE MODALES CUANDO SE DETECTA CONTENIDO DE PERFIL ===
// Esta función se ejecuta cuando se carga contenido vía AJAX
$(document).ajaxComplete(function(event, xhr, settings) {
    // Si el contenido cargado contiene elementos de perfil, inicializar modales
    if ($('.contenador-perfil').length) {
        setTimeout(initProfileModals, 100); // Pequeño delay para asegurar que el DOM esté listo
    }
});

// Exportar funciones para uso global
window.showFormErrors = showFormErrors;
window.attachProfileSubmitHandler = attachProfileSubmitHandler;
window.attachPasswordChangeSubmit = attachPasswordChangeSubmit;
window.initProfileModals = initProfileModals;