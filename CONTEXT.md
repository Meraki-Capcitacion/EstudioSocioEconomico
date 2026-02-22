# Documento de Contexto Arquitectónico — EstudioEcoNom

**Versión:** 1.1
**Fecha:** 2026-02-21
**Proyecto:** Sistema de Gestión de Estudios Socioeconómicos (EstudioEcoNom)
**Stack:** Django 6.0.2 · SQLite/PostgreSQL · Tailwind CSS CDN · Python 3.x
**Idioma:** Español mexicano (`es-mx`) · Zona horaria: `America/Mexico_City`

---

## Tabla de Contenidos

1. [Mapa Arquitectónico Completo](#1-mapa-arquitectónico-completo)
2. [Análisis por App](#2-análisis-por-app)
3. [Perfiles de Usuario y Casos de Uso](#3-perfiles-de-usuario-y-casos-de-uso)
4. [Plan de Implementación Frontend](#4-plan-de-implementación-frontend)
5. [Guía para Otros Agentes](#5-guía-para-otros-agentes)
6. [Próximos Pasos Concretos](#6-próximos-pasos-concretos)

---

## 1. Mapa Arquitectónico Completo

### 1.1 Diagrama de Apps y Dependencias

```
esteconom/                    ← Configuración del proyecto Django
├── settings.py               ← SECRET_KEY, INSTALLED_APPS, BD, TZ, AUTH
├── urls.py                   ← Enrutador principal
└── wsgi.py / asgi.py

apps/
├── configuracion/            ← BASE: TimestampModel + catálogos
│   └── dependen de ella:     todos los demás apps de dominio
│
├── personas/                 ← ENTIDAD CENTRAL: Persona + SaludPersona + folio
│   └── dependen de ella:     estudios, domicilios, economia (indirecta),
│                             educacion, laboral, familia, referencias, documentos
│
├── estudios/                 ← NODO HUB: EstudioSocioeconomico (máquina de estados)
│   └── dependen de ella:     economia, visitas, evaluacion, documentos, notificaciones
│
├── domicilios/               ← FK a Persona
├── economia/                 ← OneToOne con EstudioSocioeconomico
├── educacion/                ← FK a Persona (Educacion + Idioma)
├── laboral/                  ← FK a Persona (con verificación)
├── familia/                  ← FK a Persona
├── referencias/              ← FK a Persona (con verificación)
├── visitas/                  ← FK a EstudioSocioeconomico (con GPS)
├── evaluacion/               ← OneToOne con EstudioSocioeconomico (scoring)
├── documentos/               ← FK a Persona + FK a EstudioSocioeconomico
├── notificaciones/           ← FK a User + FK a EstudioSocioeconomico
│
├── auditorias/               ← PLACEHOLDER (models.py vacío)
├── reportes/                 ← PLACEHOLDER (models.py vacío)
└── api/                      ← PLACEHOLDER (models.py vacío)
```

### 1.2 Diagrama de Relaciones entre Modelos

```
auth.User (Django built-in)
    │
    ├── TimestampModel.created_by (FK, SET_NULL)
    ├── TimestampModel.updated_by (FK, SET_NULL)
    ├── VisitaDomiciliaria.evaluador (FK, SET_NULL)
    ├── EvaluacionRiesgo.evaluador (FK, SET_NULL)
    ├── Documento.verificado_por (FK, SET_NULL)
    └── Notificacion.usuario (FK, CASCADE)

TipoEstudio  ─────── (configuracion)
    │ PROTECT
    └── EstudioSocioeconomico.tipo_estudio

NivelEducativo ────── (educacion, catálogo)
    │ PROTECT
    └── Educacion.nivel

Persona ──────────────────────────────────── (entidad central)
    │                                         folio: YYYYMMNNNNN (auto-gen)
    ├─── OneToOne ──► SaludPersona            nivel_salud, enfermedades, sustancias
    ├─── CASCADE ───► Domicilio (1..N)        tipo: ACT/ANT/REF
    ├─── CASCADE ───► Educacion (1..N)        nivel, institucion, titulo
    ├─── CASCADE ───► Idioma (1..N)           idioma, % dominio, certificación
    ├─── CASCADE ───► HistorialLaboral (1..N) verificada, fecha_verificacion
    ├─── CASCADE ───► GrupoFamiliar (1..N)    tipo_dependencia, telefono
    ├─── CASCADE ───► Referencia (1..N)       verificada, comentarios_verificacion
    ├─── CASCADE ───► Documento (1..N)        tipo, archivo, verificado
    └─── CASCADE ───► EstudioSocioeconomico (1..N)
                            │ estado: BOR→VIS→PRO→COM→REV→APR/REC/CAN
                            │
                            ├── OneToOne ──► SituacionEconomica
                            │                   ingresos (5 campos)
                            │                   egresos (8 campos)
                            │                   patrimonio + créditos + AFORE
                            │                   @property: ingreso_total_mensual
                            │                   @property: egreso_total_mensual
                            │                   @property: capacidad_ahorro
                            │
                            ├── OneToOne ──► EvaluacionRiesgo
                            │                   6 puntuaciones (0-100 c/u)
                            │                   score_final, nivel_riesgo (BAJ/MED/ALT/CRI)
                            │                   factores_riesgo, recomendacion_final
                            │
                            ├── CASCADE ───► VisitaDomiciliaria (1..N)
                            │                   evaluador (FK User)
                            │                   GPS (latitud, longitud)
                            │                   entorno: tipo_zona, nivel_seguridad (1-5)
                            │
                            ├── CASCADE ───► Documento (1..N, opcional)
                            │                   verificado, verificado_por
                            │
                            └── CASCADE ───► Notificacion (1..N)
                                                usuario (FK User)
                                                tipo, prioridad (ALT/MED/BAJ)
                                                leida, fecha_lectura
```

### 1.3 Flujo de Estados del Estudio

```
                    [INICIO]
                       │
                       ▼
                  ┌─────────┐
                  │   BOR   │  Borrador — datos iniciales capturados
                  └────┬────┘
                       │ (programar visita)
                       ▼
                  ┌─────────┐
                  │   VIS   │  Visita Programada — fecha_programada_visita definida
                  └────┬────┘
                       │ (iniciar proceso)
                       ▼
                  ┌─────────┐
                  │   PRO   │  En Proceso — recopilación activa de datos
                  └────┬────┘
                       │ (completar datos)
                       ▼
                  ┌─────────┐
                  │   COM   │  Completado — fecha_realizacion definida
                  └────┬────┘
                       │ (enviar a revisión)
                       ▼
                  ┌─────────┐
                  │   REV   │  En Revisión — revisión por analista senior
                  └────┬────┘
              ┌────────┼────────┐
              │        │        │
              ▼        ▼        ▼
         ┌────────┐ ┌────────┐ ┌────────┐
         │  APR   │ │  REC   │ │  CAN   │
         └────────┘ └────────┘ └────────┘
         Aprobado   Rechazado  Cancelado
         fecha_     (motivo en (puede
         aprobacion  conclusion) ocurrir
                               en cualquier
                               estado)
```

### 1.4 Flujos de Verificación

Los siguientes modelos tienen un workflow de verificación con 3 campos:

| Modelo | Campo verificación | Timestamp | Campo extra |
|--------|-------------------|-----------|-------------|
| `HistorialLaboral` | `verificada` (bool) | `fecha_verificacion` | — |
| `Referencia` | `verificada` (bool) | `fecha_verificacion` | `comentarios_verificacion` |
| `Documento` | `verificado` (bool) | `fecha_verificacion` | `verificado_por` (FK User) |
| `Educacion` | `documento_verificado` (bool) | — | — |

---

## 2. Análisis por App

### 2.1 `configuracion` — Base Abstracta y Catálogos

**Propósito:** Define la clase base `TimestampModel` que hereda casi todo el proyecto, y el catálogo `TipoEstudio`.

**Modelos:**

**`TimestampModel`** (abstracto — no genera tabla)
- `created_at` — DateTimeField, auto_now_add
- `updated_at` — DateTimeField, auto_now
- `created_by` — FK a `auth.User`, `SET_NULL`, related_name `%(class)s_created`
- `updated_by` — FK a `auth.User`, `SET_NULL`, related_name `%(class)s_updated`

**`TipoEstudio`** (catálogo)
- `nombre`, `descripcion`
- `activo` (bool), `orden` (int) — para filtrado y ordenamiento en UI
- `requiere_visita` (bool) — define si el tipo exige visita domiciliaria
- `requiere_verificacion_laboral` (bool)
- `puntuacion_minima_aprobacion` (int, default 70) — threshold para aprobación automática

**Notas especiales:**
- `TipoEstudio` NO hereda de `TimestampModel` (tiene sus propios `created_at`, `updated_at` sin campos `_by`)
- `NivelEducativo` (app `educacion`) sigue el mismo patrón de catálogo
- Siempre hay que poblar `created_by` y `updated_by` al guardar registros de otros modelos

**URLs:** `configuracion:tipoestudio_list/create/detail/update/delete`

---

### 2.2 `personas` — Entidad Central

**Propósito:** Perfil del solicitante/evaluado. Es el núcleo de todo el sistema.

**Modelo `Persona`** (hereda TimestampModel)

| Campo | Tipo | Notas |
|-------|------|-------|
| `folio` | CharField(20), unique, editable=False | Auto-generado en `save()`: `YYYYMMNNNNN` |
| `nombre` | CharField(100) | |
| `apellido_paterno` | CharField(100) | |
| `apellido_materno` | CharField(100), blank | |
| `fecha_nacimiento` | DateField | |
| `lugar_nacimiento` | CharField(200), blank | Ciudad/estado de nacimiento |
| `tipo_identificacion` | choices: INE/PAS/CED/CAR/OTR | |
| `numero_identificacion` | CharField(50) | |
| `curp` | CharField(18) | Validador regex `^[A-Z0-9]{18}$` |
| `rfc` | CharField(13), blank | Validador regex RFC mexicano |
| `nss` | CharField(11), blank | Número de Seguridad Social |
| `licencia_manejo_folio` | CharField(50), blank | Número/folio de licencia de manejo |
| `cartilla_militar_folio` | CharField(50), blank | Número/folio de cartilla militar |
| `acta_nacimiento_numero` | CharField(50), blank | Número de acta de nacimiento |
| `email` | EmailField | |
| `telefono_movil` | CharField(15) | |
| `telefono_fijo` | CharField(15), blank | |
| `facebook_perfil` | CharField(200), blank | Usuario o URL del perfil |
| `estado_civil` | choices: SOL/CAS/ULB/DIV/VIU/SEP/**OTR** | Se agregó 'OTR' para "Otro" |
| `numero_dependientes` | IntegerField, MinValue(0) | |
| `peso` | DecimalField(5,2), null | En kilogramos |
| `estatura` | DecimalField(5,2), null | En centímetros |
| `historial_residencias` | TextField, blank | Lugares anteriores con período y motivo |
| `periodos_sin_laborar` | TextField, blank | Períodos sin empleo y actividad durante ese tiempo |
| `actividades_tiempo_libre` | TextField, blank | Actividad, frecuencia y tiempo dedicado |
| `activo` | BooleanField, default=True | Soft delete |

**Property:** `nombre_completo` → `"{nombre} {apellido_paterno} {apellido_materno}".strip()`

**Algoritmo de folio:**
```python
# Formato: YYYYMMNNNNN (ejemplo: 202602000 1)
# Busca el último folio del mes actual, incrementa en 1
# Si no existe, inicia con '0001'
# ADVERTENCIA: No usa transacción atómica — posible race condition en producción
```

**Índices de base de datos:** `folio`, `curp`, `(apellido_paterno, apellido_materno, nombre)`

---

**Modelo `SaludPersona`** (hereda TimestampModel — OneToOne con Persona)

| Campo | Tipo | Notas |
|-------|------|-------|
| `persona` | OneToOne → Persona, CASCADE | related_name: `salud` |
| `nivel_salud` | choices: EXC/BUE/REG/MAL, blank | Autopercepción del estado de salud |
| `enfermedades_cronicas` | TextField, blank | Enfermedades, alergias, discapacidad y tratamiento |
| `antecedentes_familiares` | TextField, blank | Enfermedades y familiares que las padecen |
| `consumo_sustancias` | TextField, blank | Alcohol, tabaco, medicamentos sin receta, estupefacientes; frecuencia |

**URLs:** `personas:persona_list/create/detail/update/delete`

---

### 2.3 `estudios` — Nodo Hub (Máquina de Estados)

**Propósito:** Representa un estudio socioeconómico completo. Es el contenedor que agrupa todas las evaluaciones.

**Modelo `EstudioSocioeconomico`** (hereda TimestampModel)

| Campo | Tipo | Notas |
|-------|------|-------|
| `persona` | FK → Persona, CASCADE | related_name: `estudios` |
| `tipo_estudio` | FK → TipoEstudio, PROTECT | No se puede borrar si hay estudios |
| `estado` | choices(3): BOR/VIS/PRO/COM/REV/APR/REC/CAN | default: `BOR` |
| `fecha_programada_visita` | DateTimeField, null | Se llena en estado VIS |
| `fecha_realizacion` | DateTimeField, null | Se llena al completar |
| `fecha_aprobacion` | DateTimeField, null | Se llena al aprobar |
| `observaciones` | TextField, blank | Notas del proceso |
| `conclusion` | TextField, blank | Resultado final / motivo de rechazo |
| `puntuacion_total` | DecimalField(5,2), null | Se copia desde EvaluacionRiesgo |
| `expectativas_salariales` | CharField(200), blank | Expectativas económicas del candidato |
| `medio_enterado_vacante` | choices: FAC/REF/OTR, blank | Cómo se enteró de la vacante |
| `tiempo_traslado` | CharField(100), blank | Tiempo estimado de traslado domicilio-empresa |
| `comentarios_adicionales` | TextField, blank | Campo libre del solicitante |

**Acciones de admin disponibles:** `marcar_en_proceso` (BOR→PRO), `marcar_completado` (PRO→COM)

**NOTA IMPORTANTE:** El campo `estado` se transiciona manualmente. No hay lógica de transición automática ni validación de estados permitidos en el modelo — esto debe implementarse en las vistas o en un método `transicionar(nuevo_estado)`.

**URLs:** `estudios:estudio_list/create/detail/update/delete`

---

### 2.4 `domicilios` — Domicilio y Servicios

**Propósito:** Registra el o los domicilios del solicitante con detalle de vivienda y servicios.

**Modelo `Domicilio`** (hereda TimestampModel)

| Campo | Tipo | Notas |
|-------|------|-------|
| `persona` | FK → Persona, CASCADE | related_name: `domicilios` |
| `tipo` | choices: ACT/ANT/REF | Actual, Anterior, Referencia |
| `calle` | CharField(200) | |
| `numero_exterior` | CharField(20) | |
| `numero_interior` | CharField(20), blank | |
| `entre_calles` | CharField(200), blank | Característico de CDMX/México |
| `colonia` | CharField(100) | |
| `codigo_postal` | CharField(5) | Solo 5 dígitos |
| `municipio` | CharField(100) | |
| `estado` | CharField(100) | Estado de la República |
| `pais` | CharField(100), default='México' | |
| `tipo_inmueble` | choices: CAS/DEP, blank | Casa o Departamento |
| `tipo_vivienda` | choices: PRO/PROHIP/REN/PRE/FAM/OTR, blank | Tenencia del inmueble |
| `propietario_nombre` | CharField(200), blank | A nombre de quién está el domicilio |
| `material_construccion` | CharField(100), blank | Texto libre |
| `numero_habitaciones` | IntegerField, null | |
| `numero_niveles` | IntegerField, default=1 | |
| `superficie_m2` | DecimalField(8,2), null | Superficie aproximada en m² |
| `valor_inmueble` | DecimalField(14,2), null | Valor aproximado del inmueble |
| `valor_muebles` | choices: R1/R2/R3/R4, blank | Rangos: $1k-$10k / $10k-$20k / $20k-$50k / +$50k |
| `valor_electrodomesticos` | choices: R1/R2/R3/R4, blank | Mismos rangos |
| **Servicios (8 booleanos):** | | |
| `tiene_agua/luz/drenaje/gas/internet/tv_cable` | BooleanField | 6 servicios originales |
| `tiene_pavimentacion` | BooleanField | |
| `tiene_telefono_domicilio` | BooleanField | Teléfono fijo en el inmueble |
| **Espacios (5 booleanos):** | | |
| `tiene_sala/cocina/comedor/patio_servicio/cochera` | BooleanField | |
| **Materiales (7 booleanos):** | | |
| `tiene_piso` | BooleanField | Mosaico/madera/porcelanato |
| `tiene_piso_cemento` | BooleanField | |
| `tiene_enjarre` | BooleanField | Enjarre en las paredes |
| `tiene_paredes_sin_enjarre` | BooleanField | |
| `tiene_techo_lamina` | BooleanField | |
| `tiene_loza` | BooleanField | |
| `tiene_puertas` | BooleanField | |
| `orden_limpieza` | choices: BUE/REG/MAL, blank | Condición general del inmueble |
| `tiempo_residencia_anios` | IntegerField, null | |
| `tiempo_residencia_meses` | IntegerField, null, Min(0), Max(11) | |

**NOTA:** `tipo_vivienda` usa código `'PROHIP'` (6 chars), excepción al estándar de 3 chars.

**URLs:** `domicilios:domicilio_list/create/detail/update/delete`

---

### 2.5 `economia` — Situación Económica

**Propósito:** Captura la fotografía financiera del solicitante vinculada a un estudio específico.

**Modelo `SituacionEconomica`** (NO hereda TimestampModel — relación OneToOne directa)

**Situación autopercibida:**
- `situacion_economica_percibida` — choices: MBU/BUE/REG/MAL/MMA (Muy buena → Muy mala)

**Ingresos (5 campos):**
- `salario_mensual`, `bonos_comisiones`, `ingresos_extra`, `apoyo_familiar`
- `otros_ingresos` + `descripcion_otros_ingresos`

**Egresos (8 campos):**
- `gasto_alimentacion`, `gasto_vivienda`, `gasto_servicios`, `gasto_transporte`
- `gasto_educacion`, `gasto_salud`, `gasto_deudas`, `otros_gastos`
- `descripcion_otros_gastos`

**Patrimonio — Automóvil:**
- `tiene_automovil` + `automovil_marca_modelo` + `automovil_anio`
- `automovil_valor_comercial` — DecimalField(12,2), null
- `automovil_con_adeudo` — BooleanField

**Patrimonio — Inmueble:**
- `patrimonio_inmobiliario` — choices: NINGUNA/PROPIA/INVERSION/TERRENO/OTRO
- `descripcion_patrimonio`

**Cuenta bancaria y AFORE:**
- `institucion_bancaria` — CharField(100), blank
- `afore` — CharField(100), blank

**Créditos y deudas:**
- `tiene_creditos` + 5 tipos de crédito
- `tarjeta_credito_banco` — CharField(200), blank (banco específico)
- `tienda_departamental_nombre` — CharField(200), blank
- `tienda_departamental_adeudo` — DecimalField(12,2), null
- `descripcion_otros_creditos`

**Propiedades calculadas (no persisten en BD):**
```python
@property ingreso_total_mensual  # suma de los 5 campos de ingreso
@property egreso_total_mensual   # suma de los 8 campos de egreso
@property capacidad_ahorro       # ingreso_total - egreso_total
```

**IMPORTANTE:** Nunca intentar filtrar o agregar en BD por `ingreso_total_mensual`, `egreso_total_mensual` o `capacidad_ahorro` — son properties de Python, no columnas SQL.

**URLs:** `economia:situacioneconomica_list/create/detail/update/delete`

---

### 2.6 `educacion` — Historial Educativo e Idiomas

**Propósito:** Registra la formación académica y el dominio de idiomas del solicitante.

**Modelo `NivelEducativo`** (catálogo — NO hereda TimestampModel)
- `nivel` CharField(100), `orden` IntegerField(unique), `activo` BooleanField
- Ordenado por `orden` ASC

**Modelo `Educacion`** (hereda TimestampModel)

| Campo | Tipo | Notas |
|-------|------|-------|
| `persona` | FK → Persona, CASCADE | related_name: `educacion` |
| `nivel` | FK → NivelEducativo, PROTECT | |
| `institucion` | CharField(200) | |
| `ciudad_institucion` | CharField(100), blank | Ciudad donde se localiza la institución |
| `titulo` | CharField(200) | |
| `estado` | choices: INC/COM/TRU/CUR | Incompleto, Completo, Trunco, Cursando |
| `anio_inicio` | IntegerField | |
| `anio_fin` | IntegerField, null | Null si `estado='CUR'` |
| `tipo_documento_estudio` | choices: CER/TIT/CON/CAR/OTR/NIN, blank | Certificado, Título, Constancia, etc. |
| `tiene_cedula` | BooleanField | |
| `numero_cedula` | CharField(20), blank | |
| `documento_verificado` | BooleanField, default=False | |

---

**Modelo `Idioma`** (hereda TimestampModel — FK a Persona)

| Campo | Tipo | Notas |
|-------|------|-------|
| `persona` | FK → Persona, CASCADE | related_name: `idiomas` |
| `idioma` | CharField(100) | Nombre del idioma |
| `porcentaje_habla` | IntegerField, 0-100 | % de dominio oral |
| `porcentaje_escribe` | IntegerField, 0-100 | % de dominio escrito |
| `porcentaje_lee` | IntegerField, 0-100 | % de comprensión lectora |
| `plantel` | CharField(200), blank | Institución donde lo estudió |
| `periodo_inicio` | IntegerField, null | Año de inicio del estudio |
| `periodo_fin` | IntegerField, null | Año de fin del estudio |
| `tiene_certificacion` | BooleanField | |
| `tipo_certificacion` | CharField(100), blank | TOEFL, IELTS, DELF, etc. |
| `nivel_certificacion` | CharField(100), blank | Nivel que acredita la certificación |

**URLs:** `educacion:educacion_list/create/detail/update/delete`, `educacion:idioma_list/create/detail/update/delete` y `educacion:niveleducativo_*`

---

### 2.7 `laboral` — Historial Laboral (con Verificación)

**Propósito:** Registro del historial de empleo con flujo de verificación.

**Modelo `HistorialLaboral`** (hereda TimestampModel)

| Campo | Tipo | Notas |
|-------|------|-------|
| `persona` | FK → Persona, CASCADE | related_name: `historial_laboral` |
| `empresa` | CharField(200) | |
| `puesto` | CharField(200) | |
| `telefono_empresa` | CharField(15) | Para verificación |
| `fecha_inicio` | DateField | |
| `fecha_fin` | DateField, null | Null si es trabajo actual |
| `es_trabajo_actual` | BooleanField | |
| `salario_inicial` | DecimalField(10,2) | |
| `salario_final` | DecimalField(10,2) | |
| `nombre_jefe` | CharField(200) | Para verificación directa |
| `telefono_jefe` | CharField(15) | |
| `motivo_separacion` | TextField, blank | |
| `verificada` | BooleanField, default=False | Workflow de verificación |
| `fecha_verificacion` | DateTimeField, null | Se llena al verificar |

**Acción admin:** `marcar_verificada` — actualiza `verificada=True` y `fecha_verificacion=now()`

**URLs:** `laboral:historiallaboral_list/create/detail/update/delete`

---

### 2.8 `familia` — Grupo Familiar

**Propósito:** Registra los integrantes del núcleo familiar y su relación de dependencia económica.

**Modelo `GrupoFamiliar`** (hereda TimestampModel)

| Campo | Tipo | Notas |
|-------|------|-------|
| `persona` | FK → Persona, CASCADE | related_name: `grupo_familiar` |
| `nombre_completo` | CharField(300) | Campo único de nombre |
| `parentesco` | CharField(100) | Texto libre (esposo/a, hijo/a, etc.) |
| `edad` | IntegerField, Min(0), Max(120) | |
| `tipo_dependencia` | choices: TOT/PAR/IND/ECO | Total, Parcial, Independiente, Aporta |
| `ocupacion` | CharField(200), blank | Si trabaja, indicar empresa |
| `escolaridad` | CharField(100), blank | Texto libre |
| `telefono` | CharField(15), blank | Teléfono del familiar |
| `vive_en_domicilio` | BooleanField, default=True | |
| `ciudad_residencia` | CharField(100), blank | Para familiares que no viven en el domicilio |
| `aporta_ingreso` | BooleanField, default=False | |
| `monto_aportacion` | DecimalField(10,2), default=0 | Solo si `aporta_ingreso=True` |

**URLs:** `familia:grupofamiliar_list/create/detail/update/delete`

---

### 2.9 `referencias` — Referencias Personales/Profesionales (con Verificación)

**Propósito:** Referencias de terceros que avalan al solicitante, con flujo de verificación.

**Modelo `Referencia`** (hereda TimestampModel)

| Campo | Tipo | Notas |
|-------|------|-------|
| `persona` | FK → Persona, CASCADE | related_name: `referencias` |
| `tipo` | choices: PER/LAB/VEC/FAM/COM | Personal, Laboral, Vecinal, Familiar, Comercial |
| `nombre` | CharField(300) | |
| `telefono` | CharField(15) | |
| `email` | EmailField, blank | |
| `parentesco_o_relacion` | CharField(100) | |
| `tiempo_conocer_anios` | IntegerField, MinValue(0) | |
| `domicilio` | TextField, blank | Dirección de la referencia |
| `verificada` | BooleanField, default=False | |
| `fecha_verificacion` | DateTimeField, null | |
| `comentarios_verificacion` | TextField, blank | Notas del contacto |

**Acción admin:** `marcar_verificada`

**URLs:** `referencias:referencia_list/create/detail/update/delete`

---

### 2.10 `visitas` — Visitas Domiciliarias (con GPS)

**Propósito:** Registro de la visita al domicilio del solicitante con evaluación del entorno.

**Modelo `VisitaDomiciliaria`** (hereda TimestampModel)

| Campo | Tipo | Notas |
|-------|------|-------|
| `estudio` | FK → EstudioSocioeconomico, CASCADE | related_name: `visitas` |
| `evaluador` | FK → User, SET_NULL, null | Quien realizó la visita |
| `fecha_visita` | DateTimeField | |
| `latitud` | DecimalField(9,6), null | Coordenada GPS |
| `longitud` | DecimalField(9,6), null | Coordenada GPS |
| `persona_encontrada` | BooleanField, default=True | |
| `verificacion_domicilio` | BooleanField | El domicilio concuerda con lo declarado |
| `tipo_zona` | choices: RES/MIX/POP/RUR/IND | Residencial, Mixto, Popular, Rural, Industrial |
| `nivel_seguridad` | IntegerField, Min(1), Max(5) | Escala Likert |
| `nivel_ruido` | IntegerField, Min(1), Max(5) | Escala Likert |
| `acceso_transporte` | IntegerField, Min(1), Max(5) | Escala Likert |
| `observaciones_generales` | TextField, blank | |
| `recomendacion` | TextField, blank | |

**NOTA:** Un estudio puede tener múltiples visitas (1..N). La relación es FK, no OneToOne.

**URLs:** `visitas:visitadomiciliaria_list/create/detail/update/delete`

---

### 2.11 `evaluacion` — Evaluación de Riesgo (Scoring)

**Propósito:** Scoring multi-categoría que determina el nivel de riesgo del solicitante.

**Modelo `EvaluacionRiesgo`** (NO hereda TimestampModel — solo OneToOne)

| Campo | Tipo | Notas |
|-------|------|-------|
| `estudio` | OneToOne → EstudioSocioeconomico, CASCADE | related_name: `evaluacion_riesgo` |
| `evaluador` | FK → User, SET_NULL, null | |
| `puntuacion_identificacion` | DecimalField(5,2), 0-100 | Categoría 1 |
| `puntuacion_domicilio` | DecimalField(5,2), 0-100 | Categoría 2 |
| `puntuacion_laboral` | DecimalField(5,2), 0-100 | Categoría 3 |
| `puntuacion_economica` | DecimalField(5,2), 0-100 | Categoría 4 |
| `puntuacion_crediticia` | DecimalField(5,2), 0-100 | Categoría 5 |
| `puntuacion_referencias` | DecimalField(5,2), 0-100 | Categoría 6 |
| `score_final` | DecimalField(5,2), 0-100 | Promedio ponderado (calculado externamente) |
| `nivel_riesgo` | choices: BAJ/MED/ALT/CRI | Bajo, Medio, Alto, Crítico |
| `factores_riesgo` | TextField, blank | Descripción de riesgos identificados |
| `factores_atenuantes` | TextField, blank | Factores que reducen el riesgo |
| `recomendacion_final` | TextField | Requerido — decisión del evaluador |

**NOTA:** El `score_final` no se calcula automáticamente — debe calcularse en la vista o servicio al guardar.

**URLs:** `evaluacion:evaluacionriesgo_list/create/detail/update/delete`

---

### 2.12 `documentos` — Gestión Documental (con Verificación)

**Propósito:** Almacén de archivos digitalizados del solicitante con verificación.

**Modelo `Documento`** (hereda TimestampModel)

| Campo | Tipo | Notas |
|-------|------|-------|
| `persona` | FK → Persona, CASCADE | related_name: `documentos` |
| `estudio` | FK → EstudioSocioeconomico, CASCADE, null | Opcional — puede ser doc general |
| `tipo` | choices: IDE/DOM/ING/EST/TIT/ACT/CUR/RFC/FOT/OTR | 10 tipos de documento |
| `archivo` | FileField | Ruta: `documentos/%Y/%m/%d/` |
| `nombre_archivo` | CharField(255) | Nombre original del archivo |
| `tamaño` | IntegerField | En bytes |
| `verificado` | BooleanField, default=False | |
| `fecha_verificacion` | DateTimeField, null | |
| `verificado_por` | FK → User, SET_NULL, null | Quién verificó |

**NOTA:** Se requiere configurar `MEDIA_ROOT` y `MEDIA_URL` en settings para manejo de archivos.

**Acción admin:** `marcar_verificado` (también asigna `verificado_por=request.user`)

**URLs:** `documentos:documento_list/create/detail/update/delete`

---

### 2.13 `notificaciones` — Sistema de Notificaciones

**Propósito:** Notificaciones internas del sistema dirigidas a usuarios específicos.

**Modelo `Notificacion`** (hereda TimestampModel)

| Campo | Tipo | Notas |
|-------|------|-------|
| `usuario` | FK → User, CASCADE | related_name: `notificaciones` |
| `estudio` | FK → EstudioSocioeconomico, CASCADE, null | Contexto del estudio |
| `tipo` | choices: PRO/VIS/DOC/APR/REC/SIS | 6 tipos |
| `titulo` | CharField(200) | |
| `mensaje` | TextField | |
| `leida` | BooleanField, default=False | |
| `fecha_lectura` | DateTimeField, null | |
| `prioridad` | choices: ALT/MED/BAJ | default: MED |

**Ordenado:** `-created_at` (más recientes primero)

**URLs:** `notificaciones:notificacion_list/create/detail/update/delete`

---

### 2.14 `auditorias`, `reportes`, `api` — Placeholders

Estas tres apps tienen `models.py` vacíos y ninguna lógica implementada.

- **`auditorias`:** Sin urls.py propio — no está en `esteconom/urls.py`. Destinada a log de cambios.
- **`reportes`:** Sin urls.py propio. Destinada a generación de PDF/Excel.
- **`api`:** Sin urls.py propio. Destinada a endpoints REST para integraciones.

---

## 3. Perfiles de Usuario y Casos de Uso

El sistema actualmente usa el modelo `auth.User` estándar de Django sin diferenciación de roles. La siguiente sección define los perfiles funcionales que **deben implementarse** mediante grupos de Django (`django.contrib.auth.models.Group`) o un campo `rol` en un perfil extendido de usuario.

### 3.1 Colaborador Interno (Analista / Gestor)

**Descripción:** Personal de oficina que coordina el proceso, revisa la información, verifica documentos y toma decisiones de aprobación o rechazo.

**Acciones que puede realizar:**

| Acción | Apps/Modelos involucrados |
|--------|--------------------------|
| Crear y editar fichas de persona | `personas` |
| Iniciar y gestionar estudios | `estudios` |
| Avanzar el estado del estudio | `estudios.EstudioSocioeconomico.estado` |
| Revisar y verificar documentos | `documentos` |
| Verificar referencias | `referencias` |
| Verificar historial laboral | `laboral` |
| Capturar evaluación de riesgo | `evaluacion` |
| Aprobar o rechazar estudios | `estudios` (estados APR/REC) |
| Enviar notificaciones | `notificaciones` |
| Consultar y gestionar catálogos | `configuracion`, `educacion.NivelEducativo` |
| Generar y descargar reportes | `reportes` (futuro) |
| Ver dashboard general | Vista home |

**Flujo de trabajo típico del Colaborador:**
```
1. Recibe solicitud de nuevo estudio
2. Crea registro en Persona (o busca si ya existe)
3. Crea EstudioSocioeconomico (estado: BOR)
4. Captura datos básicos del solicitante (domicilio, educación, laboral, familia)
5. Define fecha de visita → cambia estado a VIS
6. Asigna visita al personal de campo
7. Recibe reporte de visita → cambia estado a PRO
8. Verifica documentos y referencias
9. Captura o revisa EvaluacionRiesgo
10. Marca estudio como COM (completado)
11. Envía a revisión → estado REV
12. Toma decisión final → APR o REC
```

---

### 3.2 Personal de Campo (Visitador / Investigador)

**Descripción:** Personal que realiza las visitas domiciliarias y el levantamiento físico de información.

**Flujo de trabajo típico del Personal de Campo:**
```
1. Consulta agenda diaria de visitas asignadas
2. Navega a la dirección (dirección del Domicilio tipo ACT)
3. Registra VisitaDomiciliaria:
   - Confirma persona encontrada o no
   - Captura GPS automático (si hay permisos)
   - Evalúa entorno (tipo zona, seguridad, ruido, transporte, escala 1-5)
   - Registra si el domicilio coincide con lo declarado
   - Toma fotos del exterior/interior (sube como Documento tipo FOT)
4. Redacta observaciones y recomendación
5. Actualiza domicilio si hay discrepancias
6. Notifica al colaborador interno que la visita está completa
```

---

### 3.3 Cliente / Solicitante (Portal de Seguimiento)

**Descripción:** La persona a quien se le realiza el estudio. Acceso limitado de solo lectura.

**NOTA:** Este perfil requiere la mayor cantidad de implementación nueva.

---

## 4. Plan de Implementación Frontend

### 4.1 Arquitectura Recomendada

**Recomendación: Django Templates + HTMX (híbrido)**

**Configuración HTMX a agregar en `base.html`:**
```html
<script src="https://unpkg.com/htmx.org@2.0.4"></script>
```

### 4.2 Orden de Implementación Recomendado

**Fase 1 — Base funcional (Semana 1-2)**
1. Instalar HTMX en `base.html`
2. Extender `base.html` con navbar completo (menú, notif badge, breadcrumb)
3. Implementar templates de `personas` (list, detail, form, confirm_delete)
4. Implementar templates de `estudios` (list, detail, form)
5. Vista de detalle del estudio como hub central (con tabs o secciones)

**Fase 2 — Datos del expediente (Semana 3-4)**
6. Templates de `domicilios`
7. Templates de `educacion` + `idiomas`
8. Templates de `laboral` con botón de verificación (HTMX)
9. Templates de `familia`
10. Templates de `referencias` con botón de verificación

**Fase 3 — Proceso y evaluación (Semana 5-6)**
11. Templates de `documentos` (lista + upload + verificación)
12. Templates de `visitas` (lista + formulario mobile-first)
13. Templates de `evaluacion` (formulario de scoring con totales JS)
14. Lógica de cambio de estado del estudio (vista dedicada + confirmación)

**Fase 4 — Sistema de soporte (Semana 7-8)**
15. Templates de `notificaciones` (lista + badge en navbar via HTMX)
16. Dashboard enriquecido con métricas y estudios recientes
17. Templates de `configuracion` (catálogos)
18. Implementar control de acceso por rol (grupos de Django)

**Fase 5 — Portal cliente y API (Semana 9-12)**
19. Portal de cliente (mi-estudio)
20. API REST con Django REST Framework (`apps/api`)
21. Sistema de auditoría (`apps/auditorias`)
22. Generación de reportes PDF (`apps/reportes`)

### 4.3 Colores de estado para badges (Tailwind)

```
BOR → gray    (bg-gray-100 text-gray-700)
VIS → blue    (bg-blue-100 text-blue-700)
PRO → yellow  (bg-yellow-100 text-yellow-700)
COM → indigo  (bg-indigo-100 text-indigo-700)
REV → purple  (bg-purple-100 text-purple-700)
APR → green   (bg-green-100 text-green-700)
REC → red     (bg-red-100 text-red-700)
CAN → gray    (bg-gray-200 text-gray-500)
```

**Colores de nivel de riesgo:**
```
BAJ → green   (bg-green-100 text-green-700)
MED → yellow  (bg-yellow-100 text-yellow-700)
ALT → orange  (bg-orange-100 text-orange-700)
CRI → red     (bg-red-100 text-red-700)
```

---

## 5. Guía para Otros Agentes

### 5.1 Convenciones de Código Obligatorias

**Idioma:**
- Todo texto de UI, verbose_name, help_text, choice labels: en **español mexicano**
- Nombres de variables, funciones y modelos: en **español**, excepto términos técnicos estándar de Django

**Campos de choices:**
```python
# CORRECTO: 3 caracteres en mayúsculas
ESTADO_ESTUDIO = [
    ('BOR', 'Borrador'),
    ('APR', 'Aprobado'),
]

# INCORRECTO:
('borrador', 'Borrador')   # minúsculas
('BORRADDR', 'Borrador')   # más de 3 chars
# EXCEPCIONES EXISTENTES: tipo_vivienda usa 'PROHIP' (6 chars) y
# patrimonio_inmobiliario usa 'NINGUNA', 'PROPIA', etc. — no seguir este patrón
```

**Herencia de modelos:**
```python
# SIEMPRE heredar TimestampModel para modelos de dominio
from apps.configuracion.models import TimestampModel

class MiModelo(TimestampModel):
    ...

# NO heredar si es catálogo simple (como TipoEstudio, NivelEducativo)
# NO heredar si es OneToOne obligatorio sin auditoría (como SituacionEconomica, EvaluacionRiesgo)
```

**Campos `_by` en vistas y admin:**
```python
# En toda vista CreateView o UpdateView, poblar campos _by:
def form_valid(self, form):
    form.instance.updated_by = self.request.user
    if not form.instance.pk:
        form.instance.created_by = self.request.user
    return super().form_valid(form)
```

**URLs y namespaces:**
```python
# Patrón de URL: app_name:modelo_accion
{% url 'personas:persona_list' %}
{% url 'estudios:estudio_detail' pk=estudio.pk %}
{% url 'documentos:documento_create' %}

# NUNCA hard-codear paths como '/personas/' en templates
```

**Templates — estructura mínima:**
```html
{% extends "base.html" %}

{% block title %}[Título] — Estudio Socioeconómico{% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
    <!-- contenido -->
</div>
{% endblock %}
```

---

### 5.2 Patrones Establecidos que NO Deben Romperse

1. **Folio de Persona:** `Persona.save()` genera el folio automáticamente. **Nunca** asignar `folio` manualmente ni hacerlo editable.

2. **Properties de SituacionEconomica:** `ingreso_total_mensual`, `egreso_total_mensual`, `capacidad_ahorro` son `@property`. **Nunca** intentar guardarlos como campos de BD.

3. **Cascadas de borrado:** Borrar una `Persona` elimina en cascada todos sus estudios, domicilios, laboral, educacion, idiomas, salud, familia, referencias y documentos. Proteger con confirmación obligatoria en UI.

4. **TipoEstudio con PROTECT:** No se puede borrar si hay estudios que lo referencian. Siempre usar `activo=False`.

5. **NivelEducativo con PROTECT:** Misma lógica — desactivar con `activo=False`, nunca borrar.

6. **Estado del estudio — sin transiciones automáticas:** Al implementar vistas de cambio de estado, agregar la validación de transiciones permitidas.

7. **Archivos de documentos:** El `FileField` en `Documento.archivo` necesita `MEDIA_ROOT` y `MEDIA_URL` configurados.

8. **Autenticación:** Todas las vistas deben estar protegidas con `LoginRequiredMixin`.

---

### 5.3 Qué No Debo Romper

| Componente | Riesgo | Mitigación |
|------------|--------|------------|
| `TimestampModel` en `configuracion` | Si se modifica, afecta todos los modelos | Solo agregar campos opcionales, nunca eliminar |
| `Persona.save()` — algoritmo de folio | Race condition en producción | Usar `select_for_update()` al escalar |
| `apps.configuracion` en `INSTALLED_APPS` primero | Resuelve dependencias de herencia | Mantener su posición en settings |
| Enum de choices de 3 chars | Existe en toda la BD | No cambiar valores, solo agregar nuevos |
| `app_name` en urls.py | Los namespaces están en uso | Mantener exactamente como están |

---

### 5.4 Puntos de Extensión Disponibles

1. **Roles de usuario:** Agregar `UserProfile` con FK a `auth.User` y campo `rol` (choices: ANA/CAM/CLI).
2. **Auditoría:** `apps/auditorias` está vacía. Implementar con `post_save` signals.
3. **API REST:** `apps/api` está vacía. Implementar con `djangorestframework`.
4. **Reportes:** `apps/reportes` está vacía. Usar `reportlab` (PDF) o `openpyxl` (Excel).
5. **Transiciones de estado formales:** Agregar método `transicionar(nuevo_estado, usuario)` a `EstudioSocioeconomico`.
6. **Notificaciones automáticas:** Conectar `post_save` signals en modelos clave.
7. **Configuración de archivos:** Agregar `MEDIA_ROOT` y `MEDIA_URL` a `settings.py`.
8. **Paginación:** Agregar `paginate_by = 25` a todas las ListViews.
9. **Búsqueda y filtros:** Agregar `get_queryset()` con filtrado por parámetros GET.
10. **HTMX parciales:** Crear views que retornen solo fragmentos HTML para operaciones inline.

---

## 6. Próximos Pasos Concretos

### 6.1 Lista Priorizada de Tareas

| # | Tarea | Complejidad | Dependencias | Impacto |
|---|-------|-------------|-------------|---------|
| 1 | Configurar `MEDIA_ROOT` y `MEDIA_URL` en settings | Baja | Ninguna | Desbloquea uploads |
| 2 | Agregar `LoginRequiredMixin` a todas las vistas stub | Baja | Ninguna | Seguridad crítica |
| 3 | Agregar `paginate_by = 25` a todas las ListViews | Baja | Ninguna | Performance |
| 4 | Poblar `created_by/updated_by` en form_valid() de todas las vistas | Baja | Ninguna | Integridad de datos |
| 5 | Templates de `personas` (list + detail + form + confirm) | Media | Tarea 4 | Funcionalidad base |
| 6 | Templates de `estudios` (list + detail con tabs) | Media | Tarea 5 | Funcionalidad base |
| 7 | Extender `base.html` con navbar completo y breadcrumbs | Media | Tarea 5 | UX |
| 8 | Templates de `documentos` con upload y verificación | Media | Tareas 5, 6 | Flujo crítico |
| 9 | Templates de `visitas` (mobile-first) | Media | Tarea 6 | Personal de campo |
| 10 | Templates de `evaluacion` con cálculo de score | Media | Tarea 6 | Flujo crítico |
| 11 | Vista de cambio de estado con validación de transiciones | Alta | Tareas 6, 10 | Máquina de estados |
| 12 | Templates de `laboral`, `referencias` con verificación inline | Media | Tarea 5 | Verificación |
| 13 | Templates de `domicilios`, `educacion`, `familia`, `idiomas` | Baja-Media | Tarea 5 | Completud |
| 14 | Dashboard enriquecido con métricas y KPIs | Alta | Tareas 5-13 | Gestión |
| 15 | Sistema de roles con `auth.Group` | Alta | Ninguna | Multi-perfil |
| 16 | Notificaciones automáticas con signals | Alta | Tarea 15 | Automatización |
| 17 | `apps/auditorias` — modelo y signals | Alta | Tarea 15 | Trazabilidad |
| 18 | `apps/api` — endpoints REST con DRF | Alta | Tareas 5-14 | Integraciones |
| 19 | `apps/reportes` — PDF/Excel | Alta | Tareas 5-14 | Entregables |
| 20 | Portal de cliente (acceso restringido por rol) | Alta | Tareas 15, 18 | Cliente final |
| 21 | Tests automatizados para modelos y vistas | Alta | Todo lo anterior | Calidad |
| 22 | Corrección de race condition en folio (`select_for_update`) | Media | Ninguna | Producción segura |

---

### 6.2 Detalles de Implementación para Tareas Críticas

#### Tarea 1 — MEDIA_ROOT (agregar a settings.py)
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

```python
# En esteconom/urls.py, agregar al final:
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

#### Tarea 11 — Método de transición de estado (agregar al modelo)
```python
# En apps/estudios/models.py
TRANSICIONES_VALIDAS = {
    'BOR': ['VIS', 'CAN'],
    'VIS': ['PRO', 'CAN'],
    'PRO': ['COM', 'CAN'],
    'COM': ['REV', 'CAN'],
    'REV': ['APR', 'REC', 'CAN'],
    'APR': [],
    'REC': [],
    'CAN': [],
}

def puede_transicionar(self, nuevo_estado):
    return nuevo_estado in TRANSICIONES_VALIDAS.get(self.estado, [])
```

#### Tarea 22 — Race condition en folio
```python
# En apps/personas/models.py — método save()
from django.db import transaction

def save(self, *args, **kwargs):
    if not self.folio:
        with transaction.atomic():
            year = timezone.now().strftime('%Y')
            month = timezone.now().strftime('%m')
            last = Persona.objects.select_for_update().filter(
                folio__startswith=f'{year}{month}'
            ).order_by('-folio').first()
            # ... resto del algoritmo
```

---

## Apéndice A — Registro de Campos no Estándar

Las siguientes son excepciones al estándar de 3 chars para choices:

| Modelo | Campo | Código | Chars |
|--------|-------|--------|-------|
| `Domicilio` | `tipo_vivienda` | `'PROHIP'` | 6 |
| `SituacionEconomica` | `patrimonio_inmobiliario` | `'NINGUNA'`, `'PROPIA'`, `'INVERSION'`, `'TERRENO'` | 5-8 |

---

## Apéndice B — Apps sin URL Configurada

Las siguientes apps están en `INSTALLED_APPS` pero **NO** tienen entrada en `esteconom/urls.py`:

- `apps.auditorias`
- `apps.reportes`
- `apps.api`

Al implementarlas, agregar en `esteconom/urls.py`:
```python
path('api/', include('apps.api.urls')),
path('reportes/', include('apps.reportes.urls')),
# auditorias generalmente no requiere URLs propias (es backend)
```

---

## Apéndice C — Variables de Entorno Requeridas

| Variable | Requerida | Default | Descripción |
|----------|-----------|---------|-------------|
| `SECRET_KEY` | Si | — | Clave secreta Django |
| `DEBUG` | No | `False` | Modo depuración |
| `ALLOWED_HOSTS` | No | `localhost` | Hosts permitidos (CSV) |
| `DATABASE_URL` | No | SQLite local | URL de conexión PostgreSQL |

Archivo `.env` de ejemplo:
```env
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
# DATABASE_URL=postgres://user:pass@localhost:5432/estudioeconom
```

---

## Apéndice D — Formulario de Referencia (Meraki)

El formulario Google Forms de Meraki (Evaluación Socioeconómica) es la fuente de datos que este sistema digitaliza. Todos los campos del formulario están cubiertos por los modelos actuales.

**URL del formulario:**
https://docs.google.com/forms/d/e/1FAIpQLSc75Ncb7ON5zEtl2m8kBHuH971DDD7VGQREtdRfVz_qIXA5dA/viewform

**Mapeo secciones → modelos:**

| Sección del formulario | Modelo(s) Django |
|------------------------|-----------------|
| Datos personales básicos | `Persona` |
| Documentos de identificación | `Persona` (nss, licencia, cartilla, acta, ine, curp, rfc) |
| Domicilio y características del inmueble | `Domicilio` |
| Estudios y certificaciones | `Educacion`, `Idioma` |
| Salud | `SaludPersona` |
| Grupo familiar | `GrupoFamiliar` |
| Situación económica e ingresos | `SituacionEconomica` |
| Automóvil y patrimonio | `SituacionEconomica` |
| Referencias personales | `Referencia` |
| Historial laboral | `HistorialLaboral` |
| Contexto de la solicitud | `EstudioSocioeconomico` (expectativas, medio_enterado, traslado) |

---

*Documento actualizado por Claude Code el 2026-02-21.*
*Versión 1.1 — refleja todos los modelos implementados incluyendo los nuevos campos derivados del análisis del formulario Meraki.*
