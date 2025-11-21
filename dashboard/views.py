from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, Q
from django.db.models.functions import Concat, Cast
from django.db import models as M
from django.http import HttpRequest
from django.utils import timezone
from datetime import timedelta, datetime
import pandas as pd
import json
import calendar
try:
    from app.forms import CarruselImagenForm 
except ImportError:
    class DummyForm: 
        def __init__(self, *args, **kwargs): pass
        def is_valid(self): return True
        def save(self): pass
    CarruselImagenForm = DummyForm

from app.models import Empleados, Clientes, Productos, Turnos, Compras, DetalleCompras, CarruselImagen

def format_ventas_chart(df, date_range_start_ts, period='W', label_chart='Ingresos Semanales'):
    
    if df.empty:
        return {'labels': [], 'data': [], 'label_chart': label_chart}

    df_filtered = df[df['fecha_hora'] >= date_range_start_ts]
    
    if df_filtered.empty:
        return {'labels': [], 'data': [], 'label_chart': label_chart}
    
    ventas_resampled = None
    labels = []

    if period == 'D':
        ventas_resampled = df_filtered.set_index('fecha_hora')['monto'].resample('D').sum().fillna(0)
        labels = [f.strftime("%d %b") for f in ventas_resampled.index]
        
    elif period == 'H':
        max_day_ts = df_filtered['fecha_hora'].max().normalize()
        start_time_ts = max_day_ts + timedelta(hours=6)
        end_time_ts = max_day_ts + timedelta(hours=23)
        full_index = pd.date_range(start=start_time_ts, end=end_time_ts, freq='h')
        df_set_index = df_filtered.set_index('fecha_hora')
        
        ventas_resampled_all_hours = df_set_index['monto'].resample('h').sum().reindex(full_index, fill_value=0)
        ventas_resampled = ventas_resampled_all_hours
        labels = [f.strftime("%H:%M") for f in ventas_resampled.index]
        if labels and labels[0] != '06:00':
            labels[0] = '06:00'
            
    elif period == 'W':
        ventas_resampled = df_filtered.set_index('fecha_hora')['monto'].resample('W').sum().fillna(0)
        labels = [f"Semana del {f.to_period('W').start_time.strftime('%d %b')}" for f in ventas_resampled.index]
    
    elif period == 'M':
        today = pd.to_datetime(timezone.now()).tz_localize(None).normalize()
        full_index_dates = pd.date_range(
            start=date_range_start_ts.normalize(), 
            end=today, 
            freq='D'
        )
        df_set_index = df_filtered.set_index('fecha_hora')
        ventas_resampled_all_days = df_set_index['monto'].resample('D').sum().reindex(full_index_dates, fill_value=0)
        
        ventas_resampled = ventas_resampled_all_days
        labels = [f.strftime("%d %b") for f in ventas_resampled.index]
        
    if ventas_resampled is None:
        return {'labels': [], 'data': [], 'label_chart': label_chart}

    data = [float(monto) for monto in ventas_resampled.values.tolist()]
    
    return {'labels': labels, 'data': data, 'label_chart': label_chart}

