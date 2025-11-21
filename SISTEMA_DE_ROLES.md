# 🔐 Sistema de Roles - Alma Canina

## 📋 Grupos del Sistema

### 1. **Cliente**
- **Acceso**: Solo catálogo público (vista de productos)
- **Flujo de registro**: Automático al registrarse en el sistema
- **Login**: Redirige a `index` (catálogo)
- **Restricciones**: NO puede acceder a `/adm2/` ni módulos administrativos

### 2. **Peluquero**
- **Acceso**: Solo Turnos
- **Creación**: Por el Gerente al crear empleado con cargo "Peluquero"
- **Login**: Redirige a `/` (index) → Botón "Administración" visible → `/adm2/`
- **Módulos visibles**:
  - ✅ Turnos (futuro)
  - ✅ Perfil
- **Restricciones**: NO puede ver Caja, Empleados, Inventario, Proveedores, Clientes

### 3. **Vendedor**
- **Acceso**: Solo Caja
- **Creación**: Por el Gerente al crear empleado con cargo "Vendedor"
- **Login**: Redirige a `/` (index) → Botón "Administración" visible → `/adm2/`
- **Módulos visibles**:
  - ✅ Caja
  - ✅ Perfil
- **Restricciones**: NO puede ver Empleados, Inventario, Proveedores, Clientes, Turnos

### 4. **Cajero**
- **Acceso**: Solo Caja
- **Creación**: Por el Gerente al crear empleado con cargo "Cajero"
- **Login**: Redirige a `/` (index) → Botón "Administración" visible → `/adm2/`
- **Módulos visibles**:
  - ✅ Caja
  - ✅ Perfil
- **Restricciones**: NO puede ver Empleados, Inventario, Proveedores, Clientes, Turnos

### 5. **Gerente**
- **Acceso**: TOTAL - Todos los módulos
- **Creación**: Por el Gerente al crear empleado con cargo "Gerente"
- **Login**: Redirige **directamente** a `/adm2/` (sin pasar por index)
- **Módulos visibles**:
  - ✅ Caja
  - ✅ Turnos
  - ✅ Empleados (CRUD completo)
  - ✅ Inventario (CRUD completo)
  - ✅ Proveedores (CRUD completo)
  - ✅ Clientes (CRUD completo)
  - ✅ Perfil

## 📊 Matriz de Permisos

| Módulo           | Cliente | Peluquero | Vendedor | Cajero | Gerente | Superadmin |
|------------------|---------|-----------|----------|--------|---------|------------|
| Caja             | ❌      | ❌        | ✅       | ✅     | ✅      | ✅         |
| Turnos Admin     | ❌      | ✅        | ❌       | ❌     | ✅      | ✅         |
| Turnos Cliente   | ✅      | ✅        | ✅       | ✅     | ✅      | ✅         |
| Empleados        | ❌      | ❌        | ❌       | ❌     | ✅      | ✅         |
| Inventario       | ❌      | ❌        | ❌       | ❌     | ✅      | ✅         |
| Proveedores      | ❌      | ❌        | ❌       | ❌     | ✅      | ✅         |
| Clientes         | ❌      | ❌        | ❌       | ❌     | ✅      | ✅         |
| Catálogo         | ✅      | ✅        | ✅       | ✅     | ✅      | ✅         |

## 🔄 Flujo de Creación de Empleados

### Paso 1: Gerente crea empleado
1. Login como Gerente o Superusuario
2. Ir a **Empleados** → **Crear Empleado**
3. Llenar formulario:
   - Nombre, Apellido, DNI
   - Email (opcional pero recomendado)
   - **Cargo**: Seleccionar uno (Peluquero, Cajero, Vendedor, Gerente)
   - Otros datos (teléfono, dirección, sueldo, etc.)
4. Guardar

### Paso 2: Sistema genera credenciales automáticamente
El sistema crea automáticamente:
- **Usuario**: `nombre.apellido` (normalizado sin acentos)
- **Contraseña temporal**: Según el cargo
  - Peluquero: `Peluquero123!`
  - Cajero: `Cajero123!`
  - Vendedor: `Vendedor123!`
  - Gerente: `Gerente123!`
