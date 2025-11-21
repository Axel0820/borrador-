from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError
from app.models import Empleados, Clientes
from django.core.validators import RegexValidator

# --- Validadores Personalizados --- #

LETRAS_VALIDATOR = RegexValidator(
    r'^[a-zA-ZÀ-ÿ\s]+$', 
    message="Este campo solo puede contener letras y espacios."
)

NUMEROS_VALIDATOR = RegexValidator(
    r'^[0-9]+$', 
    message="Este campo solo puede contener números."
)

TELEFONO_VALIDATOR = RegexValidator(
    r'^[0-9+\-\s()]+$',
    message="El número de teléfono no es válido. Solo se permiten números, +, -, () y espacios."
)

# --- Eleccion de sexo --- #

SEXO_CHOICES = [
    ('', 'Seleccionar sexo...'), # Placeholder
    ('M', 'Masculino'),
    ('F', 'Femenino'),
    ('O', 'Otro'),
]

# --- Perfil Empleados --- #

class EmpleadoProfileForm(forms.ModelForm):
    nombre = forms.CharField(
        label='Nombre', max_length=100, required=True,
        validators=[LETRAS_VALIDATOR],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'data-only-letters': 'true'
        })
    )
    apellido = forms.CharField(
        label='Apellido', max_length=100, required=True,
        validators=[LETRAS_VALIDATOR],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'data-only-letters': 'true'
        })
    )
    username = forms.CharField(
        label='Nombre de Usuario', max_length=150, required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    dni = forms.CharField(
        label='DNI', required=False,
        validators=[NUMEROS_VALIDATOR],
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'readonly': 'readonly',
            'data-only-numbers': 'true'
        })
    )
    cargo = forms.CharField(
        label='Cargo', required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    sexo_emp = forms.ChoiceField(
        label='Sexo',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'readonly': 'readonly'})
    )

    class Meta:
        model = Empleados
        fields = ['direccion', 'telefono', 'email', 'foto', 'sexo_emp']
        widgets = {
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'sexo_emp': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}), 
        }
        labels = {
            'direccion': 'Dirección',
            'telefono': 'Teléfono',
            'email': 'Correo Electrónico',
            'sexo_emp': 'Sexo',
            'foto': 'Foto de Perfil',
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['foto'].required = False
        if self.instance and self.instance.pk:
            self.fields['nombre'].initial = self.instance.nombre_emp
            self.fields['apellido'].initial = self.instance.apellido_emp
            self.fields['username'].initial = self.instance.user.username
            self.fields['dni'].initial = self.instance.dni_emp
            self.fields['cargo'].initial = self.instance.cargo
            self.fields['dni_emp'] = self.fields.pop('dni')
            self.fields['cargo_display'] = self.fields.pop('cargo')
            if 'dni' in self.fields:
                del self.fields['dni']
            if 'cargo' in self.fields:
                del self.fields['cargo']

    def clean_email(self):
        email = self.cleaned_data['email']
        if Empleados.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe otro empleado con este correo electrónico.")
        return email
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono and not TELEFONO_VALIDATOR.regex.match(telefono):
            raise forms.ValidationError(TELEFONO_VALIDATOR.message)
        return telefono

# --- Perfil Clientes --- #

class ClienteProfileForm(forms.ModelForm):

    nombre = forms.CharField(
        label='Nombre', max_length=45, required=True,
        validators=[LETRAS_VALIDATOR],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'data-only-letters': 'true'
        })
    )
    apellido = forms.CharField(
        label='Apellido', max_length=45, required=True,
        validators=[LETRAS_VALIDATOR],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'data-only-letters': 'true'
        })
    )
    correo = forms.EmailField(
        label='Correo Electrónico', max_length=100, required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'autocomplete': 'email'})
    )
    telefono = forms.CharField(
        label='Teléfono', max_length=45, required=False,
        validators=[TELEFONO_VALIDATOR],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'data-only-telefono': 'true'
        })
    )
    direccion = forms.CharField(
        label='Dirección', max_length=200, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        label='Nombre de Usuario', max_length=150, required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Clientes
        fields = ['dni_cliente', 'foto']
        widgets = {
            'dni_cliente': forms.TextInput(attrs={'class': 'form-control', 'data-only-numbers': 'true'}), 
            'foto': forms.FileInput(attrs={'class': 'form-control'}), 
        }
        labels = {
            'dni_cliente': 'DNI',
            'foto': 'Foto de Perfil',
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['foto'].required = False
        if self.instance and self.instance.pk:
            self.fields['nombre'].initial = self.instance.nombre_cliente
            self.fields['apellido'].initial = self.instance.apellido_cliente
            self.fields['correo'].initial = self.instance.correo_clientes
            self.fields['telefono'].initial = self.instance.telefono_cliente
            self.fields['direccion'].initial = self.instance.direccion_cliente
            self.fields['username'].initial = self.instance.user.username
            
    def clean_correo(self):
        correo = self.cleaned_data['correo']
        if Clientes.objects.filter(correo_clientes=correo).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe otro cliente con este correo electrónico.")
        
        if self.instance and self.instance.user.email != correo:
            if User.objects.filter(email=correo).exclude(pk=self.instance.user.pk).exists():
                raise forms.ValidationError("Este correo electrónico ya está asociado a otra cuenta de usuario.")
        return correo
    
    def clean_dni_cliente(self):
        dni_cliente = self.cleaned_data.get('dni_cliente')
        if dni_cliente and not NUMEROS_VALIDATOR.regex.match(dni_cliente):
            raise forms.ValidationError(NUMEROS_VALIDATOR.message)
        
        # Verificar si otro cliente tiene este DNI (excluyendo el actual)
        if self.instance and self.instance.pk:
            if Clientes.objects.filter(dni_cliente=dni_cliente).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Este DNI ya está en uso.")
        else:
            if Clientes.objects.filter(dni_cliente=dni_cliente).exists():
                raise forms.ValidationError("Este DNI ya está en uso.")
        
        return dni_cliente

# --- Cambio de Contrase;a --- #

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

        self.fields['new_password1'].help_text = _(
            "Tu contraseña debe contener al menos 8 caracteres y no debe ser una clave muy común. Te recomendamos usar mayúsculas, minúsculas, números y símbolos."
        )
        self.fields['old_password'].error_messages['required'] = _("⛔ Por favor, ingresa tu contraseña actual.")
        self.fields['new_password1'].error_messages['required'] = _("⛔ Debes ingresar la nueva contraseña.")
        self.fields['new_password2'].error_messages['required'] = _("⛔ Debes confirmar la nueva contraseña.")

    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get('new_password1')
        
        try:
            super().clean_new_password1()
        except forms.ValidationError as e:
            translated_errors = []
            for message in e.message:
                if 'too short' in message.lower():
                    translated_errors.append(_("❌ La contraseña es demasiado corta. Debe tener al menos 8 caracteres."))
                elif 'common password' in message.lower():
                    translated_errors.append(_("❌ Esta contraseña es demasiado común. Por favor, elige una más segura."))
                elif 'entirely numeric' in message.lower():
                    translated_errors.append(_("❌ La contraseña no puede ser completamente numérica."))
                elif 'user_name' in message.lower():
                    translated_errors.append(_("❌ La contraseña es demasiado similar a tu nombre de usuario."))
                else:
                    translated_errors.append(message)
            
            if translated_errors:
                raise forms.ValidationError(translated_errors)

        return new_password1
    
    def clean(self):
        cleaned_data = super().clean()
        
        if self.non_field_errors():
            new_non_field_errors = []
            for error in self.non_field_errors():
                error_message = str(error)
                
                if 'incorrect' in error_message.lower():
                    new_non_field_errors.append(
                        _("🚫 La contraseña actual que ingresaste es incorrecta.")
                    )
                elif 'did not match' in error_message.lower():
                    new_non_field_errors.append(
                        _("❌ Las nuevas contraseñas no coinciden. Por favor, asegúrate de que sean iguales.")
                    )
                else:
                    new_non_field_errors.append(error)
            self._errors[forms.NON_FIELD_ERRORS] = new_non_field_errors

        return cleaned_data
    
# --- Perfil Empleados --- #
class EmpleadoProfileForm(forms.ModelForm):
    nombre = forms.CharField(label='Nombre', max_length=100, required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    apellido = forms.CharField(label='Apellido', max_length=100, required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(label='Nombre de Usuario', max_length=150, required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    dni = forms.CharField(
        label='DNI', required=False,
        validators=[NUMEROS_VALIDATOR],
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'readonly': 'readonly',
            'data-only-numbers': 'true'
        })
    )
    cargo = forms.CharField(
        label='Cargo', required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )

    class Meta:
        model = Empleados
        fields = ['direccion', 'telefono', 'email', 'foto', 'sexo_emp']
        widgets = {
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'sexo_emp': forms.Select(attrs={'class': 'form-select'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}), 
        }
        labels = {
            'direccion': 'Dirección',
            'telefono': 'Teléfono',
            'email': 'Correo Electrónico',
            'sexo_emp': 'Sexo',
            'foto': 'Foto de Perfil',
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['nombre'].initial = self.instance.nombre_emp
            self.fields['apellido'].initial = self.instance.apellido_emp
            self.fields['username'].initial = self.instance.user.username
            
            self.fields['dni'].initial = self.instance.dni_emp
            self.fields['cargo'].initial = self.instance.cargo
            
            # Renombrar campos para que coincidan con la plantilla
            self.fields['dni_emp'] = self.fields['dni']
            self.fields['cargo_display'] = self.fields['cargo']
            
            # Remover los campos originales después de la copia
            del self.fields['dni']
            del self.fields['cargo']

    def clean_email(self):
        email = self.cleaned_data['email']
        if Empleados.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe otro empleado con este correo electrónico.")
        return email
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono and not TELEFONO_VALIDATOR.regex.match(telefono):
            raise forms.ValidationError(TELEFONO_VALIDATOR.message)
        return telefono

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Actualizar campos adicionales si están presentes
        if hasattr(self, 'cleaned_data'):
            if 'nombre' in self.cleaned_data:
                instance.nombre_emp = self.cleaned_data['nombre']
            if 'apellido' in self.cleaned_data:
                instance.apellido_emp = self.cleaned_data['apellido']
                
        if commit:
            instance.save()
            # Actualizar el username del usuario relacionado
            if 'username' in self.cleaned_data and self.cleaned_data['username']:
                instance.user.username = self.cleaned_data['username']
                instance.user.email = self.cleaned_data['email']
                instance.user.save()
                
        return instance

# --- Perfil Clientes --- #
class ClienteProfileForm(forms.ModelForm):
    nombre = forms.CharField(
        label='Nombre', max_length=45, required=True,
        validators=[LETRAS_VALIDATOR],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'data-only-letters': 'true'
        })
    )
    apellido = forms.CharField(
        label='Apellido', max_length=45, required=True,
        validators=[LETRAS_VALIDATOR],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'data-only-letters': 'true'
        })
    )
    correo = forms.EmailField(
        label='Correo Electrónico', max_length=100, required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'autocomplete': 'email'})
    )
    telefono = forms.CharField(
        label='Teléfono', max_length=45, required=False,
        validators=[TELEFONO_VALIDATOR],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'data-only-telefono': 'true'
        })
    )
    direccion = forms.CharField(
        label='Dirección', max_length=200, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        label='Nombre de Usuario', max_length=150, required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Clientes
        fields = ['dni_cliente', 'foto']
        widgets = {
            'dni_cliente': forms.TextInput(attrs={'class': 'form-control', 'data-only-numbers': 'true'}), 
            'foto': forms.FileInput(attrs={'class': 'form-control'}), 
        }
        labels = {
            'dni_cliente': 'DNI',
            'foto': 'Foto de Perfil',
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['foto'].required = False
        if self.instance and self.instance.pk:
            self.fields['nombre'].initial = self.instance.nombre_cliente
            self.fields['apellido'].initial = self.instance.apellido_cliente
            self.fields['correo'].initial = self.instance.correo_clientes
            self.fields['telefono'].initial = self.instance.telefono_cliente
            self.fields['direccion'].initial = self.instance.direccion_cliente
            self.fields['username'].initial = self.instance.user.username
            
    def clean_correo(self):
        correo = self.cleaned_data['correo']
        if Clientes.objects.filter(correo_clientes=correo).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe otro cliente con este correo electrónico.")
        
        if self.instance and self.instance.user.email != correo:
            if User.objects.filter(email=correo).exclude(pk=self.instance.user.pk).exists():
                raise forms.ValidationError("Este correo electrónico ya está asociado a otra cuenta de usuario.")
        return correo
    
    def clean_dni_cliente(self):
        dni_cliente = self.cleaned_data.get('dni_cliente')
        if dni_cliente and not NUMEROS_VALIDATOR.regex.match(dni_cliente):
            raise forms.ValidationError(NUMEROS_VALIDATOR.message)
        
        # Verificar si otro cliente tiene este DNI (excluyendo el actual)
        if self.instance and self.instance.pk:
            if Clientes.objects.filter(dni_cliente=dni_cliente).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Este DNI ya está en uso.")
        else:
            if Clientes.objects.filter(dni_cliente=dni_cliente).exists():
                raise forms.ValidationError("Este DNI ya está en uso.")
        
        return dni_cliente

# --- Cambio de Contrase;a --- #
class CustomPasswordChangeForm(PasswordChangeForm):
    pass