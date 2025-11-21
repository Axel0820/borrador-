from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models import Empleados, Clientes
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django import forms
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.views import PasswordChangeView
from .forms import CustomPasswordChangeForm
from django.db import IntegrityError, transaction
from .forms import EmpleadoProfileForm, ClienteProfileForm, CustomPasswordChangeForm
from django.contrib.auth.models import User
from PIL import Image, ImageDraw, ImageFont
import io

# --- Perfil Avatar --- #

COLOR_MAP = {
    'A': (230, 126, 34),  # Naranja
    'B': (46, 204, 113),  # Verde Esmeralda
    'C': (52, 152, 219),  # Azul
    'D': (155, 89, 182),  # Púrpura
    'E': (22, 160, 133),  # Verde Marino
    'F': (241, 196, 15),  # Amarillo Girasol
    'G': (26, 188, 156),  # Turquesa
    'H': (211, 84, 0),    # Calabaza
    'I': (142, 68, 173),  # Wisteria
    'J': (41, 128, 185),  # Azul oscuro
}
DEFAULT_COLOR = (149, 165, 166) 

def generate_avatar(request, initial):
    initial = initial.upper()
    size = 120
    bg_color = COLOR_MAP.get(initial, DEFAULT_COLOR)
    text_color = (255, 255, 255)

    img = Image.new('RGB', (size, size), color=bg_color)
    d = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", int(size * 0.6))
    except IOError:
        font = ImageFont.load_default()
    
    bbox = d.textbbox((0, 0), initial, font=font)
    
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) / 2
    y = (size - text_height) / 2
    y = y - bbox[1]

    d.text((x, y), initial, fill=text_color, font=font)

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type='image/png')

# --- Perfil Personal --- #

class PerfilOwnerMixin(LoginRequiredMixin, object):
    def get_object(self, queryset=None):
        try:
            if hasattr(self.request.user, 'empleados'):
                return self.request.user.empleados
            
            elif hasattr(self.request.user, 'cliente'): 
                return self.request.user.cliente
                
        except Empleados.DoesNotExist:
            pass
        except Clientes.DoesNotExist:
            pass
        return redirect('index')
        
# --- Perfil Empleado --- #

