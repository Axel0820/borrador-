# forms.py - Formularios para empleados, productos y proveedores
from django import forms
from django.core.validators import RegexValidator
from app.models import *
from .models import Productos, CarruselImagen


# ------------------------------------STOCK PRODUCTOS---------------------------------------------
    
class ProductoForm(forms.ModelForm):
    
    
    CATEGORIAS = [
        ('Gato', 'Gato'),
        ('Perro', 'Perro'),
        ('Pez', 'Pez'),
        
    ]

    

    categoria_prod = forms.ChoiceField(
        choices=CATEGORIAS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # NUEVO: ModelChoiceField para unidades
    unidad = forms.ModelChoiceField(
        queryset=Unidades.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Selecciona unidad y empaque"
    )

    # Campo de texto para proveedor (se puede escribir libremente)
    proveedor_prod = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Distribuidora XYZ5, Proveedor ABC, etc.',
            'maxlength': '100'
        }),
        required=False,
        help_text='Escribe el nombre del proveedor (opcional)'
    )
    
    #nombre_prod = forms.CharField(
     #   widget=forms.TextInput(attrs={
      #      "class": "form-control",
       #     "pattern": "^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$",   # Solo letras y espacios
        #    "title": "Solo se permiten letras"
        #})
    #)
    #ACA ES LOANAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    nombre_prod = forms.CharField(
    widget=forms.TextInput(attrs={
        "class": "form-control",
        "pattern": "^[A-Za-zÁÉÍÓÚáéíóúÑñ0-9 ]+$",
        "title": "Solo se permiten letras, números, espacios y caracteres especiales",
        "onkeypress": "return /^[A-Za-zÁÉÍÓÚáéíóúÑñ0-9 ]+$/.test(event.key)",
        "oninput": "this.value = this.value.replace(/[^A-Za-zÁÉÍÓÚáéíóúÑñ0-9 ]/g, '')"
    })
)
    
    # NUEVO: Campo para cantidad numérica de la unidad
    cantidad_unidad = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'step': '0.01',
            'placeholder': 'Ej: 15, 1.5, 2.0, 0.5'
        })
    )

    # NUEVO: Campo para stock mínimo
    stock_minimo = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'placeholder': 'Ej: 10'
        }),
        help_text='Cantidad mínima de stock antes de mostrar alerta de stock bajo'
    )

    class Meta:
        model = Productos
        fields = ['nombre_prod', 'precio_prod', 'stock_prod', 'stock_minimo', 'categoria_prod', 'unidad', 'cantidad_unidad', 'proveedor_prod', 'estado_prod', 'imagen_prod']
        widgets = {


            'precio_prod': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'stock_prod': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'categoria_prod': forms.Select(attrs={'class': 'form-control'}),
            'estado_prod': forms.Select(
                choices=[(1, 'Activo'), (0, 'Inactivo')],
                attrs={'class': 'form-select'}
            ),
            'imagen_prod': forms.ClearableFileInput(attrs={'class': 'form-control'}),

        }
        labels = {
            'imagen_prod': 'Imagen del producto',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['imagen_prod'].required = False  # <-- IMPORTANTE

#----------------------------------------FINAL DE STOCK PRODUCTOS-------------------------------------------


class CarruselImagenForm(forms.ModelForm):
    class Meta:
        model = CarruselImagen
        fields = ['titulo', 'imagen', 'activo'] 