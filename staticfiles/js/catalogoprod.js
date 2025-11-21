// catalogoprod.js - Funcionalidad para el catálogo de productos

$(document).ready(function() {
    // Elementos del DOM
    const filtroCategoria = $('#filtroCategoria');
    const buscarProducto = $('#buscarInput');
    const ordenarProductos = $('#ordenarProductos');
    const productosContainer = $('#productosContainer');

    // Función para filtrar productos
    function filtrarProductos() {
        const categoriaSeleccionada = filtroCategoria.val().toLowerCase();
        const textoBusqueda = buscarProducto.val().toLowerCase();
        const ordenSeleccionado = ordenarProductos.val();

        const productos = $('.producto-card');

        // Filtrar productos
        productos.each(function() {
            const producto = $(this);
            const categoria = producto.data('categoria').toLowerCase();
            const nombre = producto.data('nombre');
            const precio = parseFloat(producto.data('precio'));

            // Filtro por categoría
            const cumpleCategoria = categoriaSeleccionada === '' || categoria === categoriaSeleccionada;

            // Filtro por búsqueda
            const cumpleBusqueda = textoBusqueda === '' ||
                nombre.includes(textoBusqueda) ||
                categoria.includes(textoBusqueda);

            // Mostrar/ocultar producto
            if (cumpleCategoria && cumpleBusqueda) {
                producto.show();
            } else {
                producto.hide();
            }
        });

        // Ordenar productos visibles
        ordenarProductosVisibles(ordenSeleccionado);

        // Mostrar/ocultar secciones de categoría según filtros
        $('.categoria-section').each(function() {
            const section = $(this);
            const productosVisibles = section.find('.producto-card:visible');
            if (productosVisibles.length > 0) {
                section.show();
            } else {
                section.hide();
            }
        });
    }

    // Función para ordenar productos visibles
    function ordenarProductosVisibles(orden) {
        // Ordenar dentro de cada sección de categoría
        $('.categoria-container').each(function() {
            const container = $(this);
            const productos = container.find('.producto-card');

            productos.sort(function(a, b) {
                const aEl = $(a);
                const bEl = $(b);
                switch(orden) {
                    case 'categoria':
                        return aEl.data('categoria').localeCompare(bEl.data('categoria'));
                    case 'nombre':
                        return aEl.data('nombre').localeCompare(bEl.data('nombre'));
                    case 'precio_asc':
                        return parseFloat(aEl.data('precio')) - parseFloat(bEl.data('precio'));
                    case 'precio_desc':
                        return parseFloat(bEl.data('precio')) - parseFloat(aEl.data('precio'));
                    default:
                        return 0;
                }
            });

            // Reordenar en el DOM dentro de su contenedor
            productos.each(function() {
                container.append($(this));
            });
        });
    }

    // Event listeners
    filtroCategoria.on('change', filtrarProductos);
    buscarProducto.on('input', filtrarProductos);
    ordenarProductos.on('change', filtrarProductos);

    // Función para mostrar detalles del producto
    window.mostrarDetalle = function(productoId) {
        // Aquí puedes hacer una petición AJAX para obtener detalles completos
        // Por ahora, solo abrimos el modal con información básica
        fetch(`/app/producto/${productoId}/detalle/`)
            .then(response => response.json())
            .then(data => {
                $('#productoModalTitle').text(data.nombre);
                $('#productoModalBody').html(`
                    <div class="row">
                        <div class="col-md-6">
                            <img src="${data.imagen}" class="img-fluid" alt="${data.nombre}">
                        </div>
                        <div class="col-md-6">
                            <h4>${data.nombre}</h4>
                            <p><strong>Categoría:</strong> ${data.categoria}</p>
                            <p><strong>Precio:</strong> $${data.precio.toLocaleString('es-AR', {minimumFractionDigits: 3, maximumFractionDigits: 3})}</p>
                            <p><strong>Unidad:</strong> ${data.unidad}</p>
                            <p><strong>Stock:</strong> ${data.stock}</p>
                            ${data.proveedor ? `<p><strong>Proveedor:</strong> ${data.proveedor}</p>` : ''}
                            ${data.descripcion ? `<p><strong>Descripción:</strong> ${data.descripcion}</p>` : ''}
                        </div>
                    </div>
                `);
                $('#productoModal').modal('show');
            })
            .catch(error => {
                console.error('Error al cargar detalles:', error);
                // Fallback: mostrar modal con mensaje de error
                $('#productoModalTitle').text('Error');
                $('#productoModalBody').html('<p>No se pudieron cargar los detalles del producto.</p>');
                $('#productoModal').modal('show');
            });
    };

    // Inicializar filtros
    filtrarProductos();
});
