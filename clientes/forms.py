from django import forms
from app.models import Clientes  # Usamos el modelo de la app principal
import re
from django.contrib.auth.models import User, Group
from django.db import IntegrityError
from django.utils.crypto import get_random_string
from django.db import transaction

class ClienteForm(forms.ModelForm):
    """Formulario para crear y editar clientes usando tu modelo existente"""
    
    password_temporal = forms.CharField(
        required=False,
        label='Contraseña Inicial (Temporal)',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Dejar vacío para generar DNI como clave'
        }),
        help_text='Solo necesario si quieres que el cliente pueda iniciar sesión. Por defecto, se usará el DNI como contraseña temporal.'
    )
    
    class Meta:
        model = Clientes
        fields = [
            'nombre_cliente', 'apellido_cliente', 'correo_clientes', 
            'telefono_cliente', 'dni_cliente', 'direccion_cliente', 'estado_cliente'
        ]
        widgets = {
            'nombre_cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre'
            }),
            'apellido_cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el apellido'
            }),
            'correo_clientes': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ejemplo@correo.com'
            }),
            'telefono_cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '011-4567-8900'
            }),
            'dni_cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12345678',
                'maxlength': '10'
            }),
            'direccion_cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Calle, número, piso, depto'
            }),
            'estado_cliente': forms.Select(choices=[
                (1, 'Activo'),
                (0, 'Inactivo')
            ], attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'nombre_cliente': 'Nombre *',
            'apellido_cliente': 'Apellido *',
            'correo_clientes': 'Correo Electrónico *',
            'telefono_cliente': 'Teléfono *',
            'dni_cliente': 'DNI *',
            'direccion_cliente': 'Dirección',
            'estado_cliente': 'Estado *'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Campos requeridos
        self.fields['nombre_cliente'].required = True
        self.fields['apellido_cliente'].required = True
        self.fields['correo_clientes'].required = True
        self.fields['telefono_cliente'].required = True
        self.fields['dni_cliente'].required = True
        self.fields['estado_cliente'].required = True
        
        # Campos opcionales
        self.fields['direccion_cliente'].required = False
        
        # Valor por defecto para estado
        if not self.instance.pk:
            self.fields['estado_cliente'].initial = 1
        
        # Agregar clases CSS adicionales
        for field_name, field in self.fields.items():
            if field.required:
                field.widget.attrs['required'] = 'required'
            
            # Agregar clases de validación de Bootstrap
            if field.widget.attrs.get('class'):
                field.widget.attrs['class'] += ' needs-validation'
            else:
                field.widget.attrs['class'] = 'needs-validation'
    
    def clean_dni_cliente(self):
        """Validación personalizada para DNI"""
        dni = self.cleaned_data.get('dni_cliente')
        if dni:
            # Remover espacios y guiones
            dni = dni.replace(' ', '').replace('-', '')
            
            # Verificar que solo contenga números
            if not dni.isdigit():
                raise forms.ValidationError('El DNI debe contener solo números')
            
            # Verificar longitud máxima según tu modelo (10 caracteres)
            if len(dni) > 10:
                raise forms.ValidationError('El DNI no puede tener más de 10 dígitos')
            
            # Verificar longitud mínima (DNI argentino: 7-8 dígitos)
            if len(dni) < 7:
                raise forms.ValidationError('El DNI debe tener al menos 7 dígitos')
            
            # Verificar que no exista otro cliente con el mismo DNI
            if self.instance.pk:
                # Estamos editando, excluir el registro actual
                if Clientes.objects.filter(dni_cliente=dni).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError('Ya existe un cliente con este DNI')
            else:
                # Estamos creando, verificar que no exista
                if Clientes.objects.filter(dni_cliente=dni).exists():
                    raise forms.ValidationError('Ya existe un cliente con este DNI')
                    
        return dni
    
    def clean_telefono_cliente(self):
        """Validación personalizada para teléfono"""
        telefono = self.cleaned_data.get('telefono_cliente')
        if telefono:
            # Remover espacios, guiones y paréntesis
            telefono_limpio = telefono.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            
            # Verificar que contenga solo números
            if not telefono_limpio.isdigit():
                raise forms.ValidationError('El teléfono debe contener solo números, espacios, guiones y paréntesis')
            
            # Verificar longitud mínima
            if len(telefono_limpio) < 8:
                raise forms.ValidationError('El teléfono debe tener al menos 8 dígitos')
                
        return telefono
    
    def clean_correo_clientes(self):
        """Validación personalizada para email"""
        email = self.cleaned_data.get('correo_clientes')
        if email:
            # Convertir a minúsculas para consistencia
            email = email.lower().strip()
            
            # Validar formato básico de email con regex
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, email):
                raise forms.ValidationError('Ingrese un correo electrónico válido')
            
            # Verificar que no contenga espacios
            if ' ' in email:
                raise forms.ValidationError('El correo no puede contener espacios')
            
            # Verificar longitud máxima
            if len(email) > 100:
                raise forms.ValidationError('El correo es demasiado largo (máximo 100 caracteres)')
            
            # Verificar que no exista otro cliente con el mismo email
            if self.instance.pk:
                # Estamos editando, excluir el registro actual
                if Clientes.objects.filter(correo_clientes=email).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError('Ya existe un cliente con este correo electrónico')
            else:
                # Estamos creando, verificar que no exista
                if Clientes.objects.filter(correo_clientes=email).exists():
                    raise forms.ValidationError('Ya existe un cliente con este correo electrónico')
                    
        return email
    
    def clean_nombre_cliente(self):
        """Validación personalizada para nombre"""
        nombre = self.cleaned_data.get('nombre_cliente')
        if nombre:
            # Eliminar espacios al inicio y final
            nombre = nombre.strip()
            
            # Verificar que no esté vacío después del strip
            if not nombre:
                raise forms.ValidationError('El nombre no puede estar vacío')
            
            # Verificar que solo contenga letras y espacios (sin números)
            if not re.match(r'^[A-Za-záéíóúÁÉÍÓÚñÑ\s]+$', nombre):
                raise forms.ValidationError('El nombre solo puede contener letras y espacios')
            
            # Verificar longitud mínima
            if len(nombre) < 2:
                raise forms.ValidationError('El nombre debe tener al menos 2 caracteres')
            
            # Verificar longitud máxima
            if len(nombre) > 45:
                raise forms.ValidationError('El nombre es demasiado largo (máximo 45 caracteres)')
            
            # Capitalizar cada palabra (Primera letra en mayúscula)
            nombre = ' '.join(word.capitalize() for word in nombre.split())
                    
        return nombre
    
    def clean_apellido_cliente(self):
        """Validación personalizada para apellido"""
        apellido = self.cleaned_data.get('apellido_cliente')
        if apellido:
            # Eliminar espacios al inicio y final
            apellido = apellido.strip()
            
            # Verificar que no esté vacío después del strip
            if not apellido:
                raise forms.ValidationError('El apellido no puede estar vacío')
            
            # Verificar que solo contenga letras y espacios (sin números)
            if not re.match(r'^[A-Za-záéíóúÁÉÍÓÚñÑ\s]+$', apellido):
                raise forms.ValidationError('El apellido solo puede contener letras y espacios')
            
            # Verificar longitud mínima
            if len(apellido) < 2:
                raise forms.ValidationError('El apellido debe tener al menos 2 caracteres')
            
            # Verificar longitud máxima
            if len(apellido) > 45:
                raise forms.ValidationError('El apellido es demasiado largo (máximo 45 caracteres)')
            
            # Capitalizar cada palabra (Primera letra en mayúscula)
            apellido = ' '.join(word.capitalize() for word in apellido.split())
                    
        return apellido
    
    def clean_direccion_cliente(self):
        """Validación personalizada para dirección"""
        direccion = self.cleaned_data.get('direccion_cliente')
        if direccion:
            # Eliminar espacios al inicio y final
            direccion = direccion.strip()
            
            # Verificar longitud mínima si se ingresa
            if direccion and len(direccion) < 5:
                raise forms.ValidationError('La dirección debe tener al menos 5 caracteres')
            
            # Verificar longitud máxima
            if len(direccion) > 200:
                raise forms.ValidationError('La dirección es demasiado larga (máximo 200 caracteres)')
            
            # Verificar que no contenga solo números
            if direccion.isdigit():
                raise forms.ValidationError('La dirección debe contener más que solo números')
                    
        return direccion
    
    def clean(self):
        """Validación general del formulario"""
        cleaned_data = super().clean()
        
        # Validar que al menos un campo de contacto esté presente
        telefono = cleaned_data.get('telefono_cliente')
        correo = cleaned_data.get('correo_clientes')
        
        if not telefono and not correo:
            raise forms.ValidationError('Debe proporcionar al menos un método de contacto (teléfono o correo)')
        
        return cleaned_data
    
    def save(self, commit=True):
    # Usamos transaction.atomic() para asegurar que todo el guardado
    # (Cliente, User, Grupo) sea una única transacción atómica.
        with transaction.atomic(): 
            cliente = super().save(commit=False)
            dni = self.cleaned_data.get('dni_cliente')
            email = self.cleaned_data.get('correo_clientes')
            password = self.cleaned_data.get('password_temporal') or dni 
            
            # Inicializar user fuera del try
            user = None 

            try:
                if cliente.pk:
                    # 1. Modo Edición
                    user = cliente.user
                    
                    # Sincronizar campos del User
                    user.first_name = cliente.nombre_cliente
                    user.last_name = cliente.apellido_cliente
                    if email and user.email != email:
                        user.email = email
                    
                    # El DNI NO se está usando como username en edición, pero sí en creación.
                    # Como el username se mantiene el existente, esto está bien.
                    user.save()

                else:
                    # 2. Modo Creación
                    
                    # Asignar DNI como username por defecto
                    username_default = dni 
                    
                    # Crear la instancia de User
                    user = User.objects.create_user(
                        username=username_default,
                        email=email,
                        password=password,
                        first_name=cliente.nombre_cliente,
                        last_name=cliente.apellido_cliente,
                    )
                    
                    # Guardar la relación con el User (necesario para el save del cliente)
                    cliente.user = user 
                    
                    # 3. Asignar Grupo 'Cliente'
                    try:
                        cliente_group = Group.objects.get(name='Cliente')
                        user.groups.add(cliente_group)
                    except Group.DoesNotExist:
                        print("ADVERTENCIA: El grupo 'Cliente' no existe en Django. Por favor, créelo.")
                        
                # ********** GUARDADO FINAL DEL CLIENTE DENTRO DE LA TRANSACCIÓN **********
                if commit:
                    # Si llegamos aquí, user se creó/actualizó, ahora guardamos el cliente
                    # ESTO AHORA ES PARTE DE LA TRANSACCIÓN ATÓMICA
                    cliente.save() 
                    
            except IntegrityError as e:
                # Si el error ocurre DESPUÉS de crear el User (en un guardado secundario)
                if user and not cliente.pk:
                    # En creación, si falla, hacemos un rollback borrando el User
                    user.delete() 
                
                # Manejo de errores de unicidad
                if 'username' in str(e):
                    raise forms.ValidationError({'dni_cliente': 'El DNI ya está siendo usado como nombre de usuario por otro cliente.'})
                if 'email' in str(e):
                    raise forms.ValidationError({'correo_clientes': 'El correo electrónico ya está siendo usado por otro cliente.'})
                raise # Re-lanza cualquier otro IntegrityError

        return cliente