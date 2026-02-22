# Plan de Implementación — EstudioEcoNom (Meraki)

**Versión:** 1.1
**Fecha:** 2026-02-21
**Objetivo:** Digitalizar el proceso de estudio socioeconómico de Meraki Consultoría generando un reporte PDF idéntico al formato actual, soportando dos escenarios de captura de datos.

---

## Dos escenarios de operación

```
┌─────────────────────────────────────────────────────────┐
│  ESCENARIO A — Autogestión del candidato                │
│                                                         │
│  Analista crea estudio → genera link con token →        │
│  Candidato llena portal desde su celular →              │
│  Sube fotos y documentos →                              │
│  Analista revisa, complementa y genera PDF              │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  ESCENARIO B — Inspector en campo                       │
│                                                         │
│  Analista crea estudio y agenda visita →                │
│  Inspector va al domicilio (app mobile-first) →         │
│  Toma fotos, captura GPS, evalúa entorno →              │
│  Hace llamadas a referencias y jefes →                  │
│  Analista revisa y genera PDF                           │
└─────────────────────────────────────────────────────────┘
```

---

## Estructura del reporte PDF de referencia

El reporte final consta de 8 páginas:

| Pág. | Sección | Datos |
|------|---------|-------|
| 1 | Portada + foto + Comentarios y conclusiones | Header empresa, folio, fechas, narrativo |
| 2 | Datos personales + Identificaciones + Datos escolares | Persona, documentos oficiales, Educacion |
| 3 | Hábitos y salud + Familiares directos | SaludPersona, GrupoFamiliar |
| 4 | Datos del inmueble + Patrimonio + Situación económica | Domicilio, SituacionEconomica |
| 5 | Referencias + Comentarios de colonos + Observaciones | Referencia, VisitaDomiciliaria |
| 6 | Croquis de domicilio (mapa estático) | GPS de VisitaDomiciliaria |
| 7-8 | Fotografías del domicilio (fachada e interior) | Documento tipo FOT |

---

## FASE 0 — Completar modelos (base de datos al 100%)

**Estado:** ✅ Completada
**Prioridad:** 🔴 Crítico
**Dependencias:** Ninguna

### Objetivo
Alinear completamente la base de datos con el reporte PDF de referencia. Los modelos actuales están incompletos para generar el reporte final.

### Campos faltantes detectados en el PDF

**`apps/referencias/models.py` — modelo `Referencia`:**
- [x] `actividad_tiempo_libre` — TextField, blank — Qué hace la referencia en su tiempo libre
- [x] `lugares_laborado` — TextField, blank — Donde ha trabajado la referencia
- [x] `conducta` — TextField, blank — Descripción de conducta
- [x] `cualidades` — TextField, blank — Cualidades destacadas

**`apps/visitas/models.py` — modelo `VisitaDomiciliaria`:**
- [x] `comentarios_colonos` — TextField, blank — Comentarios de vecinos al momento de visita

**`apps/estudios/models.py` — modelo `EstudioSocioeconomico`:**
- [x] `aspectos_positivos` — TextField, blank — Aspectos positivos del candidato
- [x] `aspectos_negativos` — TextField, blank — Aspectos negativos del candidato

**`apps/domicilios/models.py` — modelo `Domicilio`:**
- [x] `observaciones_inmueble` — TextField, blank — Observaciones y comentarios del inmueble

### Nuevo modelo: `EmpresaCliente`

El reporte incluye el logo y nombre de la empresa que contrató el estudio (p. ej. Hutchison Ports LCT). Creado en `apps/configuracion/`.

- [x] Crear modelo `EmpresaCliente` (nombre, logo, activo, created_at)
- [x] Agregar FK `empresa_cliente` (null=True) a `EstudioSocioeconomico`
- [x] Registrar en admin con upload de logo

### Nuevo modelo: `EstudioToken` (para Escenario A)

- [x] Crear modelo `EstudioToken` en `apps/estudios/` (token UUID, activo, fecha_expiracion, vigente property)
- [x] Registrar en admin