@login_required
def dashboard_principal(request):
    end_datetime = timezone.now()
    end_date = end_datetime.date()
    today_ts_naive = pd.to_datetime(end_datetime).tz_localize(None)
    start_ts_month_calendar = today_ts_naive.normalize().replace(day=1) 
    start_date_90d = end_datetime - timedelta(days=90)
    start_date_30d = start_ts_month_calendar.to_pydatetime()
    start_date_60d = end_datetime - timedelta(days=60) 
    start_date_7d = end_datetime - timedelta(days=7) 
    start_date_today = end_datetime - timedelta(hours=24) 

    ingreso_total = 0.00
    ingreso_porcentaje_cambio = 0.00
    ingreso_indicador = '—'
    ingreso_clase_color = 'text-muted'
    
    productos_top_5_data = []
    productos_stock_critico = [] 
    ultimas_notificaciones = [] 
    
    chart_ventas_json_dia = json.dumps({'labels': [], 'data': [], 'label_chart': 'Ingresos Diarios'})
    chart_ventas_json_semana = json.dumps({'labels': [], 'data': [], 'label_chart': 'Ingresos Semanales'})
    chart_ventas_json_mes = json.dumps({'labels': [], 'data': [], 'label_chart': 'Ingresos Mensuales'})
    chart_turnos_dia_json = json.dumps({'labels': [], 'data': []})
    chart_turnos_data = {'completado': 0.0, 'pendiente': 0.0, 'completados_count': 0, 'total_count': 0}
    
    turnos_pendientes = 0
    turnos_cancelados = 0
    
    try:
        empleado = request.user.empleados 
        cargo_usuario = empleado.cargo.lower()
    except Empleados.DoesNotExist:
        cargo_usuario = 'gerente' 
        
    permisos = {
        'ver_empleados': cargo_usuario == 'gerente',
        'ver_clientes': cargo_usuario == 'gerente',
        'ver_carrusel_imagen': cargo_usuario == 'gerente',

        'ver_stock': cargo_usuario in ['gerente', 'vendedor', 'cajero'],
        'ver_stock_top': cargo_usuario in ['gerente', 'vendedor', 'cajero'], 
        'ver_stock_critico': cargo_usuario in ['gerente', 'vendedor', 'cajero'], 
        'ver_graficos_ventas': cargo_usuario in ['gerente', 'vendedor', 'cajero'],
        
        'ver_graficos_turnos_dias': cargo_usuario in ['gerente', 'peluquero'],
        'ver_graficos_turnos': cargo_usuario in ['gerente', 'peluquero'],
        'ver_turnos_pendientes': cargo_usuario in ['gerente', 'peluquero'],
    }
    
    total_activos = Empleados.objects.filter(activo=True).count()
    total_inactivos = Empleados.objects.filter(activo=False).count()
    total_clientes = Clientes.objects.count()
    productos_criticos_qs = Productos.objects.filter(
        stock_prod__lte=F('stock_minimo'), 
        stock_minimo__isnull=False,
        stock_minimo__gt=0,
        eliminado=False
    ).order_by('stock_prod').values('nombre_prod', 'stock_prod', 'imagen_prod')[:5] 
    stock_bajo_count = productos_criticos_qs.count()
    productos_stock_critico = [ 
        {
            'nombre': p['nombre_prod'], 
            'stock': p['stock_prod'],
            'imagen_url': p['imagen_prod'] 
        } for p in productos_criticos_qs
    ]
    if permisos['ver_graficos_ventas']:
        ventas_queryset_ampliado = DetalleCompras.objects.filter(
            id_compra_dtc__fecha_compra__gte=start_date_90d.date(),
            id_compra_dtc__id_cliente_fk__isnull=False 
        ).select_related('id_compra_dtc', 'id_producto_dtc').annotate(
            datetime_str=Concat(
                Cast('id_compra_dtc__fecha_compra', M.CharField()), 
                M.Value(' '), 
                Cast('id_compra_dtc__hora_compra', M.CharField()), 
                output_field=M.CharField() 
            ),
            monto=F('total_dtc'),
            cantidad=F('id_compra_dtc__cantidad_compra'), 
            producto_nombre=F('id_producto_dtc__nombre_prod'),
            imagen_url=F('id_producto_dtc__imagen_prod')
        ).values('datetime_str', 'monto', 'cantidad', 'producto_nombre', 'imagen_url') 
        
        df_ventas = pd.DataFrame(list(ventas_queryset_ampliado))
        
        if not df_ventas.empty:
            df_ventas['fecha_hora'] = pd.to_datetime(df_ventas['datetime_str']).dt.tz_localize(None) 
            df_ventas['fecha'] = df_ventas['fecha_hora'].dt.date
            start_ts_month = pd.to_datetime(start_date_30d).tz_localize(None) 
            start_ts_60d = pd.to_datetime(start_date_60d).tz_localize(None)
            start_ts_7d = pd.to_datetime(start_date_7d).tz_localize(None)
            start_ts_today = pd.to_datetime(start_date_today).tz_localize(None) 
            start_date_30d_naive = start_ts_month.date() 
            start_date_60d_naive = start_date_60d.date()
            
            ingreso_actual = df_ventas[df_ventas['fecha'] >= start_date_30d_naive]['monto'].sum() or 0
            ingreso_anterior = df_ventas[
                (df_ventas['fecha'] >= start_date_60d_naive) & 
                (df_ventas['fecha'] < start_date_30d_naive)
            ]['monto'].sum() or 0
            
            ingreso_dia = df_ventas[df_ventas['fecha_hora'] >= start_ts_today]['monto'].sum() or 0
            ingreso_semana = df_ventas[df_ventas['fecha_hora'] >= start_ts_7d]['monto'].sum() or 0
            ingreso_mes = float(ingreso_actual) 
            ingreso_total = float(ingreso_actual) 
                        
            if ingreso_anterior > 0:
                ingreso_porcentaje_cambio = ((ingreso_actual - ingreso_anterior) / ingreso_anterior) * 100
                if ingreso_porcentaje_cambio > 0:
                    ingreso_indicador = '↑'; ingreso_clase_color = 'bg-success-subtle text-success'
                elif ingreso_porcentaje_cambio < 0:
                    ingreso_indicador = '↓'; ingreso_clase_color = 'bg-danger-subtle text-danger'
                else:
                    ingreso_indicador = '—'; ingreso_clase_color = 'bg-info-subtle text-info'
            elif ingreso_actual > 0:
                ingreso_indicador = '↑'; ingreso_porcentaje_cambio = 100.00; ingreso_clase_color = 'bg-success-subtle text-success'
            else:
                ingreso_indicador = '—'; ingreso_porcentaje_cambio = 0.00; ingreso_clase_color = 'text-muted'

            chart_ventas_data_dia = format_ventas_chart(df_ventas, start_ts_today, period='H', label_chart='Ingresos Diarios (Últimas 24h, 6h-23h)')
            chart_ventas_json_dia = json.dumps(chart_ventas_data_dia)
            chart_ventas_data_semana = format_ventas_chart(df_ventas, start_ts_7d, period='D', label_chart='Ingresos Semanales (Últimos 7d)')
            chart_ventas_json_semana = json.dumps(chart_ventas_data_semana)
            chart_ventas_data_mes = format_ventas_chart(df_ventas, start_ts_month, period='M', label_chart='Ingresos Mensuales (Mes Calendario)')
            chart_ventas_json_mes = json.dumps(chart_ventas_data_mes)
            
            productos_agrupados = df_ventas[df_ventas['fecha'] >= start_date_30d_naive].groupby(['producto_nombre', 'imagen_url']).agg(
                monto_vendido=('monto', 'sum'), 
                cantidad_vendida=('cantidad', 'sum') 
            ).reset_index()
            
            productos_vendidos = productos_agrupados.sort_values(by='monto_vendido', ascending=False).head(5)
            
            productos_top_5_data = [
                {
                    'nombre': row['producto_nombre'], 
                    'monto': f'{float(row['monto_vendido']):,.2f}', 
                    'unidades': f'{float(row['cantidad_vendida']):,.0f}',
                    'imagen_url': row['imagen_url'] 
                } 
                for index, row in productos_vendidos.iterrows()
            ]

    if permisos['ver_graficos_turnos']:
        turnos_qs = Turnos.objects.filter(
            fecha_turno__gte=start_date_30d_naive,
            fecha_turno__lte=end_date
        )
        completados = turnos_qs.filter(estado_turno='Completado').count()
        total_turnos = turnos_qs.count()
        pendientes_y_otros = turnos_qs.filter(~Q(estado_turno='Completado')).count()

        if total_turnos > 0:
            porcentaje_completado = (completados / total_turnos) * 100
            porcentaje_pendiente = (pendientes_y_otros / total_turnos) * 100
            
            chart_turnos_data = {
                'completado': round(porcentaje_completado, 1),
                'pendiente': round(porcentaje_pendiente, 1),
                'completados_count': completados,
                'total_count': total_turnos
            }
        
        turnos_por_dia = turnos_qs.filter(
            fecha_turno__month=end_date.month, 
            fecha_turno__year=end_date.year
        ).values('fecha_turno').annotate(count=Count('id_turno')).order_by('fecha_turno')
        
        num_days = calendar.monthrange(end_date.year, end_date.month)[1]
        day_labels = [str(d) for d in range(1, num_days + 1)]
        day_counts = {day: 0 for day in range(1, num_days + 1)}
        
        for entry in turnos_por_dia:
            day = entry['fecha_turno'].day
            day_counts[day] = entry['count']
        
        chart_data_dia = [day_counts[day] for day in range(1, num_days + 1)]

        chart_turnos_dia_json = json.dumps({'labels': day_labels, 'data': chart_data_dia})
        
        turnos_pendientes = turnos_qs.filter(
            estado_turno__in=['Pendiente', 'Confirmado']
        ).count()
        
        turnos_cancelados = turnos_qs.filter(
            estado_turno__in=['Cancelado', 'No asistió']
        ).count()
        
        ultimas_notificaciones = [
            {'titulo': f"Turno pendiente", 'mensaje': "Revisar agenda para mañana.", 'fecha': end_datetime - timedelta(minutes=15)}
        ]
    context = {
        'cargo': cargo_usuario,
        'permisos': permisos, 
        'total_ingreso': f'{ingreso_total:,.2f}',
        'ingreso_dia': f'{ingreso_dia:,.2f}',
        'ingreso_semana': f'{ingreso_semana:,.2f}',
        'ingreso_mes': f'{ingreso_mes:,.2f}',
        'ingreso_porcentaje_cambio': f'{ingreso_porcentaje_cambio:.2f}',
        'ingreso_indicador': ingreso_indicador,
        'ingreso_clase_color': ingreso_clase_color,
        'turnos_pendientes': turnos_pendientes,
        'turnos_cancelados': turnos_cancelados,
        'total_clientes': total_clientes,
        'stock_bajo_count': stock_bajo_count,
        'empleados_activos': total_activos,
        'empleados_inactivos': total_inactivos,
        'chart_ventas_json_dia': chart_ventas_json_dia,
        'chart_ventas_json_semana': chart_ventas_json_semana,
        'chart_ventas_json_mes': chart_ventas_json_mes,
        'chart_turnos_dia_json': chart_turnos_dia_json,
        'chart_turnos_data': json.dumps(chart_turnos_data),
        'productos_top_5': productos_top_5_data,
        'productos_stock_critico': productos_stock_critico,
        'ultimas_notificaciones': ultimas_notificaciones,
    }
    
    return render(request, 'dashboard.html', context)

