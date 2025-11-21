// modallll no tocar
$(document).on('click', '#btnAgregarProducto', function (e) {
    e.preventDefault();
    $.ajax({
        url: "/productos/registrar/",
        type: "GET",
        success: function(data) {
            $('#modal-body-content').html(data);
            $('#modalAgregarProducto').modal('show');
        }
    });
});






// Captura el evento cuando el modal de editar se muestra
$(document).on('click', '.btn-editar', function(e) {
    e.preventDefault();
    var url = $(this).data('url');

    var modalBody = $('#modal-body-editar-content');

    modalBody.html('<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Cargando...</span></div></div>');

    // Petición ajax para obtener el formulario de edicion
    $.ajax({
        url: url,
        success: function(data) {
            modalBody.html(data);
            $('#modalEditarProducto').modal('show');
        },
        error: function() {
            modalBody.html('<p class="text-danger">Error al cargar el formulario. Inténtelo de nuevo.</p>');
        }
    });
});

// **editar saa



//boton de busacar
$(document).on('keyup', '#buscarInput', function() {
    let filtro = this.value.toLowerCase(); // lo que escribe el usuario
    let filas = document.querySelectorAll("#example tbody tr");

    filas.forEach(fila => {
        let textoFila = fila.textContent.toLowerCase();
        fila.style.display = textoFila.includes(filtro) ? "" : "none";
    });
});


// Confirmación de ELIMINAR - SOLO para productos
$(document).on("click", "#example .btn-eliminar", function (e) {
    e.preventDefault();
    const url = $(this).attr("href");

    Swal.fire({
      title: '¿Estás seguro?',
      text: "Este producto será eliminado definitivamente.",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#6c757d',
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar'
    }).then((result) => {
      if (result.isConfirmed) {
        $.ajax({
          url: url,
          headers: {'X-Requested-With': 'XMLHttpRequest'},
          success: function(data) {
            if (data.success) {
              $.ajax({
                url: '/productos/',
                headers: {'X-Requested-With': 'XMLHttpRequest'},
                success: function(data) {
                  $('#contenidoDinamico').html(data);
                }
              });
            }
          }
        });
      }
    });
  });

// Confirmación de AGREGAR con AJAX y manejo de archivos
// Manejar el envío del formulario de agregar producto (con imagen)
$(document).on('submit', '#formAgregarProducto', function(e) {
    e.preventDefault();

    // Prevenir múltiples envíos
    if ($(this).data('submitting')) {
        return;
    }
    $(this).data('submitting', true);

    // Usamos FormData para incluir los datos del formulario y la imagen.
    var formData = new FormData(this);

    $.ajax({
        url: "/productos/registrar/",
        type: "POST",
        data: formData,
        processData: false,  // Necesario para que jQuery no procese los datos.
        contentType: false,  // Necesario para que jQuery no establezca el tipo de contenido.
        success: function(data) {
            // Verificar si se necesita confirmación por falta de imagen
            if (data.confirm_image) {
                Swal.fire({
                    title: 'Producto sin imagen',
                    text: data.message,
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#d33',
                    cancelButtonColor: '#6c757d',
                    confirmButtonText: 'Sí, guardar inactivo',
                    cancelButtonText: 'Cancelar'
                }).then((result) => {
                    if (result.isConfirmed) {
                        // Agregar flag para confirmar guardado sin imagen
                        formData.append('confirm_no_image', 'true');
                        // Reenviar el formulario con confirmación
                        $.ajax({
                            url: "/productos/registrar/",
                            type: "POST",
                            data: formData,
                            processData: false,
                            contentType: false,
                            success: function(data) {
                                $('#modalAgregarProducto').modal('hide');
                                // Recargar la lista de productos sin cambiar de vista
                                $.ajax({
                                    url: '/productos/',
                                    headers: {'X-Requested-With': 'XMLHttpRequest'},
                                    success: function(data) {
                                        $('#contenidoDinamico').html(data);
                                    }
                                });
                            },
                            error: function() {
                                Swal.fire("Error", "No se pudo guardar el producto", "error");
                                $('#formAgregarProducto').data('submitting', false);
                            }
                        });
                    } else {
                        $('#formAgregarProducto').data('submitting', false);
                    }
                });
            } else {
                $('#modalAgregarProducto').modal('hide');
                // Recargar la lista de productos sin cambiar de vista
                $.ajax({
                    url: '/productos/',
                    headers: {'X-Requested-With': 'XMLHttpRequest'},
                    success: function(data) {
                        $('#contenidoDinamico').html(data);
                    }
                });
            }
        },
        error: function(xhr, status, error) {
            console.log("Error details:", xhr.responseText);
            Swal.fire("Error", "No se pudo procesar la solicitud", "error");
            $('#formAgregarProducto').data('submitting', false);
        }
    });
});