### Tareas de esta fase
- [x] Modificar modelos con campos faltantes
- [x] Ejecutar `makemigrations && migrate`
- [x] Actualizar admin de `referencias`, `visitas`, `estudios`, `domicilios`, `configuracion`
- [x] Instalar Pillow (requerido por ImageField)
- [ ] Actualizar `CONTEXT.md` con los nuevos campos (pendiente)

---

## FASE 1 — Base de templates y autenticación

**Estado:** ✅ Completada (componentes opcionales pendientes)
**Prioridad:** 🔴 Crítico
**Dependencias:** FASE 0

### Objetivo
Sistema funcional con autenticación, navegación y estructura visual base.

### Configuración técnica
- [x] Agregar `MEDIA_ROOT = BASE_DIR / 'media'` y `MEDIA_URL = 'media/'` a `settings.py`
- [x] Agregar `STATIC_ROOT = BASE_DIR / 'staticfiles'` a `settings.py`
- [x] Agregar URL de media en `esteconom/urls.py` (solo cuando `DEBUG=True`)
- [x] Crear `apps/estudios/urls_candidato.py` (placeholder para Escenario A)
- [x] Instalar HTMX en `base.html`: `<script src="https://unpkg.com/htmx.org@1.9.12"></script>`
- [x] Agregar `paginate_by = 25` a todas las `ListView` (13 apps)
- [x] Agregar `LoginRequiredMixin` a todas las vistas (13 apps)
- [x] Implementar patrón `form_valid()` con `created_by` / `updated_by` en todas las CreateView/UpdateView
- [x] Actualizar `fields` en vistas para incluir todos los nuevos campos de modelos

### Templates base
- [x] `base.html` — Layout principal con:
  - Navbar: logo Meraki, menú de navegación, badge de notificaciones, usuario activo, logout
  - Breadcrumbs (slot via `{% block breadcrumbs %}`)
  - Área de mensajes Django (`messages`)
  - Footer
  - HTMX cargado
  - Tailwind CSS via CDN
- [x] `registration/login.html` — Página standalone de login con diseño Meraki (sin extends)
- [x] `home.html` — Dashboard con:
  - Contador de estudios por estado (tarjetas con colores)
  - Accesos rápidos: Nueva persona, Nuevo estudio, Registrar visita
  - Grid de módulos del sistema
- [x] `HomeView` en `esteconom/urls.py` con context de estadísticas (total_personas, total_estudios, estudios_en_proceso, estudios_aprobados)

### Componentes reutilizables (`templates/components/`)
- [ ] `badge_estado.html` — Badge de color según estado del estudio
- [ ] `badge_riesgo.html` — Badge según nivel de riesgo
- [ ] `pagination.html` — Paginación Tailwind
- [ ] `form_field.html` — Campo con label + error
- [ ] `confirm_modal.html` — Modal de confirmación (HTMX)
- [ ] `empty_state.html` — Estado vacío para listas sin resultados
- [ ] `card_persona.html` — Tarjeta resumen de persona
- [ ] `notif_badge.html` — Badge de notificaciones no leídas

---

## FASE 2 — Expediente del candidato (panel analista)

**Estado:** ⬜ Pendiente
**Prioridad:** 🔴 Crítico
**Dependencias:** FASE 1

### Objetivo
Permitir al analista capturar y gestionar el expediente completo desde el sistema interno.

### Templates de `personas`
- [ ] `persona_list.html` — Tabla paginada con búsqueda por folio/nombre/CURP
- [ ] `persona_detail.html` — Vista hub con pestañas: Datos, Documentos, Estudios
- [ ] `persona_form.html` — Formulario creación/edición (shared create+update)
- [ ] `persona_confirm_delete.html` — Confirmación de borrado con advertencia de cascada

### Templates de `estudios`
- [ ] `estudio_list.html` — Lista con filtros por estado (tabs o badges), búsqueda
- [ ] `estudio_detail.html` — Vista hub con pestañas:
  - Resumen general
  - Domicilio
  - Educación / Idiomas
  - Salud
  - Familia
  - Laboral
  - Económico
  - Visitas
  - Documentos
  - Evaluación
