from django.urls import path
from . import views

app_name = 'empleados'

urlpatterns = [
    path('', views.listar_empleados, name='listar'),
    path('crear/', views.crear_empleado, name='crear'),
    path('editar/<int:empleado_id>/', views.editar_empleado, name='editar'),
    path('eliminar/<int:empleado_id>/', views.eliminar_empleado, name='eliminar'),
    path('reactivar/<int:empleado_id>/', views.reactivar_empleado, name='reactivar'),
    path('detalle/<int:empleado_id>/', views.detalle_empleado, name='detalle'),
    path('exportar/pdf/', views.exportar_empleados_pdf, name='exportar_pdf'),
    path('exportar/pdf/<int:empleado_id>/', views.exportar_empleado_pdf, name='exportar_empleado_pdf'),
]