- **Grupo**: Asigna automáticamente según cargo
- **Email**: Si se proporcionó email, envía credenciales por correo

### Paso 3: Empleado hace primer login
1. Ir a `/accounts/login/`
2. Ingresar usuario y contraseña temporal
3. El sistema **obliga** a cambiar la contraseña
4. Después del cambio, redirige a su vista según rol

## 🛡️ Implementación Técnica

### Decoradores Disponibles

**Archivo**: `app/decorators.py`

```python
@solo_gerente           # Solo Gerente y Superusuario
@solo_peluquero         # Peluquero y Gerente
@solo_cajero_vendedor   # Cajero, Vendedor y Gerente
@acceso_caja            # Todos los empleados (no clientes)
@acceso_empleados       # Todos los empleados (no clientes)
@solo_cliente           # Solo clientes
```

### Uso en Vistas

```python
from app.decorators import solo_gerente, acceso_caja

@login_required
@solo_gerente
def listar_empleados(request):
    """Solo Gerente puede listar empleados"""
    empleados = Empleados.objects.all()
    return render(request, 'empleados/listar.html', {'empleados': empleados})

@login_required
@acceso_caja
def caja_principal(request):
    """Todos los empleados tienen acceso a caja"""
    return render(request, 'caja/caja_ajax.html')
```

### Protección Actual de Vistas

**Empleados** (Solo Gerente - `@solo_gerente`):
- `listar_empleados`
- `crear_empleado`
- `editar_empleado`
- `eliminar_empleado`
- `detalle_empleado`
- `exportar_empleados_pdf`
- `exportar_empleado_pdf`

**Inventario** (Solo Gerente - `@solo_gerente`):
- `listar_productos`
- `registrar_producto`
- `editar_producto`
- `eliminar_producto`
- `exportar_productos_pdf`

**Proveedores** (Solo Gerente - `@solo_gerente`):
- `listar_proveedores`
- `crear_proveedor`
- `editar_proveedor`
- `eliminar_proveedor`
- `exportar_proveedores_pdf`
- `ver_proveedor`
- `buscar_proveedor`

**Clientes** (Solo Gerente - `@solo_gerente`):
- `listar_clientes`
- `crear_cliente`
- `editar_cliente`
- `eliminar_cliente`
- `exportar_clientes_pdf`
- `ver_cliente`
- `buscar_cliente`

**Caja** (Gerente, Cajero, Vendedor - `@acceso_caja`):
- `caja_principal`
- `apertura_caja`
- `crear_venta`

**Turnos Admin** (Peluquero, Gerente - `@solo_peluquero`):
- `turnosadm`

**Turnos Cliente** (Todos autenticados - `@login_required`):
- `turnos`

**Panel Administrativo** (Todos empleados - `@acceso_empleados`):
- `adm2` - Solo empleados (no clientes)

## 🔒 Redirecciones por Rol

### Después del Login (`login/views.py`):
- **Superusuario** → `/adm2/` (directo)
- **Gerente** → `/adm2/` (directo)
- **Peluquero/Cajero/Vendedor** → `/` (index) → Ve botón "Administración" → `/adm2/`
- **Cliente** → `/` (index) → NO ve botón "Administración"
- **Usuario sin grupo** → `/` (index)

### Después de Cambiar Contraseña (`profiles/views.py`):
- **Superusuario/Gerente** → `/adm2/` (directo)
- **Peluquero/Cajero/Vendedor** → `/` (index)
- **Cliente** → `/` (index)
- Marca `force_password_change = False` en el empleado

### Si Intenta Acceder Sin Permisos:
- **Cliente intenta acceso administrativo** → Redirige a `/` (index)
- **Empleado sin permisos** → Redirige a `/adm2/` (su panel)
- **Gerente** → Acceso total sin restricciones

## 📝 Verificación de Rol en Templates

En `adm2.html` y otros templates:

```django
{# Verificar si es Gerente #}
{% if request.user.is_superuser %}
    <li><a href="{% url 'empleados:listar' %}">Empleados</a></li>
{% else %}
    {% for group in request.user.groups.all %}
        {% if group.name == "Gerente" %}
            <li><a href="{% url 'empleados:listar' %}">Empleados</a></li>
        {% endif %}
    {% endfor %}
{% endif %}

{# Verificar si es Peluquero #}
{% for group in request.user.groups.all %}
    {% if group.name == "Peluquero" or group.name == "Gerente" %}
        <li><a href="#">Turnos</a></li>
    {% endif %}
{% endfor %}

{# Caja visible para todos los empleados #}
<li><a href="{% url 'caja_principal' %}">Caja</a></li>
```