- [ ] `estudio_form.html` — Crear/editar estudio
- [ ] `estudio_estado.html` (partial HTMX) — Cambio de estado con confirmación

### Templates de datos relacionados (desde detalle del estudio/persona)
- [ ] `domicilios/domicilio_form.html`
- [ ] `educacion/educacion_form.html` + `idioma_form.html`
- [ ] `salud/saludpersona_form.html`
- [ ] `familia/grupofamiliar_form.html`
- [ ] `laboral/historiallaboral_form.html` + botón verificar (HTMX)
- [ ] `referencias/referencia_form.html` + botón verificar (HTMX)
- [ ] `economia/situacioneconomica_form.html`
- [ ] `evaluacion/evaluacionriesgo_form.html` — con cálculo de score_final en JS

### Templates de `documentos`
- [ ] `documento_list.html` — Bandeja de documentos pendientes de verificar
- [ ] `documento_form.html` — Upload con preview
- [ ] Botón "Marcar verificado" inline (HTMX)

### Lógica de cambio de estado
- [ ] Vista `CambiarEstadoView` con validación de `TRANSICIONES_VALIDAS`
- [ ] Modal de confirmación con campo de observación
- [ ] Bloqueo visual de botones según estado actual

---

## FASE 3 — Portal público de autogestión (Escenario A)

**Estado:** ⬜ Pendiente
**Prioridad:** 🟠 Alto
**Dependencias:** FASE 0, FASE 1

### Objetivo
Link único con token que el candidato abre desde su celular para llenar su propio estudio, sin necesidad de crear una cuenta.

### URL del portal
```
/candidato/<uuid:token>/          → página de bienvenida
/candidato/<uuid:token>/paso/<n>/ → cada paso del wizard
/candidato/<uuid:token>/gracias/  → confirmación de envío
```

### Wizard multi-paso (7 pasos, mobile-first)

| Paso | Contenido | Modelo(s) |
|------|-----------|-----------|
| 1 | Datos personales e identificaciones | `Persona` |
| 2 | Domicilio y características del inmueble | `Domicilio` |
| 3 | Educación, idiomas y salud | `Educacion`, `Idioma`, `SaludPersona` |
| 4 | Grupo familiar (todos los que viven en casa) | `GrupoFamiliar` |
| 5 | Situación económica y patrimonio | `SituacionEconomica` |
| 6 | Referencias personales (mínimo 3) | `Referencia` |
| 7 | Historial laboral + subida de foto y documentos | `HistorialLaboral`, `Documento` |

### Funcionalidades del portal
- [ ] Acceso sin login — validación solo por token UUID
- [ ] Validación de token: expirado, ya completado, inválido
- [ ] Barra de progreso visual entre pasos
- [ ] Guardado automático al avanzar cada paso (el candidato puede retomar)
- [ ] Upload de foto desde cámara del celular (retrato, fachada, interior)
- [ ] Formularios adaptativos mobile-first (inputs grandes, teclado numérico donde aplique)
- [ ] Página de confirmación al completar: mensaje de éxito + marcar `EstudioToken.activo=False`
- [ ] Notificación automática al analista cuando el candidato completa el formulario

### Vista del analista para gestionar tokens
- [ ] Botón "Generar link para candidato" en detalle del estudio
- [ ] Mostrar link generado con botón de copiar
- [ ] Indicador de estado: Pendiente / Completado / Expirado
- [ ] Botón para regenerar token (invalida el anterior)

---

## FASE 4 — App del inspector en campo (Escenario B)

**Estado:** ⬜ Pendiente
**Prioridad:** 🟠 Alto
**Dependencias:** FASE 1, FASE 2

### Objetivo
Interfaz mobile-first para que el inspector registre la visita domiciliaria, capture fotos y verifique referencias por teléfono.

