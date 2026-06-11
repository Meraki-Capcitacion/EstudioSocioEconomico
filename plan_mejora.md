# Plan de Mejora — EstudioEcoNom

**Versión:** 1.0
**Fecha:** 2026-06-11
**Estado del proyecto:** Fases 1–9 completadas. Este documento consolida las tareas pendientes del `plan_final.md` y los bugs conocidos identificados en sesiones posteriores.

---

## Resumen Ejecutivo

| # | Tarea | Tipo | Esfuerzo | Prioridad |
|---|-------|------|----------|-----------|
| A1 | `guardar_idioma` — contexto `'salud'` faltante | Bug | Muy bajo | Alta |
| A2 | Link `idioma_list` incorrecto en `estudio_detail.html` | Bug | Muy bajo | Alta |
| A3 | `tab_list` no cableado en `EstudioDetailView` | Bug | Bajo | Media |
| A4 | `CONTEXT.md` — `ANTHROPIC_API_KEY` obsoleta | Docs | Muy bajo | Baja |
| 24 | Race condition en folio de `Persona` | Fix | Bajo | Alta |
| 21 | `apps/auditorias` — trazabilidad de acciones | Feature | Medio | Media |
| 23 | Tests automatizados para flujos críticos | Feature | Medio | Media |
| 22 | `apps/api` — endpoints REST con DRF | Feature | Alto | Baja |

**Orden de ejecución sugerido:** A1 → A2 → 24 → A3 → 21 → 23 → A4 → 22

---

## Sección A — Bugs Menores Conocidos

Identificados en la sesión del 2026-05-25 como bugs fuera del alcance de esa corrección. Son cambios de una o pocas líneas.

---

### A1 — `guardar_idioma`: contexto `'salud'` faltante en error

**Archivo:** `apps/estudios/views_candidato.py`
**Impacto:** Cuando el formulario de idioma falla validación, la página se re-renderiza sin el banner verde de salud ya guardada, confundiendo al candidato.

**Diagnóstico:**
En el mismo paso 3 del portal candidato existe un bug simétrico al ya corregido en `guardar_educacion`. La rama de error de `guardar_idioma` no incluye `'salud': salud` en el contexto de respuesta.

**Fix:**
Buscar el bloque `ctx.update(...)` en la rama de error de `guardar_idioma` dentro de `Paso3View` y agregar `'salud': salud` al igual que se hizo para `guardar_educacion`.

```python
# Antes (rama de error en guardar_idioma):
ctx.update({
    'idioma_form': idioma_form,
    'educacion_form': ...,
    # falta 'salud': salud
})

# Después:
ctx.update({
    'idioma_form': idioma_form,
    'educacion_form': ...,
    'salud': salud,
})
```

**Archivos a modificar:**
- `apps/estudios/views_candidato.py` — rama `guardar_idioma` error context

---

### A2 — Link `idioma_list` incorrecto en `estudio_detail.html`

**Archivo:** `templates/estudios/estudio_detail.html`
**Impacto:** El botón "Agregar idioma" en la vista de detalle del estudio lleva al listado (`idioma_list`) en vez de al formulario de creación (`idioma_create`), rompiendo el flujo de captura.

**Fix:**
```html
<!-- Antes: -->
<a href="{% url 'educacion:idioma_list' %}">Agregar idioma</a>

<!-- Después: -->
<a href="{% url 'educacion:idioma_create' %}?persona={{ estudio.persona.pk }}&back={{ estudio.pk }}">
    Agregar idioma
</a>
```

**Archivos a modificar:**
- `templates/estudios/estudio_detail.html` — enlace de "Agregar idioma"

---

### A3 — `tab_list` no cableado en `EstudioDetailView`

**Archivo:** `apps/estudios/views.py`
**Impacto:** La variable `tab_list` nunca llega al template `estudio_detail.html`, por lo que el bloque `{% empty %}` siempre dispara y se muestran los 12 tabs hardcodeados. El sistema de secciones configurables por `TipoEstudio.secciones` (JSONField) no tiene efecto visible.

**Diagnóstico:**
`TipoEstudio` ya tiene el campo `secciones` (JSONField con lista de strings). El template ya tiene la lógica `{% for tab in tab_list %}...{% empty %}...{% endfor %}`. Solo falta poblar `tab_list` en el contexto de la vista.

**Fix en `EstudioDetailView.get_context_data`:**
```python
def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    estudio = self.object
    secciones = estudio.tipo_estudio.secciones or []
    if secciones:
        ctx['tab_list'] = secciones
    # Si secciones vacío, tab_list no se define y el {% empty %} muestra todos
    return ctx
```