## 🧪 Pruebas

### 1. Crear los Grupos (Primera Vez)
```bash
python manage.py create_employee_groups
```

Salida esperada:
```
✓ Grupo "Cliente" creado exitosamente
✓ Grupo "Peluquero" creado exitosamente
✓ Grupo "Cajero" creado exitosamente
✓ Grupo "Vendedor" creado exitosamente
✓ Grupo "Gerente" creado exitosamente

✓ Sistema de grupos configurado correctamente
```

### 2. Crear Empleado de Prueba (Como Gerente)
1. Login como superusuario o gerente
2. Ir a Empleados → Crear
3. Llenar datos:
   - Nombre: Juan
   - Apellido: Perez
   - DNI: 12345678
   - Email: juan@test.com
   - **Cargo: Cajero**
4. Guardar
5. Anotar credenciales generadas

### 3. Probar Login como Cajero
1. Logout del gerente
2. Login con credenciales del cajero
3. **Verificar**:
   - ✅ Solicita cambio de contraseña
   - ✅ Después del cambio, redirige a `/` (index)
   - ✅ Ve botón "Administración" en el navbar
   - ✅ Click en "Administración" → Va a `/adm2/`
   - ✅ En `/adm2/` solo ve módulo "Caja"
   - ❌ NO ve: Empleados, Inventario, Proveedores, Clientes

### 4. Probar Flujo de Peluquero
1. Crear empleado con cargo "Peluquero"
2. Login con credenciales
3. **Verificar**:
   - ✅ Redirige a `/` (index)
   - ✅ Ve botón "Administración"
   - ✅ En `/adm2/` ve: Caja + Turnos
   - ❌ NO ve otros módulos

### 5. Probar Login como Gerente
1. Login como Gerente
2. **Verificar**:
   - ✅ Redirige **directamente** a `/adm2/` (sin pasar por index)
   - ✅ Ve todos los módulos
   - ✅ Acceso total

### 6. Intentar Acceso Directo (Burlar Restricciones)
Como Cajero, escribir en navegador:
- `http://127.0.0.1:8000/empleados/` → ✅ Debe redirigir a `/adm2/`
- `http://127.0.0.1:8000/productos/` → ✅ Debe redirigir a `/adm2/`

### 7. Probar Flujo de Cliente
1. Ir a `/accounts/register/`
2. Crear cuenta nueva
3. Login
4. **Verificar**:
   - ✅ Redirige a `/` (index - catálogo)
   - ❌ NO ve botón "Administración"
   - ✅ Ve botón "Mi Perfil"
   - ❌ NO puede acceder a `/adm2/`

## 🐛 Solución de Problemas

### Error: "Usuario no tiene acceso"
**Causa**: Usuario no tiene grupo asignado

**Solución**:
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import User, Group
user = User.objects.get(username='juan.perez')
print(user.groups.all())  # Verificar grupos

# Asignar grupo manualmente si es necesario
grupo = Group.objects.get(name='Cajero')
user.groups.add(grupo)
```

### Error: "No se crearon los grupos"
**Solución**:
```bash
python manage.py create_employee_groups
```

### Empleado puede acceder a módulos restringidos
**Verificar**:
1. Que la vista tenga el decorador correcto
2. Que el template verifique el grupo correctamente
3. Que el usuario tenga el grupo correcto asignado

## 📚 Archivos Modificados

1. **`app/decorators.py`** - Decoradores de control de acceso ✅
2. **`empleados/management/commands/create_employee_groups.py`** - Comando para crear grupos ✅
3. **`empleados/forms.py`** - Asignación automática de grupos ✅
4. **`login/views.py`** - Redirecciones según rol ✅
5. **`profiles/views.py`** - Cambio de contraseña y redirecciones ✅
6. **`app/templates/vadmin/adm2.html`** - Menú dinámico según rol ✅
7. **`app/views.py`** - Vistas protegidas con decoradores ✅
8. **`empleados/views.py`** - Todas las vistas protegidas ✅
9. **`caja/views.py`** - Vista caja protegida ✅

## � Experiencia de Usuario por Rol

### Para Gerente:
```
[Login] → /adm2/ (directo)
         ↓
   Panel Admin completo
   - Acceso total
   - Ve todos los módulos
   - Sin restricciones
