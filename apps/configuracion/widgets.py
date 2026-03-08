"""
Widget de arrastrar y soltar para seleccionar y ordenar secciones de TipoEstudio.

Renderiza dos columnas gestionadas con SortableJS (CDN):
  - Izquierda  "Incluidas": secciones activas, en el orden guardado.
  - Derecha "Disponibles": secciones no incluidas.

Las secciones en SECCIONES_OBLIGATORIAS ('candidato', 'evaluacion') solo
pueden reordenarse dentro de la columna izquierda; no pueden moverse a
la derecha.

El estado se persiste en un <input type="hidden"> como JSON de códigos de
sección, p. ej. '["candidato","domicilios","evaluacion"]'.
"""

import json

from django import forms
from django.utils.safestring import mark_safe


# ---------------------------------------------------------------------------
# Constantes compartidas con el modelo (se duplican aquí para evitar import
# circular; el widget se importa desde admin.py antes que los modelos reales).
# ---------------------------------------------------------------------------
_SECCIONES_DISPONIBLES = [
    ('candidato',   'Portal del Candidato'),
    ('domicilios',  'Domicilio'),
    ('educacion',   'Educación e Idiomas'),
    ('salud',       'Salud'),
    ('laboral',     'Historial Laboral'),
    ('familia',     'Grupo Familiar'),
    ('referencias', 'Referencias'),
    ('economia',    'Situación Económica'),
    ('visitas',     'Visita Domiciliaria'),
    ('evaluacion',  'Evaluación de Riesgo'),
    ('documentos',  'Documentos'),
]
_SECCIONES_OBLIGATORIAS = frozenset({'candidato', 'evaluacion'})

# Lookup rápido código → etiqueta
_LABEL = {codigo: etiqueta for codigo, etiqueta in _SECCIONES_DISPONIBLES}
_TODOS_LOS_CODIGOS = [c for c, _ in _SECCIONES_DISPONIBLES]


# ---------------------------------------------------------------------------
# Helper: construir un <li> para un ítem de la lista
# ---------------------------------------------------------------------------
def _render_item(codigo: str, *, locked: bool) -> str:
    etiqueta = _LABEL.get(codigo, codigo)

    if locked:
        item_style = (
            "display:flex;align-items:center;gap:8px;"
            "padding:10px 14px;margin:4px 0;border-radius:6px;"
            "background:#2a2060;border:1px solid #7B6BAF;"
            "color:#c8bfee;cursor:default;user-select:none;"
        )
        icon_html = (
            '<span title="Sección obligatoria" style="font-size:14px;opacity:.8;">'
            '&#x1F512;</span>'
        )
        label_html = f'<span style="flex:1;font-size:13px;">{etiqueta}</span>'
        badge_html = (
            '<span style="font-size:10px;padding:2px 6px;border-radius:10px;'
            'background:#4a3a8a;color:#a99fcc;">obligatoria</span>'
        )
        return (
            f'<li data-codigo="{codigo}" data-locked="1" style="{item_style}">'
            f'{icon_html}{label_html}{badge_html}'
            f'</li>'
        )

    item_style = (
        "display:flex;align-items:center;gap:8px;"
        "padding:10px 14px;margin:4px 0;border-radius:6px;"
        "background:#1e1e2e;border:1px solid #3a3a5a;"
        "color:#e0daf5;cursor:grab;"
    )
    handle_html = (
        '<span class="sortable-handle" '
        'style="color:#7B6BAF;font-size:16px;line-height:1;cursor:grab;" '
        'title="Arrastrar">&#8942;&#8942;</span>'
    )
    label_html = f'<span style="flex:1;font-size:13px;">{etiqueta}</span>'
    return (
        f'<li data-codigo="{codigo}" style="{item_style}">'
        f'{handle_html}{label_html}'
        f'</li>'
    )


