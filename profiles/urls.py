from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth
from . import views

urlpatterns = [
    path('mi-perfil/empleado/', views.EmpleadoProfileView.as_view(), name='perfil_empleado'),
    path('mi-perfil/cliente/', views.ClienteProfileView.as_view(), name='perfil_cliente'),
    path('password_change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth.PasswordChangeDoneView.as_view(template_name='autenticacion/password_change_done.html'), name='password_change_done'),
    path('avatar/<str:initial>/', views.generate_avatar, name='generate_avatar'),
    path('perfil/cargar-edicion/', views.load_profile_edit_form, name='load_edit_profile_form'),
    path('perfil/cargar-usuario/', views.load_user_edit_form, name='load_edit_user_form'),
]