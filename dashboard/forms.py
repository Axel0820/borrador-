from django import forms
from .models import CarruselImagen

class CarruselImagenForm(forms.ModelForm):
    class Meta:
        model = CarruselImagen
        fields = ['titulo', 'imagen', 'activo'] 