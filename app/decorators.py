"""
Decoradores para control de acceso por roles
"""
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from functools import wraps


def solo_gerente(view_func):
    """
    Solo usuarios con grupo 'Gerente' o superusuarios pueden acceder
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        if request.user.groups.filter(name='Gerente').exists():
            return view_func(request, *args, **kwargs)
        
        # Redirigir según tipo de usuario
        if request.user.groups.filter(name='Cliente').exists():
            return redirect('index')
        else:
            return redirect('adm2')
    
    return wrapper


def solo_peluquero(view_func):
    """
    Solo usuarios con grupo 'Peluquero' pueden acceder
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        if request.user.groups.filter(name__in=['Peluquero', 'Gerente']).exists():
            return view_func(request, *args, **kwargs)
        
        return redirect('adm2')
    
    return wrapper


def solo_cajero_vendedor(view_func):
    """
    Solo Cajero, Vendedor o Gerente pueden acceder
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        if request.user.groups.filter(name__in=['Cajero', 'Vendedor', 'Gerente']).exists():
            return view_func(request, *args, **kwargs)
        
        return redirect('adm2')
    
    return wrapper


def acceso_caja(view_func):
    """
    Solo Gerente, Cajero, Vendedor y Superadmin pueden acceder a Caja
    (NO Peluquero)
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Solo Gerente, Cajero y Vendedor tienen acceso a caja
        if request.user.groups.filter(
            name__in=['Gerente', 'Cajero', 'Vendedor']
        ).exists():
            return view_func(request, *args, **kwargs)
        
        # Peluquero y clientes no tienen acceso
        return redirect('adm2')
    
    return wrapper


def acceso_empleados(view_func):
    """
    Solo empleados (no clientes) pueden acceder
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Verificar que NO sea cliente
        if request.user.groups.filter(name='Cliente').exists():
            return redirect('index')
        
        # Verificar que tenga algún grupo de empleado
        if request.user.groups.filter(
            name__in=['Gerente', 'Peluquero', 'Cajero', 'Vendedor']
        ).exists():
            return view_func(request, *args, **kwargs)
        
        raise PermissionDenied
    
    return wrapper


def solo_cliente(view_func):
    """
    Solo clientes pueden acceder
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.groups.filter(name='Cliente').exists():
            return view_func(request, *args, **kwargs)
        
        # Si es empleado, redirigir a adm2
        return redirect('adm2')
    
    return wrapper
