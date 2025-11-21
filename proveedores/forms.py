from django import forms
from app.models import Proveedoress
import re

class ProveedorForm(forms.ModelForm):
    """Formulario para crear y editar proveedores"""
    
    class Meta:
        model = Proveedoress
        fields = [
            'nombre_prov', 'correo_prov', 'cuit_prov', 
            'telefono_prov', 'descripcion_prov', 'estado_prov'
        ]
        widgets = {
            'nombre_prov': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del proveedor'
            }),
            'correo_prov': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ejemplo@correo.com'
            }),
            'cuit_prov': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '20-12345678-9',
                'maxlength': '20',
                'pattern': '[0-9-]+'
            }),
            'telefono_prov': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '011-4567-8900'
            }),
            'descripcion_prov': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción del proveedor',
                'rows': 3
            }),
            'estado_prov': forms.Select(choices=[
                (1, 'Activo'),
                (0, 'Inactivo')
            ], attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'nombre_prov': 'Nombre *',
            'correo_prov': 'Correo Electrónico *',
            'cuit_prov': 'CUIT *',
            'telefono_prov': 'Teléfono *',
            'descripcion_prov': 'Descripción',
            'estado_prov': 'Estado *'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Campos requeridos
        self.fields['nombre_prov'].required = True
        self.fields['correo_prov'].required = True
        self.fields['cuit_prov'].required = True
        self.fields['telefono_prov'].required = True
        self.fields['estado_prov'].required = True
        
        # Campos opcionales
        self.fields['descripcion_prov'].required = False
        
        # Valor por defecto para estado
        if not self.instance.pk:
            self.fields['estado_prov'].initial = 1
        
        # Agregar clases CSS adicionales
        for field_name, field in self.fields.items():
            if field.required:
                field.widget.attrs['required'] = 'required'
            
            # Agregar clases de validación de Bootstrap
            if field.widget.attrs.get('class'):
                field.widget.attrs['class'] += ' needs-validation'
            else:
                field.widget.attrs['class'] = 'needs-validation'
    
    def clean_cuit_prov(self):
        """Validación personalizada para CUIT"""
        cuit = self.cleaned_data.get('cuit_prov')
        if cuit:
            # Remover espacios y guiones
            cuit_clean = cuit.replace(' ', '').replace('-', '')
            
            # Verificar que solo contenga números
            if not cuit_clean.isdigit():
                raise forms.ValidationError('El CUIT debe contener solo números y guiones')
            
            # Verificar longitud (11 dígitos sin guiones)
            if len(cuit_clean) != 11:
                raise forms.ValidationError('El CUIT debe tener 11 dígitos (formato: 20-12345678-9)')
            
            # Verificar unicidad si es un nuevo registro o si cambió el CUIT
            if self.instance.pk:
                # Es una edición
                if Proveedoress.objects.exclude(pk=self.instance.pk).filter(cuit_prov=cuit).exists():
                    raise forms.ValidationError('Ya existe un proveedor con este CUIT')
            else:
                # Es un nuevo registro
                if Proveedoress.objects.filter(cuit_prov=cuit).exists():
                    raise forms.ValidationError('Ya existe un proveedor con este CUIT')
            
            return cuit
        return cuit
    
    def clean_correo_prov(self):
        """Validación personalizada para correo"""
        correo = self.cleaned_data.get('correo_prov')
        if correo:
            # Validar formato de email
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, correo):
                raise forms.ValidationError('Ingrese un correo electrónico válido')
            
            # Verificar unicidad
            if self.instance.pk:
                if Proveedoress.objects.exclude(pk=self.instance.pk).filter(correo_prov=correo).exists():
                    raise forms.ValidationError('Ya existe un proveedor con este correo electrónico')
            else:
                if Proveedoress.objects.filter(correo_prov=correo).exists():
                    raise forms.ValidationError('Ya existe un proveedor con este correo electrónico')
            
            return correo.lower()
        return correo
    
    def clean_telefono_prov(self):
        """Validación personalizada para teléfono"""
        telefono = self.cleaned_data.get('telefono_prov')
        if telefono:
            # Remover espacios y guiones para validar
            telefono_clean = telefono.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            
            # Verificar que contenga solo números
            if not telefono_clean.isdigit():
                raise forms.ValidationError('El teléfono debe contener solo números, espacios y guiones')
            
            # Verificar longitud mínima y máxima
            if len(telefono_clean) < 7:
                raise forms.ValidationError('El teléfono debe tener al menos 7 dígitos')
            
            if len(telefono_clean) > 15:
                raise forms.ValidationError('El teléfono no puede tener más de 15 dígitos')
            
            return telefono
        return telefono
    
    def clean_nombre_prov(self):
        """Validación personalizada para nombre"""
        nombre = self.cleaned_data.get('nombre_prov')
        if nombre:
            # Verificar longitud mínima
            if len(nombre.strip()) < 2:
                raise forms.ValidationError('El nombre debe tener al menos 2 caracteres')
            
            # Verificar que no contenga números
            if any(char.isdigit() for char in nombre):
                raise forms.ValidationError('El nombre no debe contener números')
            
            # Capitalizar primera letra de cada palabra
            return nombre.strip().title()
        return nombre
    
    def clean(self):
        """Validación general del formulario"""
        cleaned_data = super().clean()
        
        # Validaciones adicionales si es necesario
        nombre = cleaned_data.get('nombre_prov')
        cuit = cleaned_data.get('cuit_prov')
        
        if nombre and cuit:
            # Puedes agregar validaciones cruzadas aquí si es necesario
            pass
        
        return cleaned_data
