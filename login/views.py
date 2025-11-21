from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm, CustomSetPasswordForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView, PasswordResetCompleteView
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from email.mime.image import MIMEImage
from app.models import Clientes
from django.contrib.auth.models import Group
import os

# --- Login --- #
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                login(request, user)
                
                # Verificar si tiene empleado asociado y forzar cambio de contraseña
                if hasattr(user, 'empleados') and user.empleados.force_password_change:
                    return redirect('password_change')
                
                # Redirigir según grupo del usuario
                if user.is_superuser:
                    return redirect('adm2')
                
                # Verificar grupos
                if user.groups.filter(name__in=['Gerente','Peluquero', 'Cajero', 'Vendedor']).exists():
                    # Empleados van al index primero
                    return redirect('adm2')
                elif user.groups.filter(name='Cliente').exists():
                    return redirect('index')
                else:
                    # Usuario sin grupo definido - redirigir a index
                    return redirect('index')
            else:
                error = "Usuario o contraseña incorrecta."
        else:
            error = "Formulario inválido."
        return render(request, 'registration/login.html', {"form": form, "error": error})

    form = AuthenticationForm()
    return render(request, 'registration/login.html', {"form": form})

# --- Logout --- #
@login_required
def signout_view(request):
    logout(request)
    return redirect('index')

# --- Register --- # 
def registro_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            
            # 1. Crear el objeto User de forma segura
            user = form.save() # Crea y guarda el User en un solo paso
            
            # 2. ASIGNACIÓN DEL ROL (Crear el perfil de Cliente)
            try:
                # Recogemos los datos esenciales del User que se creó
                Clientes.objects.create(
                    user=user,
                    # Usamos los datos del User, o valores por defecto/temporales
                    # para los campos obligatorios del perfil:
                    nombre_cliente=user.first_name if user.first_name else user.username, 
                    apellido_cliente=user.last_name if user.last_name else '(Sin apellido)',
                    correo_clientes=user.email,
                    
                    # Campos opcionales que se dejarán vacíos (null=True)
                    # No es necesario incluirlos si son null=True y blank=True.
                    # PERO si el DNI es obligatorio, se debe crear un valor temporal seguro.
                    dni_cliente='00000000', 
                    telefono_cliente='(Pendiente)',
                )
            except Exception as e:
                # Si falla la creación del perfil por cualquier motivo (ej. DNI duplicado/faltante):
                user.delete()
                print(f"Error al crear perfil de cliente: {e}")
                error_msg = f"Error al completar el perfil. Intenta de nuevo. Detalles: {e}"
                # Renderiza el formulario con el error
                return render(request, 'registration/register.html', {"form": form, "error": error_msg})

            # 3. Asignar Grupo (Para control de permisos)
            cliente_group, created = Group.objects.get_or_create(name='Cliente')
            user.groups.add(cliente_group)
            
            # Éxito: Redirigir al login
            return redirect('login') 
        
        else:
            # Si el formulario no es válido (ej. contraseñas no coinciden), renderiza con errores
            error = "Por favor, corrige los errores del formulario."
            return render(request, 'registration/register.html', {"form": form, "error": error})
            
    else:
        form = CustomUserCreationForm()
        return render(request, 'registration/register.html', {"form": form})

# --- Cambiar contraseña --- #
class MiPasswordResetView(PasswordResetView):
    template_name = "autentication/password_reset_form.html"
    email_template_name = "autentication/password_reset_email.html"
    subject_template_name = "autentication/password_reset_subject.txt"
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        user_email = form.cleaned_data['email']
        user = next(form.get_users(user_email), None)
        if user:
            context = {
                'user': user,
                'protocol': 'https' if self.request.is_secure() else 'http',
                'domain': self.request.get_host(),
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': self.token_generator.make_token(user),
                'company_name': 'Alma Canina',
                'company_tagline': 'Amor, cuidado y bienestar animal',
                'company_address': 'Salta, San Carlos, Manzana 22, Casa 27',
                'company_email': 'almacanina25@gmail.com',
                'support_url': 'https://almacanina.com/contacto', #defecto#
                'unsubscribe_url': 'https://almacanina.com/darse-de-baja',
                'logo_cid': 'logo_almacanina',
                'current_year': 2025,
                'cta_text': 'Restablecer contraseña',
                'main_message_html': 'Has solicitado restablecer tu contraseña. Haz clic en el botón de abajo para continuar.',
            }
            subject = render_to_string(self.subject_template_name, context).strip()
            html_content = render_to_string(self.email_template_name, context)
            msg = EmailMultiAlternatives(subject, "", settings.DEFAULT_FROM_EMAIL, [user_email])
            msg.attach_alternative(html_content, "text/html")
            logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo_de_alma_canina[1].png')
            if os.path.exists(logo_path):
                with open(logo_path, 'rb') as f:
                    logo = MIMEImage(f.read())
                    logo.add_header('Content-ID', '<logo_almacanina>')
                    msg.attach(logo)
            msg.send()

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string(self.template_name, {'form': form}, request=self.request)
            return JsonResponse({'success': False, 'html': html})
        return super().form_invalid(form)

class MiPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = "autentication/password_reset_confirm.html"
    success_url = reverse_lazy('password_reset_complete')

    def form_valid(self, form):
        form.save()  # Guardar nueva contraseña
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # No enviamos HTML completo, enviamos solo success
            return JsonResponse({'success': True})
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Construimos un dict con errores por campo
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = [e for e in field_errors]  # Lista de mensajes
            return JsonResponse({'success': False, 'errors': errors})
        return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'invalid_link': True})
            raise
    
class MiPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "autentication/password_reset_complete.html"
    
class MiPasswordResetDoneView(PasswordResetDoneView):
    template_name = "autentication/password_reset_done.html"