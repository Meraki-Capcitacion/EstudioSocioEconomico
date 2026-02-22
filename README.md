# EstudioEcoNom — Sistema de Gestión de Estudios Socioeconómicos

Sistema web para digitalizar y gestionar el proceso de estudios socioeconómicos de **Meraki Consultoría**. Permite capturar el expediente completo de un candidato, coordinar visitas domiciliarias, verificar referencias y generar el reporte PDF final.

---

## Tecnologías

| Capa | Tecnología |
|---|---|
| Backend | Django 6.0.2 · Python 3.12 |
| Base de datos | SQLite (desarrollo) · PostgreSQL (producción) |
| Frontend | Tailwind CSS v3 (CDN) · HTMX 1.9.12 |
| Configuración | `python-decouple` · `dj-database-url` |
| Imágenes | Pillow |
| Idioma / TZ | `es-mx` · `America/Mexico_City` |

---

## Requisitos previos

- Python 3.12+
- Git
- (Opcional) PostgreSQL si no se usa SQLite

---

## Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd estudio_socioeconomico
```

### 2. Crear y activar el entorno virtual

```bash
python -m venv .venvEstudioEcoNom
source .venvEstudioEcoNom/bin/activate   # Linux / macOS
.venvEstudioEcoNom\Scripts\activate      # Windows
```

### 3. Instalar dependencias

```bash
pip install django==6.0.2 python-decouple dj-database-url psycopg2-binary Pillow
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
SECRET_KEY=cambia-esta-clave-por-una-segura
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Opcional — si no se define, usa SQLite
# DATABASE_URL=postgres://usuario:password@localhost:5432/estudioeconom
```

### 5. Aplicar migraciones y crear superusuario

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Iniciar el servidor de desarrollo

```bash
python manage.py runserver
```

Accede en: [http://localhost:8000](http://localhost:8000)
Panel de administración: [http://localhost:8000/admin](http://localhost:8000/admin)

---

## Comandos de desarrollo

```bash
# Activar el entorno virtual
source .venvEstudioEcoNom/bin/activate

# Servidor de desarrollo
python manage.py runserver

# Crear y aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# Ejecutar todos los tests
python manage.py test

# Tests de una app específica
python manage.py test apps.personas
python manage.py test apps.estudios.tests.TestClassName.test_method

# Shell de Django
python manage.py shell

# Recolectar archivos estáticos (producción)
python manage.py collectstatic
```

---

## Estructura del proyecto

```
estudio_socioeconomico/
├── esteconom/              # Configuración del proyecto Django
│   ├── settings.py
│   ├── urls.py             # Enrutador principal
│   └── wsgi.py / asgi.py
│
├── apps/                   # 16 apps de dominio
│   ├── configuracion/      # TimestampModel base + catálogos
│   ├── personas/           # Entidad central: Persona + SaludPersona
│   ├── estudios/           # Nodo hub: EstudioSocioeconomico (máquina de estados)
│   ├── domicilios/         # Dirección y características de vivienda
│   ├── economia/           # Situación económica (ingresos, egresos, patrimonio)
│   ├── educacion/          # Historial educativo + idiomas
│   ├── laboral/            # Historial laboral con flujo de verificación
│   ├── familia/            # Grupo familiar y dependencia económica
│   ├── referencias/        # Referencias personales con verificación
│   ├── visitas/            # Visitas domiciliarias con GPS
│   ├── evaluacion/         # Scoring de riesgo (6 categorías)
│   ├── documentos/         # Gestión documental con verificación
│   ├── notificaciones/     # Notificaciones internas del sistema
│   ├── auditorias/         # Placeholder — log de cambios
│   ├── reportes/           # Placeholder — generación de PDF
│   └── api/                # Placeholder — endpoints REST
│
├── templates/              # Templates HTML
│   ├── base.html
│   ├── home.html
│   ├── registration/
│   └── components/         # Componentes reutilizables
│
├── static/                 # Archivos estáticos
├── media/                  # Archivos subidos por usuarios (creado automáticamente)
├── implementacion/         # Plan de implementación por fases
├── CONTEXT.md              # Documentación técnica completa de la arquitectura
├── CLAUDE.md               # Guía para el agente de IA
└── manage.py
```

---

## Flujo de estados del estudio

```
BOR (Borrador) → VIS (Visita programada) → PRO (En proceso)
                                               ↓
                                          COM (Completado)
                                               ↓
                                          REV (En revisión)
                                          ↙           ↘
                                    APR (Aprobado)  REC (Rechazado)