**Consideraciones:**
- Si `TipoEstudio.secciones` está vacío o es `None`, mantener el comportamiento actual (todos los tabs visibles).
- Verificar que los valores en `secciones` coincidan exactamente con los IDs de tabs en el template.

**Archivos a modificar:**
- `apps/estudios/views.py` — `EstudioDetailView.get_context_data`

---

### A4 — `CONTEXT.md` / `Apéndice C`: `ANTHROPIC_API_KEY` obsoleta

**Archivo:** `CONTEXT.md`
**Impacto:** Documentación incorrecta — el proyecto migró de Anthropic a DigitalOcean AI en la Fase 9, pero el Apéndice C aún lista `ANTHROPIC_API_KEY` como variable de entorno activa.

**Fix:**
En el Apéndice C de `CONTEXT.md`, reemplazar:
```
| `ANTHROPIC_API_KEY` | No | `''` | API key de Anthropic para análisis IA con Claude Haiku |
```
Por:
```
| `DO_MODEL_ACCESS_KEY` | No | `''` | API key de DigitalOcean AI (endpoint OpenAI-compatible) |
```

También actualizar el bloque `.env` de ejemplo en el mismo apéndice.

**Archivos a modificar:**
- `CONTEXT.md` — Apéndice C, tabla de variables y ejemplo `.env`

---

## Tarea 24 — Race Condition en Folio de `Persona`

**Archivo:** `apps/personas/models.py`
**Prioridad:** Alta — afecta integridad de datos en producción
**Esfuerzo:** Bajo — 10 líneas en 1 archivo

### Problema actual

```python
# apps/personas/models.py — método save() actual
last_study = Persona.objects.filter(
    folio__startswith=f'{year}{month}'
).order_by('-folio').first()
# ← VENTANA DE RACE CONDITION AQUÍ
# Dos requests simultáneos leen el mismo `last_study` y generan el mismo folio
```

### Fix: `select_for_update()` dentro de `transaction.atomic()`

```python
from django.db import transaction

def save(self, *args, **kwargs):
    # Normalizar nombres (código existente — no modificar)
    if self.nombre:
        self.nombre = self.nombre.strip().title()
    if self.apellido_paterno:
        self.apellido_paterno = self.apellido_paterno.strip().title()
    if self.apellido_materno:
        self.apellido_materno = self.apellido_materno.strip().title()

    if not self.folio:
        with transaction.atomic():
            year = timezone.now().strftime('%Y')
            month = timezone.now().strftime('%m')
            last = (
                Persona.objects
                .select_for_update()
                .filter(folio__startswith=f'{year}{month}')
                .order_by('-folio')
                .first()
            )
            if last:
                ultimo_num = int(last.folio[6:])
                self.folio = f'{year}{month}{str(ultimo_num + 1).zfill(4)}'
            else:
                self.folio = f'{year}{month}0001'

    super().save(*args, **kwargs)
```

**Nota:** `select_for_update()` solo bloquea filas en PostgreSQL y MySQL. Con SQLite (desarrollo) no tiene efecto pero tampoco hay riesgo real de concurrencia. El fix es transparente para el entorno de desarrollo.

### Archivos a modificar
- `apps/personas/models.py` — método `save()`
- `apps/personas/tests.py` — agregar test de concurrencia (ver Tarea 23)

---

## Tarea 21 — `apps/auditorias`: Registro de Trazabilidad

**Estado actual:** App creada, `models.py` vacío, sin `urls.py`, sin `signals.py`.
**Prioridad:** Media
**Esfuerzo:** Medio — 7 archivos nuevos + modificaciones en settings y urls

### Objetivo

Registrar automáticamente quién hizo qué y cuándo sobre los modelos críticos, sin requerir cambios en las vistas existentes.

### Paso 1 — Modelo `RegistroAuditoria`

```python
# apps/auditorias/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistroAuditoria(models.Model):
    ACCIONES = [
        ('CRE', 'Creó'),
        ('MOD', 'Modificó'),
        ('ELI', 'Eliminó'),
        ('CAM', 'Cambió estado'),
        ('VER', 'Verificó'),
    ]

    usuario       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    accion        = models.CharField(max_length=3, choices=ACCIONES)
    modelo        = models.CharField(max_length=100)   # Ej: "EstudioSocioeconomico"
    objeto_id     = models.PositiveIntegerField()
    descripcion   = models.TextField()                 # Ej: "Cambió estado BOR → VIS"
    datos_antes   = models.JSONField(null=True, blank=True)
    datos_despues = models.JSONField(null=True, blank=True)
    ip_address    = models.GenericIPAddressField(null=True, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Registro de auditoría'
        verbose_name_plural = 'Registros de auditoría'

    def __str__(self):
        return f'{self.get_accion_display()} {self.modelo} #{self.objeto_id}'
```