### Agenda del inspector
- [ ] `visitas/agenda.html` — Lista de visitas asignadas al usuario actual:
  - Fecha y hora, nombre del candidato, dirección, estado
  - Ordenadas por fecha ascendente
  - Botón "Iniciar visita" que abre el formulario de reporte

### Formulario de reporte de visita (mobile-first)
- [ ] `visitas/reporte_form.html` — Secciones:
  - **Ubicación:** Captura GPS automática al abrir (API Geolocation del navegador)
  - **Verificación:** ¿Se encontró a la persona? ¿El domicilio coincide?
  - **Distribución del inmueble:** Checkboxes (sala, cocina, comedor, patio, cochera, cuartos)
  - **Servicios:** Checkboxes (agua, luz, drenaje, gas, internet, cable, pavimentación, teléfono)
  - **Materiales:** Checkboxes (piso, enjarre, loza, techo lámina, etc.)
  - **Condición:** Radio buttons Orden/Limpieza/Mantenimiento (Bueno/Regular/Malo)
  - **Entorno:** Sliders 1-5 para seguridad, ruido, acceso a transporte, tipo de zona
  - **Observaciones:** Textarea
  - **Comentarios de colonos:** Textarea

### Upload de fotos en campo
- [ ] Captura directa desde cámara del celular (input `capture="camera"`)
- [ ] Preview inmediato de la foto antes de guardar
- [ ] Categorías: Retrato del candidato, Fachada (1-3 fotos), Interior (1-3 fotos)
- [ ] Guardado como `Documento` con tipo `FOT`

### Verificación telefónica de referencias
- [ ] Vista `referencias/verificar_form.html`:
  - Mostrar datos de la referencia (nombre, teléfono, relación)
  - Campos de resultado: conducta, cualidades, actividad tiempo libre, lugares laborados
  - Botón "Marcar verificada" → guarda `verificada=True` + `fecha_verificacion`
- [ ] Lista de referencias pendientes de verificar en el detalle del estudio

### Verificación telefónica de historial laboral
- [ ] Vista `laboral/verificar_form.html`:
  - Mostrar datos del empleo (empresa, puesto, jefe, teléfono)
  - Campos de resultado: calificación del jefe, ¿recontratable?, desempeño
  - Botón "Marcar verificada"

---

## FASE 5 — Generación del reporte PDF

**Estado:** ⬜ Pendiente
**Prioridad:** 🟠 Alto
**Dependencias:** FASE 2, FASE 3 o FASE 4

### Objetivo
Generar el PDF final idéntico al formato de referencia de Meraki.

### Stack técnico
- **Librería:** `WeasyPrint` (renderiza HTML+CSS a PDF, soporta imágenes y tablas complejas)
- **Mapa:** OpenStreetMap Static Maps API (gratuito) o Google Maps Static API
- **Instalación:** `pip install weasyprint Pillow`

### Estructura del template HTML del reporte
```
templates/reportes/
├── estudio_pdf.html        ← template principal (hereda el layout)
├── _pdf_header.html        ← logo empresa + nombre candidato + fechas + folio
├── _pdf_portada.html       ← foto candidato + comentarios y conclusiones
├── _pdf_datos_personales.html
├── _pdf_salud_familia.html
├── _pdf_inmueble_economia.html
├── _pdf_referencias.html
├── _pdf_croquis.html       ← mapa estático
└── _pdf_fotos.html         ← galería de fotografías
```

### Vista de generación
- [ ] `GenerarReportePDFView` — protegida (solo analistas)
- [ ] Botón "Generar PDF" en detalle del estudio (solo visible en estados COM/REV/APR/REC)
- [ ] Vista previa antes de descargar (renderizado en nueva pestaña)
- [ ] Descarga directa como `Estudio_<folio>_<fecha>.pdf`

### Tareas técnicas
- [ ] Instalar `WeasyPrint` y agregar a `requirements.txt`
- [ ] Crear template HTML del reporte con CSS para impresión (A4, márgenes)
- [ ] Implementar generación del mapa estático a partir de coordenadas GPS
- [ ] Campo editable "Comentarios y Conclusiones" (el analista lo escribe antes de exportar)
- [ ] Header del reporte: logo de `EmpresaCliente`, nombre candidato, fechas, folio
- [ ] Manejo de datos faltantes: mostrar "N/A" cuando no hay información