# Carrusel de imágenes
def verificar_permiso_gerente(request):
    try:
        cargo = request.user.empleados.cargo.lower()
        return cargo == 'gerente'
    except Empleados.DoesNotExist:
        return True 

@login_required
def lista_carrusel(request):
    if not verificar_permiso_gerente(request):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return render(request, 'carrusel/acceso_denegado_fragment.html', status=403)
        else:
            return redirect('dashboard:principal')

    imagenes = CarruselImagen.objects.all().order_by('-id')
    context = {'imagenes': imagenes}
    return render(request, 'carrusel/lista_carrusel.html', context)

@login_required
def agregar_carrusel(request):
    if not verificar_permiso_gerente(request):
        return redirect('dashboard:principal')

    if request.method == 'POST':
        form = CarruselImagenForm(request.POST, request.FILES) 
        if form.is_valid():
            form.save()
            return HttpResponse(status=204) 
    else:
        form = CarruselImagenForm()

    context = {'form': form, 'accion': 'Agregar Imagen al Carrusel', 'is_modal_form': True}
    return render(request, 'carrusel/carrusel_form.html', context)

@login_required
def editar_carrusel(request, pk):
    if not verificar_permiso_gerente(request):
        return redirect('dashboard:principal')

    imagen = get_object_or_404(CarruselImagen, pk=pk)
    
    if request.method == 'POST':
        form = CarruselImagenForm(request.POST, request.FILES, instance=imagen) 
        if form.is_valid():
            form.save()
            return HttpResponse(status=204) 
    else:
        form = CarruselImagenForm(instance=imagen)

    context = {'form': form, 'accion': f'Editar Imagen: {imagen.titulo}', 'is_modal_form': True}
    return render(request, 'carrusel/carrusel_form.html', context)

@login_required
def eliminar_carrusel(request, pk):
    if not verificar_permiso_gerente(request):
        return redirect('dashboard:principal')

    imagen = get_object_or_404(CarruselImagen, pk=pk)
    
    if request.method == 'POST':
        imagen.delete()
        return HttpResponse(status=204)
    
    context = {'imagen': imagen, 'accion': f'Eliminar Imagen: {imagen.titulo}', 'is_modal_confirm': True}
    return render(request, 'carrusel/carrusel_confirm_delete.html', context)