### Paso 2 — Middleware para capturar request

```python
# apps/auditorias/middleware.py
import threading

_thread_locals = threading.local()

def get_request():
    return getattr(_thread_locals, 'request', None)

class AuditoriaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        response = self.get_response(request)
        return response
```

Agregar en `esteconom/settings.py` después de `AuthenticationMiddleware`:
```python
'apps.auditorias.middleware.AuditoriaMiddleware',
```

### Paso 3 — Signals para modelos críticos

```python
# apps/auditorias/signals.py
# Conectar post_save / post_delete en:
#   EstudioSocioeconomico  — CRE, MOD, CAM (detectar cambio de estado)
#   Persona                — CRE, MOD
#   EvaluacionRiesgo       — CRE, MOD
#   Documento              — VER (cuando verificado cambia a True)
#   HistorialLaboral       — VER
#   Referencia             — VER
```

Patrón de función auxiliar:
```python
def _registrar(accion, instance, descripcion, datos_antes=None, datos_despues=None):
    from .models import RegistroAuditoria
    from .middleware import get_request
    request = get_request()
    RegistroAuditoria.objects.create(
        usuario=request.user if request and request.user.is_authenticated else None,
        accion=accion,
        modelo=instance.__class__.__name__,
        objeto_id=instance.pk,
        descripcion=descripcion,
        datos_antes=datos_antes,
        datos_despues=datos_despues,
        ip_address=request.META.get('REMOTE_ADDR') if request else None,
    )
```

### Paso 4 — Vistas de consulta (solo lectura)

```python
# apps/auditorias/views.py
# AuditoriaListView:
#   - LoginRequiredMixin + AnalistaRequeridoMixin
#   - Filtros: modelo, usuario, rango de fechas, acción
#   - paginate_by = 50
#   - Template: auditorias/auditoria_list.html
```

### Paso 5 — Registrar en URL y módulos

```python
# esteconom/urls.py
path('auditorias/', include('apps.auditorias.urls')),

# apps/usuarios/models.py — MODULOS_DISPONIBLES
# Agregar 'auditorias' a la lista
```

### Archivos a crear/modificar

| Archivo | Acción |
|---------|--------|
| `apps/auditorias/models.py` | Crear `RegistroAuditoria` |
| `apps/auditorias/middleware.py` | Crear — captura request en thread-local |
| `apps/auditorias/signals.py` | Crear — conectar a modelos críticos |
| `apps/auditorias/views.py` | Crear — `AuditoriaListView` |
| `apps/auditorias/urls.py` | Crear |
| `apps/auditorias/admin.py` | Actualizar — registrar modelo en admin |
| `apps/auditorias/apps.py` | Modificar — importar signals en `ready()` |
| `templates/auditorias/auditoria_list.html` | Crear |
| `esteconom/settings.py` | Agregar middleware |
| `esteconom/urls.py` | Agregar ruta |

---

## Tarea 23 — Tests Automatizados

**Estado actual:** Archivos `tests.py` existentes en todas las apps pero vacíos (solo placeholder).
**Prioridad:** Media
**Esfuerzo:** Medio — implementar tests en 4+ archivos

### Prioridad 1 — Tests de modelos (unitarios)

#### `apps/personas/tests.py`
```python
# TestPersonaFolio
#   - Crear Persona → folio tiene formato YYYYMMNNNNN (11 chars)
#   - Folio empieza con año y mes actuales
#   - El folio no es editable (no se sobreescribe si ya existe)

# TestPersonaFolioSecuencial
#   - Crear dos Personas en el mismo mes → folios distintos y secuenciales
#   - Segunda persona tiene folio = primera + 1
```

#### `apps/economia/tests.py`
```python
# TestSituacionEconomicaProperties
#   - ingreso_total_mensual = suma de los 5 campos de ingreso
#   - egreso_total_mensual = suma de los 8 campos de egreso
#   - capacidad_ahorro = ingreso_total - egreso_total
#   - capacidad_ahorro negativa cuando egresos > ingresos
```

#### `apps/estudios/tests.py` — modelos
```python
# TestTransicionesEstado
#   - BOR → VIS: válida
#   - BOR → APR: inválida
#   - COM → CAN: inválida
#   - REC → BOR: válida (corrección)
#   - APR → cualquiera: inválida (estado terminal)
```

