from django import forms
from django.contrib.auth.models import User, Group
from app.models import Empleados, AuthUser, AuthGroup, AuthUserGroups
from datetime import date
import unicodedata
import re
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


class EmpleadoForm(forms.ModelForm):
    """Formulario para crear y editar empleados"""
    
    CARGO_CHOICES = [
        ('', 'Seleccionar cargo...'),
        ('peluquero', 'Peluquero'),
        ('cajero', 'Cajero'),
        ('vendedor', 'Vendedor'),
        ('gerente', 'Gerente'),
    ]
    
    cargo = forms.ChoiceField(
        choices=CARGO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Cargo'
    )

    class Meta:
        model = Empleados
        fields = [
            'sexo_emp', 'nombre_emp', 'apellido_emp', 'dni_emp',
            'direccion', 'telefono', 'email', 'cargo', 'fecha_ingreso',
            'sueldo', 'activo'
        ]
        widgets = {
            'sexo_emp': forms.Select(
                attrs={'class': 'form-select'},
                choices=[('', 'Seleccionar genero...'), ('Masculino', 'Masculino'), ('Femenino', 'Femenino'), ('Otro', 'Otro')]
            ),
            'nombre_emp': forms.TextInput(attrs={
                'class': 'form-control',
                'pattern': '[A-Za-zÁÉÍÓÚáéíóúÑñ ]+',
                'title': 'Solo letras y espacios',
                'maxlength': '20'
            }),
            'apellido_emp': forms.TextInput(attrs={
                'class': 'form-control',
                'pattern': '[A-Za-zÁÉÍÓÚáéíóúÑñ ]+',
                'title': 'Solo letras y espacios',
                'maxlength': '20'
            }),
            'dni_emp': forms.TextInput(attrs={
                'class': 'form-control',
                'pattern': '[0-9]{8}',
                'title': 'Solo números (8 dígitos)',
                'maxlength': '8'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Av. Corrientes 1234'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej:3875787392',
                'pattern': '[0-9]+',
                'title': 'Solo números',
                'maxlength': '11'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: juan@gmail.com'
            }),
            'fecha_ingreso': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'max': date.today().isoformat()
            }),
            'sueldo': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '99999999.99'
            }),
            'activo': forms.Select(
                attrs={'class': 'form-select'},
                choices=[(True, 'Activo'), (False, 'Inactivo')]
            )
        }
        labels = {
            'sexo_emp': 'Género',
            'nombre_emp': 'Nombre',
            'apellido_emp': 'Apellido',
            'dni_emp': 'DNI',
            'direccion': 'Dirección',
            'telefono': 'Teléfono',
            'email': 'Email',
            'cargo': 'Cargo',
            'fecha_ingreso': 'Fecha de Ingreso',
            'sueldo': 'Sueldo',
            'foto': 'Foto',
            'activo': 'Estado'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Marcar campos como obligatorios para mostrar asteriscos
        self.fields['sexo_emp'].required = True
        self.fields['email'].required = True
        self.fields['direccion'].required = True
        self.fields['cargo'].required = True
        self.fields['fecha_ingreso'].required = True
        
        # Agregar atributo required en el HTML para que aparezcan asteriscos
        for field_name, field in self.fields.items():
            if field.required:
                field.widget.attrs['required'] = 'required'

    
    def clean_nombre_emp(self):
        nombre = self.cleaned_data['nombre_emp']
        if not nombre.replace(' ', '').isalpha():
            raise forms.ValidationError('El nombre solo puede contener letras y espacios.')
        if len(nombre) > 20:
            raise forms.ValidationError('El nombre no puede tener más de 20 caracteres.')
        return nombre

    def clean_apellido_emp(self):
        apellido = self.cleaned_data['apellido_emp']
        # Eliminar espacios y verificar que solo contenga letras
        if not apellido.replace(' ', '').isalpha():
            raise forms.ValidationError('El apellido solo puede contener letras y espacios, no se permiten números.')
        if len(apellido) > 20:
            raise forms.ValidationError('El apellido no puede tener más de 20 caracteres.')
        return apellido

    def clean_cargo(self):
        cargo = self.cleaned_data['cargo']
        if not cargo:
            raise forms.ValidationError('Debe seleccionar un cargo.')
        return cargo

    def clean_sueldo(self):
        sueldo = self.cleaned_data.get('sueldo')
        if sueldo is not None:
            if sueldo < 0:
                raise forms.ValidationError('El sueldo no puede ser negativo.')
            if sueldo > 99999999.99:
                raise forms.ValidationError('El sueldo no puede ser mayor a 99,999,999.99 (10 dígitos con 2 decimales).')
        return sueldo

    def clean_dni_emp(self):
        dni = self.cleaned_data['dni_emp']
        # Eliminar espacios y guiones si los hay
        dni = dni.replace(' ', '').replace('-', '')
        
        if not dni.isdigit():
            raise forms.ValidationError('El DNI solo puede contener números, no se permiten letras.')
        if len(dni) != 8:
            raise forms.ValidationError('El DNI debe tener exactamente 8 dígitos.')
        
        # Validar patrones secuenciales o repetitivos
        # Verificar secuencias ascendentes (12345678)
        if dni == '12345678':
            raise forms.ValidationError('El DNI no puede ser una secuencia numérica simple.')
        
        # Verificar secuencias descendentes (87654321)
        if dni == '87654321':
            raise forms.ValidationError('El DNI no puede ser una secuencia numérica simple.')
        
        # Verificar todos los dígitos iguales (11111111, 22222222, etc.)
        if len(set(dni)) == 1:
            raise forms.ValidationError('El DNI no puede tener todos los dígitos iguales.')
        
        # Verificar patrones intercalados simples (12121212, 12341234)
        if dni == dni[:4] + dni[:4]:
            raise forms.ValidationError('El DNI no puede tener un patrón repetitivo simple.')
        
        # Verificar secuencias ascendentes de cualquier tipo
        is_ascending = all(int(dni[i]) == int(dni[i-1]) + 1 for i in range(1, len(dni)))
        if is_ascending:
            raise forms.ValidationError('El DNI no puede ser una secuencia ascendente.')
        
        # Verificar secuencias descendentes de cualquier tipo
        is_descending = all(int(dni[i]) == int(dni[i-1]) - 1 for i in range(1, len(dni)))
        if is_descending:
            raise forms.ValidationError('El DNI no puede ser una secuencia descendente.')
        
        # Verificar unicidad
        if self.instance and self.instance.pk:
            if Empleados.objects.filter(dni_emp=dni).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Ya existe un empleado con este DNI')
        else:
            if Empleados.objects.filter(dni_emp=dni).exists():
                raise forms.ValidationError('Ya existe un empleado con este DNI')
        return dni

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '')
        if telefono:
            # Permitir solo números
            if not telefono.isdigit():
                raise forms.ValidationError('El teléfono solo puede contener números. No se permiten letras ni caracteres especiales.')
            if len(telefono) > 11:
                raise forms.ValidationError('El teléfono no puede tener más de 11 dígitos.')
        return telefono

    def clean_fecha_ingreso(self):
        fecha_ingreso = self.cleaned_data.get('fecha_ingreso')
        if fecha_ingreso:
            if fecha_ingreso > date.today():
                raise forms.ValidationError('La fecha de ingreso no puede ser posterior a la fecha actual.')
        return fecha_ingreso

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        if email:
            # Verificar formato
            if '@' not in email:
                raise forms.ValidationError('El email debe contener @')
            
            # Verificar unicidad
            if self.instance and self.instance.pk:
                if Empleados.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError('Ya existe un empleado con este email')
            else:
                if Empleados.objects.filter(email=email).exists():
                    raise forms.ValidationError('Ya existe un empleado con este email')
        return email

    def clean(self):
        """Validación general del formulario"""
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre_emp')
        apellido = cleaned_data.get('apellido_emp')
        
        # Verificar que nombre y apellido no sean iguales (sin importar mayúsculas/minúsculas)
        if nombre and apellido:
            if nombre.strip().lower() == apellido.strip().lower():
                self.add_error('nombre_emp', 'El nombre apellido no pueden ser iguales.')
                self.add_error('apellido_emp', 'El apellido y nombre no pueden ser iguales.')
        
        return cleaned_data

    def normalize_text(self, text):
        """Normalizar texto eliminando acentos y caracteres especiales"""
        text = unicodedata.normalize('NFD', text)
        text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
        text = re.sub(r'[^a-zA-Z0-9]', '', text.lower())
        return text

    def generate_username(self, nombre, apellido):
        """Generar username único basado en nombre.apellido"""
        base_username = f"{self.normalize_text(nombre)}.{self.normalize_text(apellido)}"
        username = base_username
        counter = 1
        
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
            
        return username

    def generate_temporary_password(self, cargo):
        """Generar contraseña temporal basada en el cargo"""
        cargo_passwords = {
            'gerente': 'Gerente123!',
            'vendedor': 'Vendedor123!',
            'cajero': 'Cajero123!',
            'peluquero': 'Peluquero123!',
        }
        return cargo_passwords.get(cargo.lower(), 'Empleado123!')

    def assign_group_by_cargo(self, user, cargo):
        """Asignar grupo según el cargo"""
        grupo_mapping = {
            'gerente': 'Gerente',
            'vendedor': 'Vendedor', 
            'cajero': 'Cajero',
            'peluquero': 'Peluquero',
        }
        
        grupo_name = grupo_mapping.get(cargo.lower())
        if grupo_name:
            try:
                grupo = Group.objects.get(name=grupo_name)
                user.groups.add(grupo)
            except Group.DoesNotExist:
                # Si no existe el grupo, crearlo
                grupo = Group.objects.create(name=grupo_name)
                user.groups.add(grupo)

    def send_credentials_email(self, empleado, username, password, request):
        """Enviar email con las credenciales al empleado"""
        if not empleado.email:
            return False
            
        try:
            login_url = request.build_absolute_uri('/login/login/')
            
            context = {
                'empleado': empleado,
                'username': username,
                'password': password,
                'login_url': login_url,
                'current_year': date.today().year,
            }
            
            # Template HTML para el email
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #6f00b5; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9f9f9; }}
                    .credentials {{ background-color: white; padding: 15px; border-left: 4px solid #6f00b5; }}
                    .footer {{ text-align: center; padding: 10px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🐕 Bienvenido a Alma Canina</h1>
                    </div>
                    <div class="content">
                        <p>Hola <strong>{empleado.nombre_emp}</strong>,</p>
                        <p>Te damos la bienvenida a nuestro equipo.</p>
                        
                        <div class="credentials">
                            <h3>Tus credenciales de acceso:</h3>
                            <p><strong>Usuario:</strong> {username}</p>
                            <p><strong>Contraseña temporal:</strong> {password}</p>
                            <p><strong>URL de acceso:</strong> <a href="{login_url}">{login_url}</a></p>
                        </div>
                        
                        <p><strong>IMPORTANTE:</strong> Debes cambiar esta contraseña en tu primer acceso.</p>
                    </div>
                    <div class="footer">
                        <p>&copy; {context['current_year']} Alma Canina - Todos los derechos reservados</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            plain_message = f"""
Hola {empleado.nombre_emp},

Te damos la bienvenida a Alma Canina.

Tus credenciales de acceso son:
Usuario: {username}
Contraseña temporal: {password}
URL de acceso: {login_url}

IMPORTANTE: Debes cambiar esta contraseña en tu primer acceso.

Saludos,
Equipo Alma Canina
            """
            
            # Enviar con timeout para no bloquear
            from django.core.mail import get_connection
            
            connection = get_connection(
                timeout=3  # Timeout de 3 segundos
            )
            
            send_mail(
                subject='🐕 Bienvenido a Alma Canina - Credenciales de Acceso',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[empleado.email],
                html_message=html_message,
                fail_silently=True,  # No bloquear si falla
                connection=connection
            )
            
            return True
            
        except Exception as e:
            print(f"Error al enviar email: {e}")
            return False

    def save(self, commit=True, request=None):
        empleado = super().save(commit=False)
        
        empleado.email = self.cleaned_data.get('email', '')
        empleado.cargo = self.cleaned_data.get('cargo', 'sin cargo')
        
        if commit:
            empleado.save()
            
            # Crear usuario solo si el cargo no es 'sin cargo' y no tiene usuario
            if empleado.cargo != 'sin cargo' and not empleado.user:
                username = self.generate_username(empleado.nombre_emp, empleado.apellido_emp)
                temp_password = self.generate_temporary_password(empleado.cargo)
                
                user = User.objects.create_user(
                    username=username,
                    email=empleado.email or '',
                    password=temp_password,
                    first_name=empleado.nombre_emp,
                    last_name=empleado.apellido_emp,
                    is_active=True
                )
                
                self.assign_group_by_cargo(user, empleado.cargo)
                
                empleado.user = user
                empleado.force_password_change = True
                empleado.save()
                
                # Guardar credenciales temporales
                self.temp_username = username
                self.temp_password = temp_password
                
                # Enviar email
                if request and empleado.email:
                    email_sent = self.send_credentials_email(empleado, username, temp_password, request)
                    self.email_sent = email_sent
                else:
                    self.email_sent = False
            
        return empleado
