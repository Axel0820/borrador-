from django.urls import path
from . import views

app_name = 'caja'

urlpatterns = [
    # Sistema de caja
    path('', views.caja_principal, name='principal'),
    path('abrir/', views.abrir_caja, name='abrir'),
    path('cerrar/', views.cerrar_caja, name='cerrar'),
    
    # Movimientos de caja
    path('movimientos/', views.listar_movimientos, name='listar_movimientos'),
    path('movimientos/registrar/', views.registrar_movimiento, name='registrar_movimiento'),
    path('movimientos/anular/<int:movimiento_id>/', views.anular_movimiento, name='anular_movimiento'),
    
    # Detalle de venta
    path('detalle-venta/<int:id_compra>/', views.detalle_venta, name='detalle_venta'),
]