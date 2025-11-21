from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
import re
from django.contrib.auth import authenticate

# Register #
# Validaciones Register #
class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),  
        label="Contraseña",
        help_text="Introduce una contraseña segura. Debe tener al menos 8 caracteres.",
        required= True,
        error_messages={
            'required': "La contraseña es obligatoria.",
        }
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}), 
        label="Confirmar contraseña",
        help_text="Introduce nuevamente la contraseña para confirmarla.",
        required= True,
        error_messages={
            'required': "La contraseña es obligatoria.",
        }
    )
    username = forms.CharField(
        required= True,
        error_messages={
        'required': "El usuario es obligatorio.",
        }
    )
    last_name = forms.CharField(
        required= True,
        error_messages={
        'required': "El apellido es obligatorio.",
        }
    )
    first_name = forms.CharField(
        required= True,
        error_messages={
        'required': "El nombre es obligatorio.",
        }
    )
    email = forms.CharField(
        required= True,
        error_messages={
        'required': "El correo es obligatorio.",
        }
    )

    class Meta:
        model= User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
# Validaciones Register #

# Validacion de errores register #
    def clean_username(self): # Username #
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def clean_email(self): # Email #
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este correo electrónico ya está en uso.")
        return email

    def clean(self): # Password 1 y 2 #
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        password1_errors = []
        if not password1:
            password1_errors.append("La contraseña es obligatoria.")
        else:
            if len(password1) < 8:
                password1_errors.append("La contraseña debe tener al menos 8 caracteres.")
            if not re.search(r"[A-Z]", password1):
                password1_errors.append("La contraseña debe contener al menos una letra mayúscula.")
            if not re.search(r"\d", password1):
                password1_errors.append("La contraseña debe contener al menos un número.")
            if not re.search(r"[^A-Za-z0-9]", password1):
                password1_errors.append("La contraseña debe contener al menos un carácter especial.")
        if password1_errors:
            self.add_error('password1', password1_errors)
        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Las contraseñas no coinciden.")
        return cleaned_data
    
    def clean_last_name(self): # last name #
        last_name = self.cleaned_data.get('last_name')
        if not re.match("^[A-Za-záéíóúÁÉÍÓÚÑñ ]+$", last_name):
            raise ValidationError("Solo letras y espacios.")
        return last_name
    
    def clean_first_name(self): # First name #
        first_name = self.cleaned_data.get('first_name')
        if not re.match("^[A-Za-záéíóúÁÉÍÓÚÑñ ]+$", first_name):
            raise ValidationError("Solo letras y espacios.")
        return first_name
# Validacion de errores register #
# Guardar al Usuario #
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            grupo_usuarios, created = Group.objects.get_or_create(name='Usuarios')
            user.groups.add(grupo_usuarios)
        return user
# Guardar al Usuario #
# Register #

# Login #
# Validacion Login 

# Validacion Login #
# Validacion de errores login #
    
# Validacion de errores login #
# Login #

# Cambio password #
class CustomSetPasswordForm(SetPasswordForm):
    error_messages={
            'required': "Debe confirmar la contraseña.", 
            'invalid': "Contraseña inválida.",
            'password_mismatch': "Las contraseñas no coinciden.",
            'password_too_short': "La contraseña debe tener al menos 8 caracteres.",
            'password_no_upper': "La contraseña debe contener al menos una letra mayúscula.",
            'password_no_number': "La contraseña debe contener al menos un número.",
            'password_no_symbol': "La contraseña debe contener al menos un carácter especial.",
            'required': "Este campo es obligatorio.",
            'invalid': "Contraseña inválida."
        }
    new_password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text="Introduce una contraseña segura. Debe tener al menos 8 caracteres.",
    )
    new_password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text="Introduce nuevamente la contraseña para confirmarla.",
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')

        if password1:
            if len(password1) < 8:
                self.add_error('new_password1', "La contraseña debe tener al menos 8 caracteres.")
            if not re.search(r"[A-Z]", password1):
                self.add_error('new_password1', "La contraseña debe contener al menos una letra mayúscula.")
            if not re.search(r"\d", password1):
                self.add_error('new_password1', "La contraseña debe contener al menos un número.")
            if not re.search(r"[^A-Za-z0-9]", password1):
                self.add_error('new_password1', "La contraseña debe contener al menos un carácter especial.")

        def clean_new_password2(self):
            password1 = self.cleaned_data.get("new_password1")
            password2 = self.cleaned_data.get("new_password2")
            if password1 and password2 and password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch'
                )
            return password2
# Cambio password #