from django.urls import path
from . import views

urlpatterns = [
    path('turnoscli/turnos', views.turnos, name='turnos'),
    path('turnoscli/guardar-turno/', views.guardar_turno, name='guardar_turno'),
    path('turnoscli/turnos-json/', views.turnos_json, name='turnos_json'),
    path('turnosadm/', views.turnosadm, name='turnosadm'),
    path('turnosadm/cambiar-estado/', views.cambiar_estado_turno, name='cambiar_estado_turno'),
    path('turnosadm/detalles/<int:turno_id>/', views.detalles_turno, name='detalles_turno'),
    path('turnosadm/turnos-json/', views.turnosadm_json, name='turnosadm_json'),
    path('turnosadm/pdf/', views.exportar_turnos_pdf, name='exportar_turnos_pdf'),
]