```

### Para Cajero/Vendedor/Peluquero:
```
[Login] → / (index - catálogo)
         ↓
   Ve botón "Administración" en navbar
         ↓
   Click en "Administración"
         ↓
   /adm2/ (panel limitado)
         ↓
   Solo ve sus módulos permitidos:
   - Peluquero: Caja + Turnos
   - Cajero: Caja
   - Vendedor: Caja
```

### Para Cliente:
```
[Login] → / (index - catálogo)
         ↓
   NO ve botón "Administración"
   Ve botón "Mi Perfil"
         ↓
   Solo puede navegar:
   - Catálogo de productos
   - Su perfil
   - Carrito de compras
```

## 🎯 Próximos Pasos

- [x] Implementar módulo de Turnos
- [x] Proteger vistas de Proveedores y Clientes con `@solo_gerente`
- [x] Proteger Turnos Admin con `@solo_peluquero`
- [x] Proteger Turnos Cliente con `@login_required`
- [ ] Agregar tests automatizados para cada rol
- [ ] Dashboard personalizado según rol
- [ ] Logs de acceso por usuario

## 📞 Soporte

Si tienes problemas con el sistema de roles:
1. Verificar que los grupos existen: `python manage.py create_employee_groups`
2. Verificar que el usuario tiene grupo asignado
3. Verificar que la vista tiene el decorador correcto
4. Revisar los logs de Django para errores específicos

---

**Última actualización**: 22 de octubre de 2025
**Versión**: 1.1

##  Sistema de Turnos

El sistema de turnos tiene **DOS interfaces** independientes:

### 1. **Turnos Cliente** (/turnoscli/turnos)
- **URL**: /turnoscli/turnos
- **Vista**: `app.views.turnos`
- **Template**: `app/templates/turnoscli/turnos.html`
- **JavaScript**: `static/js/turnos/turnosCli.js`
- **Protección**: `@login_required` (todos los usuarios autenticados)
- **Acceso**: Cliente, Peluquero, Cajero, Vendedor, Gerente, Superusuario
- **Descripción**: Interface para que los clientes puedan:
  - Ver turnos disponibles
  - Reservar turnos de peluquería
  - Ver historial de turnos propios
  - Cancelar turnos futuros
- **Navegación**: Visible en navbar público (`index.html`) con enlace "Turnos"

### 2. **Turnos Admin** (/turnosadm/)
- **URL**: `/turnosadm/`
- **Vista**: `app.views.turnosadm`
- **Template**: `app/templates/turnosAdm/turnoadm.html`
- **JavaScript**: `static/js/turnos/turnosAdm.js`
- **Protección**: `@login_required @solo_peluquero`
- **Acceso**: Peluquero, Gerente, Superusuario
- **Descripción**: Panel administrativo para que peluqueros gestionen:
  - Ver todos los turnos del día/semana/mes
  - Confirmar/rechazar turnos
  - Marcar turnos como completados
  - Gestionar horarios disponibles
  - Ver estadísticas de turnos
- **Navegación**: Visible en menú de `/adm2/` solo para Peluquero y Gerente

### Flujo de Uso

**Cliente**:
1. Login  Redirige a `/` (index)
2. Click en navbar "Turnos"  `/turnoscli/turnos`
3. Selecciona fecha, hora y servicio
4. Confirma reserva
5. Recibe confirmación

**Peluquero**:
1. Login  Redirige a `/` (index)
2. Click en "Administración"  `/adm2/`
3. Click en "Turnos" (menú lateral)  `/turnosadm/`
4. Ve lista de turnos pendientes
5. Confirma o gestiona turnos

**Gerente**:
1. Login  Redirige directamente a `/adm2/`
2. Tiene acceso a ambas interfaces (cliente y admin)
3. Puede gestionar turnos igual que el peluquero