# ---------------------------------------------------------------------------
# Widget principal
# ---------------------------------------------------------------------------
class SeccionesWidget(forms.Widget):
    """
    Widget de drag-and-drop para el campo JSONField `secciones` de TipoEstudio.
    Usa SortableJS desde CDN. No requiere archivos de template externos.
    """

    class Media:
        js = ('https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js',)

    # ------------------------------------------------------------------
    # render
    # ------------------------------------------------------------------
    def render(self, name: str, value, attrs=None, renderer=None) -> str:
        # --- Normalizar el valor actual ---
        if isinstance(value, str):
            try:
                incluidas = json.loads(value) if value else []
            except (json.JSONDecodeError, ValueError):
                incluidas = []
        elif isinstance(value, list):
            incluidas = list(value)
        else:
            incluidas = []

        # Garantizar que las obligatorias siempre estén en "incluidas"
        for oblig in sorted(_SECCIONES_OBLIGATORIAS):
            if oblig not in incluidas:
                incluidas.insert(0, oblig)

        # Calcular disponibles (las que NO están incluidas)
        disponibles = [c for c in _TODOS_LOS_CODIGOS if c not in incluidas]

        widget_id = attrs.get('id', f'id_{name}') if attrs else f'id_{name}'
        hidden_id = f'{widget_id}_hidden'

        # --- Construir listas HTML ---
        items_incluidas = ''.join(
            _render_item(c, locked=(c in _SECCIONES_OBLIGATORIAS))
            for c in incluidas
        )
        items_disponibles = ''.join(
            _render_item(c, locked=False)
            for c in disponibles
        )

        # --- Estilos de columna compartidos ---
        col_style = (
            "flex:1;min-width:220px;display:flex;flex-direction:column;"
        )
        col_header_style = (
            "font-size:12px;font-weight:600;letter-spacing:.05em;"
            "text-transform:uppercase;color:#9B8EC4;margin-bottom:8px;"
            "padding-bottom:6px;border-bottom:1px solid #3a3a5a;"
        )
        list_style = (
            "list-style:none;margin:0;padding:8px;"
            "min-height:120px;border-radius:8px;"
            "background:#13131f;border:1px dashed #3a3a5a;"
            "flex:1;"
        )
        placeholder_style = (
            "color:#4a4a6a;font-size:12px;text-align:center;"
            "padding:20px;user-select:none;"
        )

        # Input hidden con valor inicial
        hidden_value = json.dumps(incluidas)

        html = f"""
<div id="{widget_id}" style="font-family:inherit;">
  <!-- Input oculto que Django leerá en el submit -->
  <input type="hidden" id="{hidden_id}" name="{name}" value="{hidden_value}">

  <!-- Contenedor de dos columnas -->
  <div style="display:flex;gap:24px;flex-wrap:wrap;align-items:flex-start;">

    <!-- Columna izquierda: Secciones Incluidas -->
    <div style="{col_style}">
      <p style="{col_header_style}">Incluidas</p>
      <ul
        id="{widget_id}_incluidas"
        style="{list_style}"
      >
        {items_incluidas if items_incluidas else
         f'<li style="{placeholder_style}">Arrastra secciones aquí</li>'}
      </ul>
    </div>

    <!-- Columna derecha: Secciones Disponibles -->
    <div style="{col_style}">
      <p style="{col_header_style}">Disponibles</p>
      <ul
        id="{widget_id}_disponibles"
        style="{list_style}"
      >
        {items_disponibles if items_disponibles else
         f'<li style="{placeholder_style}">Todas las secciones están incluidas</li>'}
      </ul>
    </div>

  </div><!-- /columnas -->

  <p style="margin-top:10px;font-size:11px;color:#6a6a8a;">
    &#x1F512; Las secciones con candado son obligatorias y no pueden removerse.
    Arrastra para cambiar el orden de las secciones incluidas.
  </p>
</div><!-- /widget -->

<script>
(function () {{
  // Esperar a que SortableJS esté disponible
  function initSecciones() {{
    if (typeof Sortable === 'undefined') {{
      setTimeout(initSecciones, 50);
      return;
    }}

    var hiddenInput   = document.getElementById('{hidden_id}');
    var listaIncluidas  = document.getElementById('{widget_id}_incluidas');
    var listaDisponibles = document.getElementById('{widget_id}_disponibles');

    // Conjuntos de códigos
    var OBLIGATORIAS = {json.dumps(sorted(_SECCIONES_OBLIGATORIAS))};

    function esObligatoria(el) {{
      return el.dataset && el.dataset.locked === '1';
    }}

    // Elimina el placeholder si existe
    function limpiarPlaceholder(lista) {{
      var ph = lista.querySelector('li[data-placeholder]');
      if (ph) ph.remove();
    }}

    // Añade un placeholder si la lista quedó vacía
    function agregarPlaceholder(lista, texto) {{
      if (lista.querySelectorAll('li[data-codigo]').length === 0) {{
        var li = document.createElement('li');
        li.setAttribute('data-placeholder', '1');
        li.style.cssText = '{placeholder_style}';
        li.textContent = texto;
        lista.appendChild(li);
      }}
    }}

    function actualizarHidden() {{
      var items = listaIncluidas.querySelectorAll('li[data-codigo]');
      var orden = Array.from(items).map(function(el) {{
        return el.dataset.codigo;
      }});
      hiddenInput.value = JSON.stringify(orden);
    }}

    // Sortable en la lista de incluidas
    Sortable.create(listaIncluidas, {{
      group: {{
        name: 'secciones',
        pull: function (to, from, dragEl) {{
          // No permite sacar items bloqueados
          return !esObligatoria(dragEl);
        }},
        put: true,
      }},
      handle: '.sortable-handle',
      animation: 150,
      ghostClass: 'sortable-ghost',
      onStart: function (evt) {{
        limpiarPlaceholder(listaIncluidas);
      }},
      onAdd: function (evt) {{
        limpiarPlaceholder(listaIncluidas);
        actualizarHidden();
        agregarPlaceholder(
          listaDisponibles,
          'Todas las secciones est\u00e1n incluidas'
        );
      }},
      onRemove: function (evt) {{
        actualizarHidden();
        agregarPlaceholder(listaIncluidas, 'Arrastra secciones aqu\u00ed');
      }},
      onUpdate: function () {{
        actualizarHidden();
      }},
    }});

    // Sortable en la lista de disponibles
    Sortable.create(listaDisponibles, {{
      group: {{
        name: 'secciones',
        pull: true,
        put: function (to, from, dragEl) {{
          // No acepta items bloqueados
          return !esObligatoria(dragEl);
        }},
      }},
      handle: '.sortable-handle',
      animation: 150,
      ghostClass: 'sortable-ghost',
      onStart: function (evt) {{
        limpiarPlaceholder(listaDisponibles);
      }},
      onAdd: function (evt) {{
        limpiarPlaceholder(listaDisponibles);
        actualizarHidden();
        agregarPlaceholder(listaIncluidas, 'Arrastra secciones aqu\u00ed');
      }},
      onRemove: function () {{
        agregarPlaceholder(
          listaDisponibles,
          'Todas las secciones est\u00e1n incluidas'
        );
      }},
    }});

    // Estilo del ghost mientras se arrastra
    var style = document.createElement('style');
    style.textContent = (
      '.sortable-ghost {{ opacity: 0.4; background: #4a3a8a !important; }}'
      + ' .sortable-handle:active {{ cursor: grabbing; }}'
    );
    document.head.appendChild(style);

    // Sincronización inicial
    actualizarHidden();
  }}

  // Inicializar cuando el DOM esté listo
  if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', initSecciones);
  }} else {{
    initSecciones();
  }}
}})();
</script>
"""
        return mark_safe(html)

    # ------------------------------------------------------------------
    # value_from_datadict: lee el input hidden y devuelve lista Python
    # ------------------------------------------------------------------
    def value_from_datadict(self, data, files, name):
        raw = data.get(name, '[]')
        if not raw:
            return []
        try:
            parsed = json.loads(raw)
            if not isinstance(parsed, list):
                return []
            # Solo devolver códigos válidos
            validos = {c for c, _ in _SECCIONES_DISPONIBLES}
            return [c for c in parsed if c in validos]
        except (json.JSONDecodeError, ValueError):
            return []
