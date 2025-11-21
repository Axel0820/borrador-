/**
 * Script unificado y mejorado para manejar la carga dinámica del modal de Administración de Carrusel,
 * la navegación interna (Lista <-> Formularios), y el envío de formularios (POST) vía AJAX 
 * para prevenir el reenvío del formulario y la barra blanca.
 *
 * ASUME: El modal principal es '#carrusel-imagen' y su contenido es '#carrusel-content'.
 * ASUME: La URL para recargar la lista de imágenes debe ser accesible globalmente 
 * (p. ej., obtenida del botón que abre el modal).
 */
$(document).ready(function() {

    const carruselModalElement = document.getElementById('carrusel-imagen');
    const carruselContentElement = document.getElementById('carrusel-content');
    let listaCarruselUrl = null; // Variable para guardar la URL de la lista

    if (!carruselModalElement || !carruselContentElement) {
        console.error("No se encontraron los elementos '#carrusel-imagen' o '#carrusel-content'.");
        return;
    }

    // =========================================================================
    // 1. Manejo del Modal Principal (#carrusel-imagen)
    // =========================================================================

    carruselModalElement.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const url = button.getAttribute('data-url');
        
        if (!url) {
            console.error("El botón disparador del modal no tiene el atributo 'data-url'.");
            return;
        }

        // Guarda la URL de la lista para usarla después del POST exitoso
        listaCarruselUrl = url; 
        
        // Mostrar estado de carga (Spinner)
        showSpinner(carruselContentElement, 'Cargando gestión de carrusel...');

        // Realizar la petición AJAX para cargar la lista de contenido
        loadContent(url, carruselContentElement);
    });
    
    // Limpiar el contenido del modal cuando se cierra
    carruselModalElement.addEventListener('hidden.bs.modal', function () {
        carruselContentElement.innerHTML = '';
        listaCarruselUrl = null; 
    });

    // =========================================================================
    // 2. Manejo de Navegación Interna (GET)
    // =========================================================================
    
    // Delegación de eventos para capturar clics en los enlaces de acción internos (Agregar, Editar, Eliminar)
    $(document).on('click', '#carrusel-content a.carousel-modal-link', function(e) {
        e.preventDefault();
        
        const newUrl = $(this).attr('href');
        
        if (newUrl) {
            // Mostrar spinner antes de cargar el nuevo formulario
            showSpinner(carruselContentElement, 'Cargando formulario...');
            
            // Cargar el nuevo contenido (formulario, confirmación, etc.) vía AJAX
            loadContent(newUrl, carruselContentElement);
        }
    });

    // =========================================================================
    // 3. Manejo del Envío del Formulario (POST)
    // =========================================================================

    // Delegación de eventos para interceptar el SUBMIT de los formularios cargados
    $(document).on('submit', '#carrusel-content form', function(e) {
        e.preventDefault(); 

        const form = $(this);
        const actionUrl = form.attr('action');
        // FormData es crucial para manejar la carga de archivos (imágenes)
        const formData = new FormData(this);

        // Deshabilita el botón de envío
        form.find('button[type="submit"]').prop('disabled', true).text('Guardando...');

        $.ajax({
            url: actionUrl,
            type: 'POST',
            data: formData,
            processData: false, 
            contentType: false, 
            
            success: function(data, textStatus, xhr) {
                // Si Django devuelve 204 No Content (POST exitoso, patrón PRG)
                if (xhr.status === 204) { 
                    
                    // 1. Forzar un GET para recargar el contenido de la lista (Evita reenvío y barra blanca)
                    showSpinner(carruselContentElement, 'Actualizando lista...');
                    loadContent(listaCarruselUrl, carruselContentElement, function() {
                         // Callback después de recargar la lista: No necesitamos hacer nada más 
                         // porque el modal principal ya está abierto.
                    });

                } else {
                     // Caso de fallback si Django devuelve un 200 con contenido inesperado
                    handleAjaxError(form.closest('#carrusel-content')[0], `Respuesta inesperada del servidor (HTTP ${xhr.status}).`);
                }
            },
            error: function(xhr, status, error) {
                // Maneja errores de validación de Django (HTTP 400 Bad Request)
                if (xhr.status === 400) { 
                    // Reemplaza el contenido con el formulario que contiene los errores
                    carruselContentElement.innerHTML = xhr.responseText;
                    // Re-habilita el botón en el formulario recargado
                    $(carruselContentElement).find('button[type="submit"]').prop('disabled', false).text('Guardar');
                } else {
                    handleAjaxError(carruselContentElement, `Error al guardar: ${xhr.status} ${error}`);
                }
            }
        });
    });

    // =========================================================================
    // 4. Funciones de Utilidad
    // =========================================================================

    /** Muestra el spinner de carga */
    function showSpinner(containerElement, message) {
        containerElement.innerHTML = `
            <div class="text-center p-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p class="mt-2 text-muted">${message}</p>
            </div>
        `;
    }

    /** Muestra un mensaje de error AJAX */
    function handleAjaxError(containerElement, message) {
        containerElement.innerHTML = `
            <div class="alert alert-danger text-center" role="alert">
                <i class="bi bi-x-octagon-fill me-2"></i> ${message}
            </div>
        `;
    }

    /** Carga contenido vía GET AJAX */
    function loadContent(url, containerElement, callback = null) {
        $.ajax({
            url: url,
            type: 'GET',
            success: function(data) {
                containerElement.innerHTML = data;
                if (callback) callback();
                // 💡 No necesitamos re-adjuntar eventos aquí, ya que usamos delegación ($(document).on(...)).
            },
            error: function(xhr, status, error) {
                handleAjaxError(containerElement, `Error al cargar: ${status}.`);
            }
        });
    }
});