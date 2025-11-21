from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from . import views




urlpatterns = [
        path('', views.index, name='index'),
        path('nosotros/', views.nosotros, name='nosotros'),
        path('adm/', views.adm, name='adm'),
        path('adm2/', views.adm2, name='adm2'),

        # Página de inicio (index.html)
        path('productos/', views.listar_productos, name='listarProductos'),
        path('productos/registrar/', views.registrar_producto, name='registrarProducto'),
        path('productos/editar/<int:pk>/', views.editar_producto, name='editarProducto'),
        path('productos/eliminar/<int:pk>/', views.eliminar_producto, name='eliminarProducto'),
        #generar PDF
        path('productos/pdf/', views.exportar_productos_pdf, name='exportarProductosPDF'),


        #TIENDA



            #productos Clientes
        path('productocli/', views.catalogoprod, name='catalogo'),
        path('producto/<int:producto_id>/detalle/', views.detalle_producto, name='detalle_producto'),
        path('productocli/carrito/', views.carrito, name='carrito'),
        path('productocli/favorito/', views.favorito, name='favorito'),
        path('productocli/alimento/', views.alimento, name='alimento'),
        path('productocli/accesorio/', views.accesorio, name='accesorio'),
        path('productocli/juguete/', views.juguete, name='juguete'),
        path('productocli/pipeta/', views.pipeta, name='pipeta'),
        path('productocli/navProd/', views.pesca, name='navProd'),
        path('productocli/pesca/', views.pesca, name='pesca'),
        path('productocli/detalle/', views.detalle, name='detalle'),
        path('productocli/catalogoprod/', views.catalogoprod, name='catalogoprod'),



]
