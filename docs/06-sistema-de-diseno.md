# Sistema de diseño

## Historial de versiones

| Versión | Dirección visual | Estado |
|---|---|---|
| v1 | Oscura, brutalista industrial, inspirada en *Marathon* (Bungie, 1994) | Reemplazada |
| v2 | Clara, minimalista-brutalista, paleta hueso + azul/naranja, motivo hexagonal | Reemplazada |
| v3 | "Consola de matriz de puntos": papel gris cálido, tinta negra, un acento naranja | **Actual** |

La v3 empezó como un bloque de CSS pegado al final de la hoja de la v2 que sobrescribía casi todos sus tokens: el archivo tenía dos temas completos encimados y la mitad de las reglas no se usaban. En el tercer pase se reescribió `static/css/design-system.css` como una sola hoja, ordenada en tokens → base → shell → componentes → páginas → responsivo.

## Principios

- **Una sola acción principal por pantalla**, en negro con la "ficha" naranja de puntos (`.btn-primary`). Las acciones secundarias son botones con borde; las destructivas, rojas y siempre con confirmación.
- **Lo urgente arriba.** El inicio muestra "Requiere tu atención" según el rol; los préstamos se ordenan por fecha límite; las solicitudes pendientes, por orden de llegada.
- **Legibilidad antes que estilo.** La tipografía de matriz de puntos (Doto) se reserva para la marca y los números enteros grandes. Con cifras decimales (dinero, promedios) el "." se confunde con ",", así que esas usan la monoespaciada (`.stat-card__value--decimal`). Titulares, etiquetas y botones van en Instrument Sans, sin mayúsculas forzadas.
- **Estados con nombre, no con código.** `{% estado objeto %}` pinta la insignia con la etiqueta del modelo ("Pendiente", no "PENDIENTE").
- **Español de México** en toda la interfaz (tuteo, sin voseo).

## Tokens

| Token | Valor | Uso |
|---|---|---|
| `--bg` | `#f1f0ee` | Fondo de página (con trama de puntos) |
| `--surface` | `#ffffff` | Tarjetas, tablas, campos |
| `--surface-sunken` | `#f7f6f4` | Barra lateral, encabezados de tabla |
| `--line` / `--line-soft` | `#dcdbd6` / `#e9e8e4` | Bordes |
| `--ink` / `--ink-dim` / `--ink-faint` | `#111111` / `#55554f` / `#85847d` | Texto principal, secundario y auxiliar |
| `--accent` / `--accent-ink` | `#e8542f` / `#a8391a` | Acento; la variante `-ink` cumple contraste AA como texto |
| `--success`, `--warn`, `--danger`, `--info` | con su `-bg` | Estados funcionales |

Espaciado en escala de 4 px (`--sp-1` a `--sp-7`); radios de 8, 12 y 16 px.

## Componentes

| Clase / plantilla | Para qué |
|---|---|
| `templates/base.html` | Shell: barra lateral (con contador de solicitudes pendientes), barra superior con `page_title`, `breadcrumbs` y `page_actions`, avisos descartables y diálogo de confirmación |
| `templates/form_page.html` | Página de alta/edición; las plantillas solo definen `cancelar` y, si hace falta, `intro` |
| `templates/_form_fields.html` | Todos los campos con etiqueta, marca de obligatorio, ayuda y error (`aria-invalid`, `aria-describedby`) |
| `templates/_paginacion.html`, `templates/_vacio.html` | Paginación que conserva filtros; fila de "sin datos" con ícono, texto y acción |
| `.list-toolbar`, `.search-form`, `.chip` | Búsqueda y filtros por estado sobre cada lista |
| `.stat-card`, `.attention-item`, `.module-card` | Tableros e inicio |
| `.badge--ok/pending/danger/info/off` | Estados |
| `.callout--ok/warn/danger` | Avisos dentro de una página |
| `<form data-confirm="…">` | Pide confirmación en el diálogo compartido; con `data-confirm-motivo` agrega un campo de motivo |

Las etiquetas `{% estado %}`, `{% activo %}`, `{% icono %}` y `{% widget %}` viven en `usuarios/templatetags/ui.py` y están registradas como *builtins*: no hace falta `{% load %}`.

## Responsivo

- Debajo de 960 px la barra lateral se vuelve un menú deslizable (se cierra con el fondo, con Escape o al navegar).
- Debajo de 720 px las tablas se convierten en tarjetas: cada celda toma su etiqueta del encabezado.
- En pantallas táctiles ningún botón mide menos de 44 px (`pmq-kit.css`).

## Caché de estáticos

Nginx sirve `/static/` como `immutable` por 30 días. Por eso en producción se usa `ManifestStaticFilesStorage`: `collectstatic` genera `design-system.<hash>.css` y cada cambio de CSS llega de inmediato. En desarrollo (`DJANGO_DEBUG=True`) se sirven los archivos sin hash.

## Pendiente

- Nuevas capturas en `docs/screenshots/` con la v3.
- Las fuentes vienen de Google Fonts; si se quiere cero dependencias externas, alojarlas en `static/fonts/`.
