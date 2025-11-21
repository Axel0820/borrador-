from django import forms
from app.models import Cajas, Productos, MovimientosCaja
from decimal import Decimal

class AperturaCajaForm(forms.ModelForm):
    saldo_inicial = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.00'),
        widget=forms.NumberInput(attrs={
            'placeholder': 'Ingrese el monto inicial',
            'step': '0.01',
            'min': '0',
            'autofocus': True,
            'onkeypress': 'return event.charCode >= 48 && event.charCode <= 57 || event.charCode == 46'
        }),
        label='Monto Inicial',
        help_text='Dinero en efectivo al momento de abrir la caja'
    )

    class Meta:
        model = Cajas
        fields = ['saldo_inicial']

class CierreCajaForm(forms.Form):
    saldo_final = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.00'),
        widget=forms.NumberInput(attrs={
            'placeholder': 'Ingrese el saldo final',
            'step': '0.01',
            'min': '0',
            'onkeypress': 'return event.charCode >= 48 && event.charCode <= 57 || event.charCode == 46'
        }),
        label='Saldo Final'
    )
    
    observaciones = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Observaciones (opcional)'
        }),
        required=False,
        max_length=500,
        label='Observaciones'
    )


class MovimientoCajaForm(forms.ModelForm):
    """
    Formulario para registrar movimientos manuales de caja
    (ingresos/egresos que no sean ventas)
    """
    
    # Definir choices específicas para cada tipo
    CATEGORIAS_INGRESO = [
        ('venta', 'Venta'),
        ('otros_ingresos', 'Otros Ingresos'),
    ]
    
    CATEGORIAS_EGRESO = [
        ('servicios', 'Pago Servicios'),
        ('otros_egresos', 'Otros Egresos'),
    ]
    
    class Meta:
        model = MovimientosCaja
        fields = ['tipo_movimiento', 'categoria', 'monto', 'descripcion', 'observaciones']
        widgets = {
            'tipo_movimiento': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_tipo_movimiento'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_categoria',
                'disabled': 'disabled'
            }),
            'monto': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01',
                'id': 'id_monto',
                'onkeypress': 'return event.charCode >= 48 && event.charCode <= 57 || event.charCode == 46'
            }),
            'descripcion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Pago de luz del local',
                'maxlength': '255',
                'id': 'id_descripcion'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Detalles adicionales (opcional)',
                'id': 'id_observaciones'
            })
        }
        labels = {
            'tipo_movimiento': 'Tipo de Movimiento',
            'categoria': 'Categoría',
            'monto': 'Monto',
            'descripcion': 'Descripción',
            'observaciones': 'Observaciones'
        }


class FiltroMovimientosForm(forms.Form):
    """
    Formulario para filtrar la lista de movimientos de caja
    por fecha, tipo, categoría, etc.
    """
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'id': 'id_fecha_desde'
        }),
        label='Desde'
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'id': 'id_fecha_hasta'
        }),
        label='Hasta'
    )
    
    tipo_movimiento = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos')] + MovimientosCaja.TIPOS_MOVIMIENTO,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_filtro_tipo'
        }),
        label='Tipo'
    )
    
    categoria = forms.ChoiceField(
        required=False,
        choices=[('', 'Todas')] + MovimientosCaja.CATEGORIAS_MOVIMIENTO,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_filtro_categoria'
        }),
        label='Categoría'
    )
    
    buscar = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por descripción...',
            'id': 'id_buscar'
        }),
        label='Buscar'
    )


class FiltroHistorialCajaForm(forms.Form):
    """
    Formulario para filtrar el historial de cajas
    """
    
    empleado = forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_empleado_historial'
        }),
        label='Empleado'
    )
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'id': 'id_fecha_desde_historial'
        }),
        label='Desde'
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'id': 'id_fecha_hasta_historial'
        }),
        label='Hasta'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Poblar choices de empleados - solo Cajeros y Gerentes
        from app.models import Empleados
        from django.contrib.auth.models import Group
        
        # Obtener grupos de Cajero y Gerente
        grupos_permitidos = Group.objects.filter(name__in=['Cajero', 'Gerente'])
        
        # Filtrar empleados que pertenezcan a esos grupos y estén activos
        empleados = Empleados.objects.filter(
            activo=True,
            user__groups__in=grupos_permitidos
        ).distinct().order_by('apellido_emp', 'nombre_emp')
        
        self.fields['empleado'].choices = [('', 'Todos')] + [
            (emp.id_emp, f"{emp.apellido_emp}, {emp.nombre_emp}") 
            for emp in empleados
        ]