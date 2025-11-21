/**
 * Script para manejar la carga dinámica del contenido del modal de Administración de Carrusel.
 * Asume que jQuery y Bootstrap 5 (o superior) están cargados.
 * Depende de que la tarjeta de carrusel tenga el atributo data-url y que la URL devuelva un fragmento HTML.
 */
$(document).ready(function() {

    const carruselModal = document.getElementById('carrusel-imagen');

    if (carruselModal) {
        
        // 1. Escucha el evento 'show.bs.modal' de Bootstrap
        carruselModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const url = button.getAttribute('data-url');
            const modalContent = document.getElementById('carrusel-content');
            
            // Mostrar estado de carga (Spinner)
            modalContent.innerHTML = `
                <div class="text-center p-5">
                    <div class="spinner-border text-warning" role="status">
                        <span class="visually-hidden">Cargando...</span>
                    </div>
                    <p class="mt-2 text-muted">Cargando gestión de carrusel...</p>
                </div>
            `;

            // 2. Realizar la petición AJAX para cargar el contenido
            $.ajax({
                url: url,
                type: 'GET',
                success: function(data) {
                    modalContent.innerHTML = data; 
                    // Re-adjuntar eventos para enlaces de navegación dentro del modal (Ej: Editar, Agregar)
                    initializeCarouselModalLinks(); 
                },
                error: function(xhr, status, error) {
                    // Muestra el error para facilitar el debug
                    const errorMessage = `Error (${status}): ${xhr.statusText || 'No se pudo contactar al servidor.'}`;
                    modalContent.innerHTML = `
                        <div class="alert alert-danger text-center" role="alert">
                            <i class="bi bi-x-octagon-fill me-2"></i> Error al cargar el contenido: ${errorMessage}
                            <p class="mt-2 small">Verifica la URL de Django.</p>
                        </div>
                    `;
                }
            });
        });
        
        // 3. Limpiar el contenido del modal cuando se cierra
        carruselModal.addEventListener('hidden.bs.modal', function () {
            document.getElementById('carrusel-content').innerHTML = '';
        });
        
        /**
         * Maneja los clics internos dentro del modal para cargar las vistas de Agregar/Editar/Eliminar 
         * sin cerrar el modal principal.
         */
        function initializeCarouselModalLinks() {
            // Usamos delegación de eventos para capturar clics en elementos cargados dinámicamente
            $(document).off('click.carouselModalLink').on('click.carouselModalLink', '.carousel-modal-link', function(e) {
                e.preventDefault();
                const newUrl = $(this).attr('href');
                const modalContent = document.getElementById('carrusel-content');
                
                // Mostrar spinner para el nuevo contenido/formulario
                modalContent.innerHTML = `
                    <div class="text-center p-5">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Cargando formulario...</span>
                        </div>
                        <p class="mt-2 text-muted">Cargando formulario...</p>
                    </div>
                `;
                
                // Cargar el nuevo contenido (formulario, confirmación, etc.) vía AJAX
                $.ajax({
                    url: newUrl,
                    type: 'GET',
                    success: function(data) {
                        modalContent.innerHTML = data;
                    },
                    error: function(xhr, status, error) {
                        modalContent.innerHTML = `
                            <div class="alert alert-danger text-center" role="alert">
                                Error al cargar el formulario: ${status}.
                            </div>
                        `;
                    }
                });
            });
        }
    }
});