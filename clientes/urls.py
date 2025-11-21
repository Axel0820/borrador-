from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    # Vista principal - listado de clientes
    path('', views.listar_clientes, name='listar'),
    
    # CRUD - Crear, Editar, Eliminar
    path('crear/', views.crear_cliente, name='crear'),
    path('editar/<int:cliente_id>/', views.editar_cliente, name='editar'),
    path('eliminar/<int:cliente_id>/', views.eliminar_cliente, name='eliminar'),
    
    # Vista detalle
    path('detalle/<int:cliente_id>/', views.detalle_cliente, name='detalle'),
    
    # Exportar a PDF
    path('exportar/pdf/', views.exportar_clientes_excel, name='exportar_pdf'),
    path('exportar/pdf/<int:cliente_id>/', views.exportar_cliente_excel, name='exportar_cliente_pdf'),
]