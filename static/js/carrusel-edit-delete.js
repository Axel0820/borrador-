/**
 * Script para manejar la navegación modal de Carrusel (Lista <-> Acciones).
 * Intercepta los clics en los enlaces de la lista cargada para cerrar la lista 
 * y abrir el modal de acción (Editar/Agregar/Eliminar) con el contenido cargado por AJAX.
 */
$(document).ready(function() {

    // Delegación de eventos para capturar clics en los enlaces de acción cargados dentro de la lista.
    $(document).on('click', '#carrusel-content .carousel-modal-link', function(e) {
        e.preventDefault();
        
        const link = $(this);
        const newUrl = link.attr('href');
        
        // Obtener el ID del modal de destino (Ej: #carrusel-editar-guardar o #carrusel-eliminar)
        const targetModalId = link.data('bs-target'); 
        
        if (!targetModalId) return;

        // 1. Ocultar el modal de lista actual (#carrusel-imagen)
        const listModalElement = document.getElementById('carrusel-imagen');
        const listModal = bootstrap.Modal.getInstance(listModalElement);
        if (listModal) {
            listModal.hide();
        }

        // 2. Determinar el ID del contenedor de contenido del modal de destino
        const targetModalElement = document.getElementById(targetModalId.replace('#', ''));
        let targetContentId = '';
        
        if (targetModalId === '#carrusel-editar-guardar') {
            targetContentId = 'carrusel-editar-agregar-content';
        } else if (targetModalId === '#carrusel-eliminar') {
            targetContentId = 'carrusel-eliminar-content';
        } else {
            return;
        }
        
        const modalContent = document.getElementById(targetContentId);
        
        // Mostrar spinner de carga
        modalContent.innerHTML = `
            <div class="text-center p-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p class="mt-2 text-muted">Cargando contenido...</p>
            </div>
        `;

        // 3. Mostrar el modal de destino
        const newModal = new bootstrap.Modal(targetModalElement);
        newModal.show();
        
        // 4. Cargar el nuevo contenido vía AJAX
        $.ajax({
            url: newUrl,
            type: 'GET',
            success: function(data) {
                modalContent.innerHTML = data;
                
                // 5. Configurar los botones de 'Cancelar' o 'Volver' en el nuevo formulario/confirmación
                setupReturnToMainModal(targetModalElement);
            },
            error: function(xhr, status, error) {
                modalContent.innerHTML = `
                    <div class="alert alert-danger text-center" role="alert">
                        Error al cargar el contenido: ${status}.
                    </div>
                `;
            }
        });
    });

    /**
     * Configura el botón 'Cancelar' o 'Volver' para cerrar el modal secundario 
     * y reabrir el modal de la lista principal.
     */
    function setupReturnToMainModal(currentModalElement) {
        
        const currentModalInstance = bootstrap.Modal.getInstance(currentModalElement);

        if (currentModalInstance) {
            // Usamos el evento 'hidden.bs.modal' para reabrir la lista solo después de que el modal de acción se ha ocultado.
            $(currentModalElement).one('hidden.bs.modal', function() {
                const listModal = new bootstrap.Modal(document.getElementById('carrusel-imagen'));
                listModal.show();
            });
            
            // Busca enlaces de cancelación que tengan la URL de lista_carrusel y los fuerza a cerrar el modal actual.
            // Esto maneja el enlace "Cancelar" en los formularios de Agregar/Editar/Eliminar.
            $(currentModalElement).find('a[href*="lista_carrusel"]').on('click', function(e) {
                e.preventDefault();
                currentModalInstance.hide();
            });
            // NOTA: Los botones con data-bs-dismiss="modal" funcionan automáticamente.
        }
    }

});