---

## FASE 6 — Notificaciones y flujo automatizado

**Estado:** ⬜ Pendiente
**Prioridad:** 🟡 Medio
**Dependencias:** FASE 2

### Objetivo
Automatizar las notificaciones internas y el flujo de estados del estudio.

### Tareas
- [ ] Implementar `transicionar(nuevo_estado, usuario)` en `EstudioSocioeconomico` con validación de `TRANSICIONES_VALIDAS`
- [ ] `post_save` signal en `EstudioSocioeconomico` → crear `Notificacion` al cambiar estado
- [ ] `post_save` signal → notificar al analista cuando el candidato completa el portal
- [ ] Templates de `notificaciones`: lista paginada, marcar como leída (HTMX)
- [ ] Badge dinámico en navbar (HTMX polling cada 30 segundos)
- [ ] Envío de email con `send_mail` en estados críticos (APR, REC)

---

## FASE 7 — Roles y control de acceso

**Estado:** ⬜ Pendiente
**Prioridad:** 🟡 Medio
**Dependencias:** FASE 2

### Objetivo
Diferenciar el acceso y las funcionalidades según el rol del usuario en el sistema.

### Roles del sistema

| Código | Rol | Acceso |
|--------|-----|--------|
| `ANA` | Analista | Panel completo, generación de PDF, aprobación/rechazo |
| `INS` | Inspector | Solo agenda de visitas + app de campo |

> El **candidato** no tiene cuenta en el sistema — accede solo via token público.

### Modelo `PerfilUsuario`
```python
class PerfilUsuario(models.Model):
    usuario = OneToOneField(User, CASCADE, related_name='perfil')
    ROL = [('ANA', 'Analista'), ('INS', 'Inspector')]
    rol = CharField(max_length=3, choices=ROL)
    foto = ImageField(upload_to='perfiles/', null=True, blank=True)
```

### Tareas
- [ ] Crear modelo `PerfilUsuario` en nueva app `apps/usuarios/` o en `apps/configuracion/`
- [ ] Crear `RolRequeridoMixin` para proteger vistas por rol
- [ ] Redireccionamiento post-login: `ANA` → dashboard, `INS` → agenda
- [ ] Panel de administración de usuarios con asignación de rol y foto
- [ ] Señal `post_save` en `User` para crear `PerfilUsuario` automáticamente

---

## Dependencias técnicas adicionales a instalar

```bash
pip install weasyprint        # Generación de PDF desde HTML
pip install Pillow            # Manejo de imágenes (ya instalado)
pip install django-crispy-forms tailwind  # Formularios con Tailwind (opcional)
```

Agregar al `requirements.txt`:
```
weasyprint
Pillow
```

---

## Resumen del estado del plan

| Fase | Nombre | Prioridad | Estado |
|------|--------|-----------|--------|
| 0 | Completar modelos | 🔴 Crítico | ✅ Completada |
| 1 | Base de templates y auth | 🔴 Crítico | ✅ Completada |
| 2 | Expediente del candidato (analista) | 🔴 Crítico | ⬜ Pendiente |
| 3 | Portal público de autogestión | 🟠 Alto | ⬜ Pendiente |
| 4 | App del inspector en campo | 🟠 Alto | ⬜ Pendiente |
| 5 | Generación del reporte PDF | 🟠 Alto | ⬜ Pendiente |
| 6 | Notificaciones y flujo automatizado | 🟡 Medio | ⬜ Pendiente |
| 7 | Roles y control de acceso | 🟡 Medio | ⬜ Pendiente |

---

*Plan elaborado el 2026-02-21. Actualizado el 2026-02-21 tras completar Fase 0 y Fase 1.*
*Basado en el reporte PDF de referencia (Meraki Consultoría) y el análisis del formulario Google Forms de Meraki.*
