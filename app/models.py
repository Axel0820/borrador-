# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.utils import timezone

solo_letras = RegexValidator(r'^[A-Za-z ]+$', 'Solo letras y espacios.')
solo_letras_numeros = RegexValidator(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ0-9 ]+$', 'Solo letras, números, espacios y caracteres especiales.')

class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Cajas(models.Model):
    id_caja = models.AutoField(db_column='Id_caja', primary_key=True)  # Field name made lowercase.
    saldo_inicial = models.DecimalField(db_column='Saldo_inicial', max_digits=12, decimal_places=5)  # Field name made lowercase.
    saldo_anterior = models.DecimalField(db_column='Saldo_anterior', max_digits=12, decimal_places=5)  # Field name made lowercase.
    saldo_actual = models.DecimalField(db_column='Saldo_actual', max_digits=12, decimal_places=5)  # Field name made lowercase.
    saldo_final = models.DecimalField(db_column='Saldo_final', max_digits=12, decimal_places=5)  # Field name made lowercase.
    fecha_apertura = models.DateTimeField(db_column='Fecha_apertura', null=True, blank=True)  # Field name made lowercase.
    fecha_cierre = models.DateTimeField(db_column='Fecha_cierre', null=True, blank=True)  # Field name made lowercase.
    estado_caja = models.IntegerField(db_column='Estado_caja')  # Field name made lowercase.
    id_emp_cj = models.ForeignKey('Empleados', models.DO_NOTHING, db_column='Id_emp_cj')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'cajas'


class Clientes(models.Model):
    id_cliente = models.AutoField(db_column='Id_cliente', primary_key=True)
    nombre_cliente = models.CharField(db_column='Nombre_cliente', max_length=45, validators=[solo_letras])
    apellido_cliente = models.CharField(db_column='Apellido_cliente', max_length=45, validators=[solo_letras])
    correo_clientes = models.EmailField(db_column='Correo_clientes', max_length=100, unique=True)
    telefono_cliente = models.CharField(db_column='Telefono_cliente', max_length=45,  blank=True, null=True)
    dni_cliente = models.CharField(db_column='DNI_cliente', max_length=10, unique=True,  blank=True, null=True)
    direccion_cliente = models.CharField(db_column='Direccion_cliente', max_length=200, blank=True, null=True)
    estado_cliente = models.IntegerField(db_column='Estado_cliente', default=1)
    fecha_registro_cliente = models.DateTimeField(db_column='Fecha_registro_cliente', auto_now_add=True)
    foto = models.ImageField(db_column='Foto', upload_to='fotos_cliente/', blank=True, null=True)
    user = models.OneToOneField( 
        User, 
        on_delete=models.CASCADE, 
        related_name='cliente_perfil'
    )

    class Meta:
        db_table = 'clientes'
        
    def __str__(self):
        return f"{self.nombre_cliente} {self.apellido_cliente}"


class Compras(models.Model):
    # Choices para método de pago
    METODOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('tarjeta', 'Tarjeta'),
    ]
    
    id_compra = models.AutoField(db_column='Id_compra', primary_key=True)  # Field name made lowercase.
    nombre_compra = models.CharField(db_column='Nombre_compra', max_length=455)  # Field name made lowercase.
    cantidad_compra = models.IntegerField(db_column='Cantidad_compra')  # Field name made lowercase.
    fecha_compra = models.DateField(db_column='Fecha_compra')  # Field name made lowercase.
    hora_compra = models.TimeField(db_column='Hora_compra', auto_now_add=True, verbose_name='Hora de Compra')
    precio_compra = models.DecimalField(db_column='Precio_compra', max_digits=12, decimal_places=5)  # Field name made lowercase.
    descripcion_compra = models.CharField(db_column='Descripcion_compra', max_length=455)  # Field name made lowercase.
    id_empleado_fk = models.ForeignKey('Empleados', models.DO_NOTHING, db_column='Id_empleado_fk')  # Field name made lowercase.
    id_caja_fk = models.ForeignKey(Cajas, models.DO_NOTHING, db_column='Id_caja_fk')  # Field name made lowercase.
    id_cliente_fk = models.ForeignKey(Clientes, models.DO_NOTHING, db_column='Id_cliente_fk')  # Field name made lowercase.
    estado_compra = models.IntegerField(db_column='Estado_compra', blank=True, null=True)  # Field name made lowercase.
    
    # Nuevo campo para método de pago
    metodo_pago = models.CharField(
        db_column='Metodo_pago',
        max_length=20,
        choices=METODOS_PAGO,
        default='efectivo',
        verbose_name='Método de Pago'
    )

    class Meta:
        managed = True
        db_table = 'compras'