Desde cualquier estado → CAN (Cancelado)
```

---

## Escenarios de operación

**Escenario A — Autogestión del candidato**
1. El analista crea el estudio y genera un link con token único
2. El candidato llena el portal desde su celular (sin cuenta)
3. Sube fotos y documentos
4. El analista revisa, complementa y genera el PDF

**Escenario B — Inspector en campo**
1. El analista crea el estudio y agenda una visita
2. El inspector va al domicilio (interfaz mobile-first)
3. Captura fotos, GPS y evalúa el entorno
4. Verifica referencias y empleo por teléfono
5. El analista revisa y genera el PDF

---

## Roles del sistema

| Rol | Descripción |
|---|---|
| **Analista** | Panel completo, gestión de estudios, aprobación/rechazo, generación de PDF |
| **Inspector** | Solo agenda de visitas y app de campo |
| **Candidato** | Acceso exclusivo por token público, sin cuenta en el sistema |

---

## Módulos principales

| URL | Módulo |
|---|---|
| `/` | Dashboard con estadísticas |
| `/personas/` | Gestión de candidatos |
| `/estudios/` | Estudios socioeconómicos |
| `/domicilios/` | Domicilios y vivienda |
| `/laboral/` | Historial laboral |
| `/educacion/` | Educación e idiomas |
| `/familia/` | Grupo familiar |
| `/referencias/` | Referencias personales |
| `/economia/` | Situación económica |
| `/visitas/` | Visitas domiciliarias |
| `/evaluacion/` | Evaluación de riesgo |
| `/documentos/` | Documentos digitalizados |
| `/notificaciones/` | Notificaciones internas |
| `/admin/` | Panel de administración Django |

---

## Estado de implementación

| Fase | Descripción | Estado |
|---|---|---|
| 0 | Modelos de base de datos | ✅ Completada |
| 1 | Templates base y autenticación | ✅ Completada |
| 2 | Expediente del candidato (panel analista) | ✅ Completada |
| 3 | Portal público de autogestión (candidato) | ⬜ Pendiente |
| 4 | App del inspector en campo | ⬜ Pendiente |
| 5 | Generación del reporte PDF | ⬜ Pendiente |
| 6 | Notificaciones y flujo automatizado | ⬜ Pendiente |
| 7 | Roles y control de acceso | ⬜ Pendiente |

---

## Documentación adicional

- [`CONTEXT.md`](./CONTEXT.md) — Arquitectura detallada, modelos, relaciones y guía técnica
- [`implementacion/01_plan_de_implementacion.md`](./implementacion/01_plan_de_implementacion.md) — Plan de implementación por fases con checklist de tareas

---

## Contribución

Este proyecto sigue las convenciones definidas en `CLAUDE.md` y `CONTEXT.md`:

- Todo el código y textos de UI en **español mexicano**
- Modelos de dominio heredan de `TimestampModel` (campos `created_by` / `updated_by`)
- Vistas protegidas con `LoginRequiredMixin`
- Campos `choices` de 3 caracteres en mayúsculas (p. ej. `'BOR'`, `'APR'`)
- Nunca asignar `Persona.folio` manualmente — se autogenera en `save()`
- Siempre poblar `created_by` y `updated_by` en `form_valid()`
