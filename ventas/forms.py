from django import forms

class VentaForm(forms.Form):
    producto = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'producto_id'}),
        required=True,
        label="Producto"
    )
    cantidad = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Cantidad',
            'min': '1',
            'id': 'id_cantidad'
        }),
        label="Cantidad"
    )