class EmpleadoProfileView(LoginRequiredMixin, UpdateView):
    model = Empleados
    template_name = 'profiles/perfil_personal.html'
    form_class = EmpleadoProfileForm 

    def dispatch(self, request, *args, **kwargs):
        # Verificar si el usuario tiene perfil de empleado antes de procesar
        try:
            Empleados.objects.get(user=request.user)
        except Empleados.DoesNotExist:
            return redirect('adm2')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return Empleados.objects.get(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empleado = self.object 
        
        context['object'] = {
            'nombre': empleado.nombre_emp,
            'apellido': empleado.apellido_emp,
            'dni': empleado.dni_emp,
            'direccion': empleado.direccion,
            'telefono': empleado.telefono,
            'correo': empleado.email,
            'foto': empleado.foto,
            'cargo': empleado.cargo, 
            'fecha_ingreso': empleado.fecha_ingreso,
            'sueldo': empleado.sueldo,
            'user': self.request.user, 
        }
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form_class()(request.POST, request.FILES, instance=self.object)
        
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        user = self.request.user
        
        try:
            with transaction.atomic():
                empleado = form.save(commit=False)
                empleado.nombre_emp = form.cleaned_data['nombre']
                empleado.apellido_emp = form.cleaned_data['apellido']
                # Para empleados usar 'email', no 'correo'
                empleado.email = form.cleaned_data.get('email', '')
                empleado.save()
                
                user.username = form.cleaned_data['username']
                user.first_name = form.cleaned_data['nombre']
                user.last_name = form.cleaned_data['apellido']
                user.email = empleado.email
                user.save(update_fields=['username', 'first_name', 'last_name', 'email'])
                
        except IntegrityError:
            form.add_error(None, "El nombre de usuario o el correo electrónico ya está en uso.")
            return self.form_invalid(form)

        return JsonResponse({'success': True, 'message': 'Perfil actualizado con éxito.'})

    def form_invalid(self, form):
        errors = form.errors.get_json_data()
        return JsonResponse({'success': False, 'errors': errors}, status=400)
    
    def get_success_url(self):
        return reverse_lazy('perfil_empleado')

# --- Perfil Cliente --- #

class ClienteProfileView(LoginRequiredMixin, UpdateView):
    model = Clientes
    template_name = 'profiles/perfil_personal.html'
    form_class = ClienteProfileForm

    def get_object(self, queryset=None):
        return Clientes.objects.get(user=self.request.user)
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar si el usuario está autenticado
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Verificar si el usuario tiene perfil de cliente antes de procesar
        try:
            Clientes.objects.get(user=request.user)
        except Clientes.DoesNotExist:
            return redirect('index')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return Clientes.objects.get(user=self.request.user) 
            
        return super().dispatch(request, *args, **kwargs)
            
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cliente = self.object 

        context['object'] = {
            'nombre': cliente.nombre_cliente,
            'apellido': cliente.apellido_cliente,
            'dni': cliente.dni_cliente,
            'direccion': cliente.direccion_cliente,
            'telefono': cliente.telefono_cliente,
            'correo': cliente.correo_clientes,
            'foto': cliente.foto,
            'user': self.request.user, 
        }
        return context

    def form_valid(self, form):
        user = self.request.user
        
        try:
            with transaction.atomic():
                cliente = form.save(commit=False)
                cliente.nombre_cliente = form.cleaned_data['nombre']
                cliente.apellido_cliente = form.cleaned_data['apellido']
                cliente.correo_clientes = form.cleaned_data['correo']
                cliente.telefono_cliente = form.cleaned_data['telefono']
                cliente.direccion_cliente = form.cleaned_data['direccion']
                cliente.save()
                
                user.username = form.cleaned_data['username']
                user.first_name = form.cleaned_data['nombre']
                user.last_name = form.cleaned_data['apellido']
                user.email = form.cleaned_data['correo']
                user.save(update_fields=['username', 'first_name', 'last_name', 'email'])
                
        except IntegrityError:
            form.add_error(None, "El nombre de usuario o el correo electrónico ya está en uso.")
            return self.form_invalid(form)

        return JsonResponse({'success': True, 'message': 'Perfil actualizado con éxito.'})

    def form_invalid(self, form):
        errors = form.errors.get_json_data()
        return JsonResponse({'success': False, 'errors': errors}, status=400)
    
    def get_success_url(self):
        return reverse_lazy('perfil_cliente')
    
# --- Editar Perfil personal --- #

def load_profile_edit_form(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autorizado'}, status=403)
        
    try:
        if hasattr(request.user, 'empleados'):
            profile_instance = request.user.empleados
            form_class = EmpleadoProfileForm
        
        elif hasattr(request.user, 'cliente_perfil'):
            profile_instance = request.user.cliente_perfil 
            form_class = ClienteProfileForm
        
        else:
            return JsonResponse({'error': 'Perfil no encontrado (Tipo de usuario no definido)'}, status=404)
            
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Perfil no encontrado (Instancia no existe para el usuario)'}, status=404)
        
    form = form_class(instance=profile_instance)
    return render(request, 'profiles/edit_perfil.html', {
        'form': form,
        'object': profile_instance 
    })

# --- Editar Usuario --- #

def load_user_edit_form(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autorizado'}, status=403)
        
    try:
        if hasattr(request.user, 'empleados'):
            profile_instance = request.user.empleados
            form_class = EmpleadoProfileForm
        
        elif hasattr(request.user, 'cliente_perfil'):
            profile_instance = request.user.cliente_perfil
            form_class = ClienteProfileForm
        
        else:
            return JsonResponse({'error': 'Perfil no encontrado (Tipo de usuario no definido)'}, status=404)
            
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Perfil no encontrado (Instancia no existe para el usuario)'}, status=404)
        
    form = form_class(instance=profile_instance)
    return render(request, 'profiles/edit-user.html', {
        'form': form,
        'object': profile_instance 
    })

# --- Cambio de contrase;a --- #

class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm 
    template_name = 'autenticacion/password_change_form.html'
    success_url = reverse_lazy('password_change_done') 

    def get_success_url(self):
        """Redirigir según el grupo del usuario después de cambiar contraseña"""
        user = self.request.user
        
        # Marcar que ya cambió la contraseña
        if hasattr(user, 'empleados'):
            user.empleados.force_password_change = False
            user.empleados.save()
        
        # Redirigir según grupo
        if user.is_superuser or user.groups.filter(name__in=['Peluquero', 'Cajero', 'Vendedor','Gerente']).exists():
            return reverse_lazy('adm2')
        elif user.groups.filter(name='Cliente').exists():
            return reverse_lazy('index')
        else:
            return reverse_lazy('index')

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = [str(e) for e in field_errors]
            return JsonResponse({'success': False, 'errors': errors}, status=400)
        
        return super().form_invalid(form)

    def form_valid(self, form):
        response = super().form_valid(form)
        
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        return response