class DetalleCompras(models.Model):
    id_detalle_compra = models.AutoField(db_column='Id_detalle_compra', primary_key=True)  # Field name made lowercase.
    precio_unitario_dtc = models.DecimalField(db_column='Precio_unitario_dtc', max_digits=12, decimal_places=5)  # Field name made lowercase.
    subtotal_dtc = models.DecimalField(db_column='Subtotal_dtc', max_digits=12, decimal_places=5)  # Field name made lowercase.
    descuento_dtc = models.DecimalField(db_column='Descuento_dtc', max_digits=12, decimal_places=5)  # Field name made lowercase.
    total_dtc = models.DecimalField(db_column='Total_dtc', max_digits=12, decimal_places=5)  # Field name made lowercase.
    fecha_entrega_dtc = models.DateField(db_column='Fecha_entrega_dtc')  # Field name made lowercase.
    descripcion_dtc = models.CharField(db_column='Descripcion_dtc', max_length=445, blank=True, null=True)  # Field name made lowercase.
    estado_dtc = models.IntegerField(db_column='Estado_dtc')  # Field name made lowercase.
    id_compra_dtc = models.ForeignKey(Compras, models.DO_NOTHING, db_column='Id_compra_dtc')  # Field name made lowercase.
    id_producto_dtc = models.ForeignKey('Productos', models.DO_NOTHING, db_column='Id_producto_dtc')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'detalle_compras'