// Confirmación de EDITAR con AJAX (CORREGIDO para manejar imágenes)
$(document).on('submit', '#formEditarProducto', function(e) {
  e.preventDefault();
  const form = this;
  const url = $(form).attr("action");

  // Usar FormData para manejar imágenes
  const formData = new FormData(form);

  Swal.fire({
    title: '¿Confirmar cambios?',
    text: "Se actualizará la información del producto.",
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#6f42c1',
    cancelButtonColor: '#6c757d',
    confirmButtonText: 'Sí, guardar',
    cancelButtonText: 'Cancelar'
  }).then((result) => {
    if (result.isConfirmed) {
      $.ajax({
        type: "POST",
        url: url,
        data: formData, // ¡Este es el cambio clave!
        processData: false, // ¡Añadido!
        contentType: false, // ¡Añadido!
        success: function(data) {
          $('#modalEditarProducto').modal('hide');
          // Recargar la lista de productos sin cambiar de vista
          $.ajax({
            url: '/productos/',
            headers: {'X-Requested-With': 'XMLHttpRequest'},
            success: function(data) {
              $('#contenidoDinamico').html(data);
            }
          });
        },
        error: function() {
          Swal.fire("Error", "No se pudieron guardar los cambios", "error");
        }
      });
    }
  });
});

// Función para manejar el cambio de unidad y controlar el campo cantidad
function manejarCambioUnidad() {
    const unidadSelect = $(this);
    const cantidadInput = unidadSelect.closest('.row').find('input[name="cantidad_unidad"]');
    const selectedOption = unidadSelect.find('option:selected');
    const tipoEmpaque = selectedOption.text().toLowerCase();

    // Si el tipo de empaque es "pieza", deshabilitar el campo cantidad
    if (tipoEmpaque.includes('pieza')) {
        cantidadInput.prop('disabled', true).val('').attr('placeholder', ' N/A');
    } else {
        cantidadInput.prop('disabled', false).attr('placeholder', 'Ej: 1.5');
    }
}

// Evento para el formulario de agregar producto
$(document).on('change', '#formAgregarProducto select[name="unidad"]', manejarCambioUnidad);

// Evento para el formulario de editar producto
$(document).on('change', '#formEditarProducto select[name="unidad"]', manejarCambioUnidad);

// Inicializar el estado del campo cantidad al cargar el formulario
$(document).on('shown.bs.modal', '#modalAgregarProducto, #modalEditarProducto', function() {
    const unidadSelect = $(this).find('select[name="unidad"]');
    if (unidadSelect.length) {
        manejarCambioUnidad.call(unidadSelect[0]);
    }
});

// Botón Limpiar filtros
$(document).on('click', '#btnLimpiarProductos', function(e) {
    e.preventDefault();
    // Limpiar todos los campos del formulario de filtros
    $('#filtroFormProductos')[0].reset();
    // Recargar la lista de productos sin filtros usando AJAX
    $.ajax({
        url: '/productos/',
        headers: {'X-Requested-With': 'XMLHttpRequest'},
        success: function(data) {
            $('#contenidoDinamico').html(data);
        }
    });
});
