from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_principal, name='principal'),
    path('carrusel/', views.lista_carrusel, name='lista_carrusel'),
    path('carrusel/agregar/', views.agregar_carrusel, name='agregar_carrusel'),
    path('carrusel/editar/<int:pk>/', views.editar_carrusel, name='editar_carrusel'),
    path('carrusel/eliminar/<int:pk>/', views.eliminar_carrusel, name='eliminar_carrusel'),
]