class DetalleSolicOc(models.Model):
    id_detalle_solic_oc = models.AutoField(db_column='Id_detalle_solic_OC', primary_key=True)  # Field name made lowercase.
    cantidad_producto_oc = models.IntegerField(db_column='Cantidad_producto_OC')  # Field name made lowercase.
    precio_unitario_oc = models.DecimalField(db_column='Precio_unitario_OC', max_digits=12, decimal_places=5)  # Field name made lowercase.
    sub_total_oc = models.DecimalField(db_column='Sub_total_OC', max_digits=12, decimal_places=5)  # Field name made lowercase.
    fecha_oc = models.DateField(db_column='Fecha_OC')  # Field name made lowercase.
    decripcion_oc = models.CharField(db_column='Decripcion_OC', max_length=455)  # Field name made lowercase.
    estado_oc = models.IntegerField(db_column='Estado_OC')  # Field name made lowercase.
    id_solicitud_oc = models.ForeignKey('SolicitudOrdenCompras', models.DO_NOTHING, db_column='Id_solicitud_OC')  # Field name made lowercase.
    id_provxprod_oc = models.ForeignKey('Provxprod', models.DO_NOTHING, db_column='Id_provXprod_OC')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'detalle_solic_oc'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class EmpRoles(models.Model):
    id_rol_emp = models.AutoField(db_column='Id_rol_emp', primary_key=True)  # Field name made lowercase.
    id_rol_emp_emp = models.ForeignKey('Empleados', models.DO_NOTHING, db_column='Id_rol_emp_emp')  # Field name made lowercase.
    id_rol_emp_rol = models.ForeignKey('Roles', models.DO_NOTHING, db_column='Id_rol_emp_rol')  # Field name made lowercase.
    estado_emp_rol = models.IntegerField(db_column='Estado_emp_rol', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'emp_roles'


class Empleados(models.Model):
    id_emp = models.AutoField(db_column='Id_emp', primary_key=True)
    sexo_emp = models.CharField(db_column='Sexo_emp', max_length=10, blank=True, null=True)
    nombre_emp = models.CharField(db_column='Nombre_emp', max_length=20, validators=[solo_letras])
    apellido_emp = models.CharField(db_column='Apellido_emp', max_length=20, validators=[solo_letras])
    dni_emp = models.CharField(db_column='DNI_emp', max_length=8, unique=True)
    direccion = models.CharField(db_column='Direccion', max_length=150, blank=True, null=True)
    telefono = models.CharField(db_column='Telefono_emp', max_length=11, blank=True, null=True)
    email = models.EmailField(db_column='Email_emp', max_length=254, blank=True, null=True)
    cargo = models.CharField(db_column='Cargo', max_length=50, default='sin cargo')
    fecha_ingreso = models.DateField(db_column='Fecha_ingreso', blank=True, null=True)
    sueldo = models.DecimalField(db_column='Sueldo', max_digits=10, decimal_places=2, blank=True, null=True)
    foto = models.ImageField(db_column='Foto', upload_to='fotos_empleados/', blank=True, null=True)
    activo = models.BooleanField(db_column='Activo', default=True)
    
    # Relación con auth_user (según tu DER) - TU MODIFICACIÓN
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    
    # Campo para controlar cambio obligatorio de contraseña - TU MODIFICACIÓN
    force_password_change = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = 'Empleados'

    def __str__(self):
        return f"{self.nombre_emp} {self.apellido_emp} ({self.cargo})"

class Mascotas(models.Model):
    id_mascotas = models.AutoField(db_column='Id_mascotas', primary_key=True)  # Field name made lowercase.
    estado_mascota = models.IntegerField(db_column='Estado_mascota', blank=True, null=True)  # Field name made lowercase.
    id_cliente_masc = models.ForeignKey(Clientes, models.DO_NOTHING, db_column='Id_cliente_masc')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'mascotas'


class OrdenCompras(models.Model):
    id_orden_compra = models.AutoField(db_column='Id_orden_compra', primary_key=True)  # Field name made lowercase.
    fecha_emision_orden = models.DateField(db_column='Fecha_emision_orden')  # Field name made lowercase.
    total_orden = models.DecimalField(db_column='Total_orden', max_digits=12, decimal_places=5)  # Field name made lowercase.
    estado_orden = models.IntegerField(db_column='Estado_orden')  # Field name made lowercase.
    id_solicitud_orc = models.ForeignKey('SolicitudOrdenCompras', models.DO_NOTHING, db_column='Id_solicitud_orc')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'orden_compras'


class PrecioServicios(models.Model):
    id_precio_servicio = models.AutoField(db_column='Id_precio_servicio', primary_key=True)  # Field name made lowercase.
    id_servicio_preser = models.ForeignKey('Servicios', models.DO_NOTHING, db_column='Id_servicio_preser')  # Field name made lowercase.
    precio_unitario_preser = models.DecimalField(db_column='Precio_unitario_preser', max_digits=12, decimal_places=5)  # Field name made lowercase.
    precio_completo_preser = models.DecimalField(db_column='Precio_completo_preser', max_digits=12, decimal_places=5)  # Field name made lowercase.
    descripcion_precio_servicio = models.CharField(db_column='Descripcion_precio_servicio', max_length=455, blank=True, null=True)  # Field name made lowercase.
    estado_precio_servicio = models.IntegerField(db_column='Estado_precio_servicio', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'precio_servicios'


class Productos(models.Model):
    id_prod = models.AutoField(db_column='Id_prod', primary_key=True)  # Field name made lowercase.
    nombre_prod = models.CharField(db_column='Nombre_prod', max_length=45, validators=[solo_letras_numeros])  # Field name made lowercase.
    stock_prod = models.IntegerField(db_column='Stock_prod')  # Field name made lowercase.
    stock_minimo = models.IntegerField(db_column='Stock_minimo', default=10, help_text='Cantidad mínima de stock antes de mostrar alerta')  # Field name made lowercase.
    precio_prod = models.DecimalField(db_column='Precio_prod', max_digits=12, decimal_places=5)  # Field name made lowercase.
    #unidad_media_prod = models.CharField(db_column='Unidad_media_prod', max_length=45)  # Field name made lowercase.
    categoria_prod = models.CharField(db_column='Categoria_prod', max_length=45)  # Field name made lowercase.
    estado_prod = models.IntegerField(db_column='Estado_prod', blank=True, null=True)  # Field name made lowercase.
    imagen_prod = models.ImageField(upload_to="productos/", blank=True, null=True)# agrego nuevo campo para poder guradar imagenes
    # Nueva foreign key a unidades
    unidad = models.ForeignKey('Unidades', on_delete=models.PROTECT, db_column='Id_unidad', null=True, blank=True)
    cantidad_unidad = models.DecimalField(db_column='Cantidad_unidad', max_digits=8, decimal_places=2, null=True, blank=True)
    proveedor_prod = models.CharField(db_column='Proveedor_prod', max_length=100, blank=True, null=True)
    # Campo para eliminación lógica--------------
    eliminado = models.BooleanField(default=False, verbose_name='Eliminado')

    class Meta:
        managed = True
        db_table = 'productos'

    def get_unidad_completa(self):
        """Retorna la representación completa de la unidad con cantidad"""
        if self.unidad and self.cantidad_unidad:
            
            cantidad_str = str(self.cantidad_unidad).rstrip('0').rstrip('.')
            return f"{cantidad_str} {self.unidad.simbolo} - {self.unidad.tipo_empaque}"
        elif self.unidad:
            return f"{self.unidad.simbolo} - {self.unidad.tipo_empaque}"
        else:
            return "Sin unidad"

class Proveedoress(models.Model):
    id_prov = models.AutoField(db_column='Id_prov', primary_key=True)
    nombre_prov = models.CharField(db_column='Nombre_prov', max_length=45)
    correo_prov = models.CharField(db_column='Correo_prov', max_length=45)
    cuit_prov = models.CharField(db_column='CUIT_prov', max_length=13)
    telefono_prov = models.CharField(db_column='Telefono_prov', max_length=20)
    descripcion_prov = models.CharField(db_column='Descripcion_prov', max_length=455)
    estado_prov = models.IntegerField(db_column='Estado_prov', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'proveedoress'
        ordering = ['nombre_prov']
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
    
    def __str__(self):
        return f"{self.nombre_prov} - {self.cuit_prov}"


class Provxprod(models.Model):
    id_provxprod = models.AutoField(db_column='Id_provXprod', primary_key=True)  # Field name made lowercase.
    id_prov_fk = models.ForeignKey(Proveedoress, models.DO_NOTHING, db_column='Id_prov_fk')  # Field name made lowercase.
    id_prod_fk = models.ForeignKey(Productos, models.DO_NOTHING, db_column='Id_prod_fk')  # Field name made lowercase.
    estado_provxprod = models.IntegerField(db_column='Estado_provXprod', blank=True, null=True)  # Field name made lowercase.
    nombre_prov = models.CharField(db_column='Nombre_prov', max_length=455)  # Field name made lowercase.
    nombre_prod = models.CharField(db_column='Nombre_prod', max_length=455)  # Field name made lowercase.
    fecha_entrega_provxprod = models.DateField(db_column='Fecha_entrega_provXprod')  # Field name made lowercase.
    descripcion_provxprod = models.CharField(db_column='Descripcion_provXprod', max_length=455)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'provxprod'


class Roles(models.Model):
    id_rol = models.AutoField(db_column='Id_rol', primary_key=True)  # Field name made lowercase.
    nombre_rol = models.CharField(db_column='Nombre_rol', max_length=95)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'roles'


class Servicios(models.Model):
    id_servicio = models.AutoField(db_column='Id_servicio', primary_key=True)
    nombre_servicio = models.CharField(db_column='Nombre_servicio', max_length=100)
    tipo_de_servicio = models.CharField(db_column='Tipo_de_servicio', max_length=50, default='Estética')
    descripcion = models.TextField(db_column='Descripcion', blank=True, null=True)
    estado = models.CharField(db_column='Estado', max_length=20, default='Activo', choices=[
        ('Activo', 'Activo'),
        ('Inactivo', 'Inactivo'),
    ])

    class Meta:
        managed = True
        db_table = 'servicios'

    def __str__(self):
        return self.nombre


class ServiciosPrestados(models.Model):
    id_serv_prestados = models.AutoField(db_column='Id_serv_prestados', primary_key=True)
    id_turnos = models.ForeignKey('Turnos', on_delete=models.CASCADE, db_column='Id_turno', null=True, blank=True)
    id_servicio = models.ForeignKey(Servicios, on_delete=models.CASCADE, db_column='Id_servicio', null=True, blank=True)
    id_empleados = models.ForeignKey(Empleados, on_delete=models.CASCADE, db_column='Id_empleados', null=True, blank=True)
    monto_serv = models.DecimalField(db_column='Monto_serv', max_digits=10, decimal_places=2, null=True, blank=True)
    estado = models.CharField(db_column='Estado', max_length=20, default='Pendiente de pago', choices=[
        ('Pendiente de pago', 'Pendiente de pago'),
        ('Pagado', 'Pagado'),
        ('Cancelado', 'Cancelado'),
    ], null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'servicios_prestados'

    def __str__(self):
        return f"Servicio {self.id_servicios.nombre if self.id_servicios else 'Sin servicio'} en turno {self.id_turnos.id_turno if self.id_turnos else 'Sin turno'}"


class SolicitudOrdenCompras(models.Model):
    id_solicitud_orden_compra = models.AutoField(db_column='Id_solicitud_orden_compra', primary_key=True)  # Field name made lowercase.
    fecha_solicitud_orc = models.DateField(db_column='Fecha_solicitud_orc')  # Field name made lowercase.
    descripcion_orc = models.CharField(db_column='Descripcion_orc', max_length=455)  # Field name made lowercase.
    estado_orc = models.IntegerField(db_column='Estado_orc')  # Field name made lowercase.
    id_empleado_orc = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='Id_empleado_orc', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'solicitud_orden_compras'


class Stocks(models.Model):
    id_stock = models.AutoField(db_column='Id_stock', primary_key=True)  # Field name made lowercase.
    cantidad_stock = models.IntegerField(db_column='Cantidad_stock')  # Field name made lowercase.
    fecha_egreso_stock = models.DateTimeField(db_column='Fecha_egreso_stock')  # Field name made lowercase.
    fecha_vencimiento_stock = models.DateTimeField(db_column='Fecha_vencimiento_stock')  # Field name made lowercase.
    id_prod_stock = models.ForeignKey(Productos, models.DO_NOTHING, db_column='Id_prod_stock')  # Field name made lowercase.
    estado_stock = models.IntegerField(db_column='Estado_stock')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'stocks'


class Turnos(models.Model):
    id_turno = models.AutoField(db_column='Id_turno', primary_key=True)  # Field name made lowercase.
    fecha_turno = models.DateField(db_column='Fecha_turno')  # Field name made lowercase.
    hora_turno = models.TimeField(db_column='Hora_turno')  # Field name made lowercase.
    motivo_cance_turno = models.CharField(db_column='Motivo_cance_turno', max_length=200, blank=True, null=True)  # Field name made lowercase.
    estado_turno = models.CharField(db_column='Estado_turno', max_length=20, choices=[
        ('Pendiente', 'Pendiente'),
        ('Confirmado', 'Confirmado'),
        ('En curso', 'En curso'),
        ('Completado', 'Completado'),
        ('Cancelado', 'Cancelado'),
        ('No asistió', 'No asistió'),
    ], default='Pendiente')  
    nombre = models.CharField(db_column='Nombre', max_length=50, default='Sin nombre')  # Field name made lowercase.
    tipo_turno = models.CharField(db_column='Tipo_turno', max_length=20, default='Perro')  # Field name made lowercase.
    tamaño_turno = models.CharField(db_column='Tamaño_turno', max_length=20, default='Mediano')  # Field name made lowercase.
    genero = models.CharField(db_column='Genero', max_length=10, default='Macho')  # Field name made lowercase.
    edad_turno = models.IntegerField(db_column='Edad_turno', blank=True, null=True)  # Field name made lowercase.
    observaciones_turno = models.TextField(db_column='Observaciones_turno', blank=True, null=True)  # Field name made lowercase.
    id_cliente = models.ForeignKey(Clientes, models.DO_NOTHING, db_column='Id_cliente', default=1)  # Field name made lowercase.
    servicios = models.ManyToManyField(Servicios, through='ServiciosPrestados', blank=True)

    class Meta:
        managed = True
        # Evita que un mismo cliente cree varios turnos para la misma fecha y hora
        unique_together = (('id_cliente', 'fecha_turno', 'hora_turno'),)
        db_table = 'turnos'

class Unidades(models.Model):
    id_unidad = models.AutoField(db_column='Id_unidad', primary_key=True)
    unidad_medida = models.CharField(db_column='Unidad_medida', max_length=20, choices=[
        ('litros', 'Litros'),
        ('gramos', 'Gramos'),
        ('kilogramos', 'Kilogramos'),
        ('piezas', 'Piezas'),
    ])
    simbolo = models.CharField(db_column='Simbolo', max_length=5, choices=[
        ('L', 'L'),
        ('g', 'g'),
        ('kg', 'kg'),
        ('pz', 'pz'),
    ])
    tipo_empaque = models.CharField(db_column='Tipo_empaque', max_length=30, choices=[
        ('botella', 'Botella'),
        ('sachet', 'Sachet'),
        ('bolsa', 'Bolsa'),
        ('sobre', 'Sobre'),
        ('lata', 'Lata'),
        ('caja', 'Caja'),
        ('pieza', 'Pieza'),
    ])

    class Meta:
        managed = True
        db_table = 'unidades'

    def __str__(self):
        return f"{self.unidad_medida} ({self.simbolo}) - {self.tipo_empaque}"

    def get_display_format(self):
        """Retorna el formato de visualización para mostrar en tablas y formularios"""
        return f"{self.simbolo} - {self.tipo_empaque}"
    

class CarruselImagen(models.Model):
    titulo = models.CharField(max_length=100, blank=True, null=True, help_text="Título o descripción breve de la imagen.")
    imagen = models.ImageField(upload_to='carrusel/', help_text="Sube la imagen para el carrusel.")
    orden = models.PositiveIntegerField(default=0, help_text="Número para definir el orden de visualización. Menor número va primero.")
    activo = models.BooleanField(default=True, help_text="Si está activo, se mostrará en el carrusel.")
    fecha_subida = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['orden', '-fecha_subida']
        verbose_name = "Imagen del Carrusel"
        verbose_name_plural = "Imágenes del Carrusel"
        managed = True
        db_table = 'carrusel_imagen'

    def __str__(self):
        return self.titulo or f"Imagen Carrusel ID: {self.id}"
    

class MovimientosCaja(models.Model):
    """
    Registro unificado de todos los movimientos de dinero en caja.
    Incluye ventas automáticas y movimientos manuales.
    """
    TIPOS_MOVIMIENTO = [
        ('ingreso', 'Ingreso'),
        ('egreso', 'Egreso'),
    ]
    
    CATEGORIAS_MOVIMIENTO = [
        ('venta', 'Venta'),
        ('servicios', 'Pago Servicios'),
        ('otros_ingresos', 'Otros Ingresos'),
        ('otros_egresos', 'Otros Egresos'),
    ]
    
    id_movimiento = models.AutoField(primary_key=True)
    tipo_movimiento = models.CharField(max_length=10, choices=TIPOS_MOVIMIENTO)
    categoria = models.CharField(max_length=30, choices=CATEGORIAS_MOVIMIENTO, default='otros_ingresos')
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    descripcion = models.CharField(max_length=255)
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    
    # Relaciones con modelos existentes
    id_caja_fk = models.ForeignKey('Cajas', on_delete=models.CASCADE, db_column='Id_caja')
    id_empleado_fk = models.ForeignKey('Empleados', on_delete=models.CASCADE, db_column='Id_empleado')
    id_compra_fk = models.ForeignKey('Compras', on_delete=models.CASCADE, null=True, blank=True, db_column='Id_compra')
    
    # Control
    es_automatico = models.BooleanField(default=False)
    estado = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True, null=True)
    
    class Meta:
        managed = True
        db_table = 'movimientos_caja'
        ordering = ['-fecha_movimiento']
    
    def __str__(self):
        signo = '+' if self.tipo_movimiento == 'ingreso' else '-'
        return f"{signo}${self.monto} - {self.descripcion}"
