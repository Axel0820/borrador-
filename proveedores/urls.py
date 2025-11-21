from django.urls import path
from . import views

app_name = 'proveedores'

urlpatterns = [
    path('', views.listar_proveedores, name='listar'),
    path('crear/', views.crear_proveedor, name='crear'),
    path('editar/<int:proveedor_id>/', views.editar_proveedor, name='editar'),
    path('eliminar/<int:proveedor_id>/', views.eliminar_proveedor, name='eliminar'),
    path('detalle/<int:proveedor_id>/', views.detalle_proveedor, name='detalle'),
    path('exportar/pdf/', views.exportar_proveedores_pdf, name='exportar_pdf'),
    path('exportar/pdf/<int:proveedor_id>/', views.exportar_proveedor_pdf, name='exportar_proveedor_pdf'),
]
