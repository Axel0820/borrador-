from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    # Sistema de ventas POS
    path('nueva-venta/', views.nueva_venta, name='nueva_venta'),
    path('procesar-venta-form/', views.procesar_venta_form, name='procesar_venta_form'),
    path('procesar-venta-pos/', views.procesar_venta_pos, name='procesar_venta_pos'),
    
    # APIs de ventas
    path('venta/', views.registrar_venta, name='registrar_venta'),
    path('precio-producto/', views.obtener_precio_producto, name='obtener_precio_producto'),
    path('productos-modal/', views.listar_productos_modal, name='listar_productos_modal'),
    
    # Descarga de ticket PDF
    path('ticket-pdf/<int:compra_id>/', views.exportar_ticket_pdf, name='exportar_ticket_pdf'),
]