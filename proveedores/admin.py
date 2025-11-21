from django.contrib import admin
from app.models import Proveedoress

@admin.register(Proveedoress)
class ProveedoresAdmin(admin.ModelAdmin):
    list_display = ('id_prov', 'nombre_prov', 'cuit_prov', 'correo_prov', 'telefono_prov', 'estado_prov')
    list_filter = ('estado_prov',)
    search_fields = ('nombre_prov', 'cuit_prov', 'correo_prov')
    list_per_page = 20
