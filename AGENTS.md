# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Django application for managing socioeconomic studies (estudios socioeconómicos) in Mexican Spanish (`es-mx`, timezone `America/Mexico_City`). Tracks persons, their financial situation, employment history, education, family, references, home visits, risk evaluations, and document verification.

## Development Commands

```bash
# Activate virtual environment
source .venvEstudioEcoNom/bin/activate

# Run development server
python manage.py runserver

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Run all tests
python manage.py test

# Run tests for a specific app or method
python manage.py test apps.personas
python manage.py test apps.estudios.tests.TestClassName.test_method_name

# Create admin user
python manage.py createsuperuser
```

## Architecture

### Project Layout

- `esteconom/` — Django project configuration (settings, urls, wsgi/asgi). Settings module: `esteconom.settings`.
- `apps/` — 16 domain-specific Django apps, all registered in `INSTALLED_APPS` as `apps.<name>`.
- `templates/` — Project-level templates. `base.html` uses Tailwind CSS via CDN. App templates go under `templates/<app_name>/`.

### Entity Relationships

`Persona` is the central entity. Most domain models relate to it via ForeignKey. `EstudioSocioeconomico` links a `Persona` to a `TipoEstudio` and serves as the parent for one-to-one models (`SituacionEconomica`, `EvaluacionRiesgo`) and one-to-many models (`VisitaDomiciliaria`, `Documento`, `Notificacion`).

Other models (`Domicilio`, `HistorialLaboral`, `Educacion`, `GrupoFamiliar`, `Referencia`) link directly to `Persona`.

### Key Patterns

**TimestampModel** (`apps/configuracion/models.py`): Abstract base inherited by nearly all models. Provides `created_at`, `updated_at`, `created_by`, `updated_by` fields. Always populate the `_by` fields when creating/updating records.

**EstudioSocioeconomico state machine**: `BOR` (Borrador) → `VIS` (Visita Programada) → `PRO` (En Proceso) → `COM` (Completado) → `REV` (En Revisión) → `APR`/`REC`/`CAN` (Aprobado/Rechazado/Cancelado).

**Computed properties in `SituacionEconomica`**: `ingreso_total_mensual`, `egreso_total_mensual`, `capacidad_ahorro` are `@property` methods that sum stored fields — not stored in the database.

**Verification workflows**: `HistorialLaboral`, `Referencia`, and `Documento` all have `verificado`/`verificada` boolean flags with associated `fecha_verificacion` timestamps.

**Folio auto-generation**: `Persona.save()` generates a unique folio in `YYYYMMNNNNN` format (e.g. `2026020001`). The `folio` field is `editable=False`.

**URL naming convention**: Each app uses `<model_lower>_list`, `<model_lower>_create`, `<model_lower>_detail`, `<model_lower>_update`, `<model_lower>_delete` (e.g. `persona_list`, `persona_create`). URL namespaces match app names.

**Catalog models**: `TipoEstudio` and `NivelEducativo` are catalog/lookup tables with `activo` flags and `orden` fields for sorting.

### Configuration

Environment variables via `python-decouple` from `.env`:
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DATABASE_URL`
- SQLite by default; PostgreSQL via `dj_database_url` when `DATABASE_URL` is set

Authentication uses Django's built-in `django.contrib.auth` with session-based login. `LOGIN_URL = 'login'`, `LOGIN_REDIRECT_URL = '/'`, `LOGOUT_REDIRECT_URL = 'login'`.

### Current Status

Models and admin registrations are fully designed. Views are mostly ListView stubs. URL routing is wired for all apps with CRUD patterns. Templates, REST API (`apps/api`), audit logging (`apps/auditorias`), and report generation (`apps/reportes`) are placeholders ready for implementation.

### Conventions

- All model fields, verbose names, choice labels, and UI text must be in Mexican Spanish.
- Use 3-character uppercase codes for choice fields (e.g. `'BOR'`, `'INE'`, `'SOL'`).
- Frontend uses Tailwind CSS via CDN (`<script src="https://cdn.tailwindcss.com">`). Templates extend `templates/base.html`.
