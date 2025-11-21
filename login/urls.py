from django.urls import path, include
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('reset_password/', views.MiPasswordResetView.as_view(), name='password_reset'),
    path('reset/<uidb64>/<token>/', views.MiPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password/done/', views.MiPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset_password/complete/', views.MiPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]