### Prioridad 2 — Tests de vistas

#### `apps/estudios/tests.py` — vistas
```python
# TestEstudioDetailView
#   - Sin login → redirige a /accounts/login/
#   - Con login → HTTP 200, contiene nombre del candidato

# TestCambiarEstadoView
#   - Transición válida (BOR → VIS) → HTTP 302, estado actualizado
#   - Transición inválida (BOR → APR) → HTTP 400 o mensaje de error
#   - Requiere login

# TestGenerarTokenView
#   - POST en estudio sin token → crea EstudioToken, HTTP 302
#   - POST en estudio con token activo → no crea duplicado
```

#### `apps/estudios/tests_candidato.py` (nuevo archivo)
```python
# TestPortalCandidato
#   - Token válido → GET /candidato/<uuid>/ → HTTP 200
#   - Token inválido (UUID inexistente) → HTTP 302 a token_invalido
#   - Token expirado → HTTP 302 a token_invalido
#   - Token completado (activo=False) → HTTP 302 a token_invalido

# TestPaso1Submit
#   - POST con datos válidos → guarda Persona, redirige a paso 2
#   - POST con CURP inválido → HTTP 200, muestra errores

# TestFlujoCandidatoCompleto (integración)
#   - Pasos 1-7 completos → GraciasView, token.activo=False
```

#### `apps/estudios/tests_ia.py` (nuevo archivo)
```python
# TestAnalizarEstudioIAView
#   - Mock del cliente OpenAI (DigitalOcean)
#   - POST → guarda aspectos_positivos, aspectos_negativos, conclusion en BD
#   - Retorna JSON {ok: true, ...}
#   - Error de API → retorna JSON {error: "..."}

# TestSugerirEvaluacionIAView
#   - Mock del cliente OpenAI
#   - POST → retorna JSON con 6 puntuaciones + 3 campos de texto
#   - NO guarda nada en BD
```

### Prioridad 3 — Tests de concurrencia

#### `apps/personas/tests.py` (agregar)
```python
# TestPersonaFolioConcurrencia
#   - Usar ThreadPoolExecutor para crear 10 Personas simultáneamente
#   - Verificar que todos los folios son únicos
#   - Solo significativo con PostgreSQL; con SQLite se puede omitir o marcar skip
import concurrent.futures
from django.test import TransactionTestCase  # No TestCase — necesita transacciones reales
```

### Comandos de ejecución

```bash
# Correr toda la suite
python manage.py test --verbosity=2

# Por módulo
python manage.py test apps.personas --verbosity=2
python manage.py test apps.estudios --verbosity=2
python manage.py test apps.economia --verbosity=2

# Solo tests de integración del portal
python manage.py test apps.estudios.tests_candidato --verbosity=2
```

### Archivos a crear/modificar

| Archivo | Tests a implementar |
|---------|-------------------|
| `apps/personas/tests.py` | Folio, secuencia, concurrencia |
| `apps/economia/tests.py` | Properties calculadas |
| `apps/estudios/tests.py` | Transiciones de estado, vistas, token |
| `apps/estudios/tests_candidato.py` | Portal candidato pasos 1-7 |
| `apps/estudios/tests_ia.py` | Vistas IA con mocks |

---

## Tarea 22 — `apps/api`: Endpoints REST con DRF

**Estado actual:** App creada, `models.py` vacío, sin `urls.py`, sin serializers.
**Prioridad:** Baja — para integraciones externas futuras
**Esfuerzo:** Alto — 6 archivos nuevos + dependencias + configuración

### Dependencias a instalar

```bash
pip install djangorestframework djangorestframework-simplejwt django-filter
```

Agregar a `requirements.txt`:
```
djangorestframework
djangorestframework-simplejwt
django-filter
```

### Paso 1 — Configuración en `settings.py`

```python
INSTALLED_APPS += [
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}
```

### Paso 2 — Serializers

```python
# apps/api/serializers.py

# PersonaSerializer — lectura: folio, nombre_completo, curp, email, telefono_movil
# EstudioListSerializer — lectura: pk, persona (folio+nombre), estado, tipo_estudio, created_at
# EstudioDetalleSerializer — lectura: estudio completo con relaciones anidadas (educacion, laboral, etc.)
# EvaluacionRiesgoSerializer — lectura/escritura: 6 puntuaciones + score_final + nivel_riesgo
# CambiarEstadoSerializer — escritura: nuevo_estado (valida contra TRANSICIONES_VALIDAS)
```

### Paso 3 — ViewSets

```python
# apps/api/views.py

# PersonaViewSet — list, retrieve (solo lectura, requiere autenticación)
#   Filtros: nombre, curp, folio
#   Búsqueda: nombre_completo, folio, curp

# EstudioViewSet — list, retrieve (solo lectura externa)
#   Acción extra: POST /api/v1/estudios/{pk}/cambiar_estado/ → CambiarEstadoSerializer

# EvaluacionRiesgoViewSet — list, retrieve, create, update
#   Solo para analistas (verificar rol via PerfilUsuario)
```

### Paso 4 — Permisos basados en rol

```python
# apps/api/permissions.py
from rest_framework.permissions import BasePermission

class EsAnalista(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'perfil') and
            request.user.perfil.es_analista
        )
```

### Paso 5 — URLs

```python
# apps/api/urls.py
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register('personas', PersonaViewSet, basename='persona')
router.register('estudios', EstudioViewSet, basename='estudio')
router.register('evaluaciones', EvaluacionRiesgoViewSet, basename='evaluacion')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
```

Registrar en `esteconom/urls.py`:
```python
path('api/v1/', include('apps.api.urls')),
```

### Endpoints resultantes

| Método | URL | Descripción |
|--------|-----|-------------|
| POST | `/api/v1/token/` | Obtener JWT (usuario + contraseña) |
| POST | `/api/v1/token/refresh/` | Renovar JWT |
| GET | `/api/v1/personas/` | Listar personas (paginado, con filtros) |
| GET | `/api/v1/personas/{id}/` | Detalle de persona |
| GET | `/api/v1/estudios/` | Listar estudios |
| GET | `/api/v1/estudios/{id}/` | Detalle de estudio |
| POST | `/api/v1/estudios/{id}/cambiar_estado/` | Transicionar estado |
| GET | `/api/v1/evaluaciones/` | Listar evaluaciones |
| POST | `/api/v1/evaluaciones/` | Crear evaluación |
| PUT/PATCH | `/api/v1/evaluaciones/{id}/` | Actualizar evaluación |

### Archivos a crear/modificar

| Archivo | Acción |
|---------|--------|
| `apps/api/serializers.py` | Crear |
| `apps/api/views.py` | Implementar (actualmente vacío) |
| `apps/api/urls.py` | Crear |
| `apps/api/permissions.py` | Crear |
| `apps/api/tests.py` | Implementar tests de endpoints |
| `esteconom/settings.py` | Agregar DRF config |
| `esteconom/urls.py` | Agregar ruta `/api/v1/` |
| `requirements.txt` | Agregar 3 dependencias |

---

## Orden de Ejecución Recomendado

```
Sesión 1 — Bugs rápidos (1-2 horas)
  ├── A1: guardar_idioma contexto salud faltante    (~5 min)
  ├── A2: idioma_list → idioma_create link          (~5 min)
  └── 24: select_for_update en Persona.save()       (~15 min)

Sesión 2 — Mejoras de comportamiento (2-3 horas)
  ├── A3: tab_list en EstudioDetailView             (~30 min)
  └── A4: CONTEXT.md Apéndice C actualización      (~10 min)

Sesión 3 — Auditorías (4-6 horas)
  └── 21: apps/auditorias completa

Sesión 4 — Tests (4-6 horas)
  └── 23: Suite de tests prioritarios

Sesión 5 — API REST (6-8 horas, cuando se requiera)
  └── 22: apps/api con DRF
```

---

## Notas de Implementación

1. **Siempre correr `python manage.py check` después de cada cambio** — detecta errores de configuración antes de arrancar el servidor.
2. **Para Tarea 21 (auditorías):** El middleware de auditoría debe ir DESPUÉS de `AuthenticationMiddleware` en `settings.py` para tener acceso a `request.user`.
3. **Para Tarea 22 (API):** No exponer campos sensibles en los serializers — verificar que `numero_identificacion`, `curp`, `rfc` y `nss` solo sean visibles para usuarios autenticados con rol ANA/AUD.
4. **Para Tarea 23 (tests):** Usar `TestCase` para tests unitarios y `TransactionTestCase` solo donde se necesiten transacciones reales (test de concurrencia del folio).
5. **`select_for_update()` y SQLite:** En desarrollo con SQLite, `select_for_update()` no lanza error pero tampoco bloquea. El código es compatible con ambas BDs.

---

*Creado el 2026-06-11. Actualizar `CONTEXT.md` al completar cada tarea marcando su estado como ✅.*
