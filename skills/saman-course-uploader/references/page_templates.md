# Páginas HTML para Saman

## Generación
`scripts/saman_html.py` entrega helpers (`p`, `ul`, `ol`, `h3`, `h4`, `subtitle`, `link`, `banner`, `meta_table`, `callout`, `page_open`, `page_close`, `write_page`). Lee `platform.base_url` y `theme.*` de `course.yaml`; sin banners configurados, las páginas salen sin imágenes de banner. `scripts/md_to_saman.py` convierte un manual Markdown completo (código resaltado, tablas, imágenes en data URI, admoniciones y diagramas Mermaid prerenderizados con `scripts/mermaid_prerender.py`). Los generadores de cada página viven en el repo del curso (`paths.builders_dir`), no en la skill.

```python
import sys; sys.path.insert(0, "<repo>/.agents/skills/saman-course-uploader/scripts")
from saman_html import *
parts = [page_open(), h3("Titulo"), p("Texto."), page_close()]
write_page("pagina.html", parts)
```

## Sistema tipográfico (verificado midiendo estilos computados)
Todo el texto en **Lato, #202122**, con cuatro niveles: título de sección 32 px (700, color de acento), título de actividad 20 px (700), título de lectura o subsección 18 px (700, acento) y **todo lo demás 16 px** (400; negrita 700; enlaces 700 #006fbf). Cabeceras de tabla 16 px blanco sobre `theme.table_header`. Código en Consolas 14 px (en línea, 15 px).

## Trampas de la plantilla institucional (`styles.min.css` + `contentstyler`)
- Un `<p>` dentro de un `<li>` se escala a ~19 px si no tiene `font-size` propio: poner `font-size: 16px` en cada `p`, `li` y `td` (no basta en el `span`).
- `<strong>` dentro de `<h3>/<h4>` sale en serif (Times) o con peso 900: usar `<span style="font-family: Lato, sans-serif; font-size: ...; font-weight: 700">` dentro del encabezado.
- Un enlace con `<strong>` interno sale con peso 900: poner `font-weight: 700` en el `<a>`.
- Verificar con la operación `typography`: debe dar solo las combinaciones del sistema.

## Estructura de la plantilla semanal institucional
Banner de unidad, `h2` "Introducción", banner de objetivos, consignas de actividades, banner de entregables con `h3 "Actividad N"` y `ul`, banner de recursos con bibliografía. Cualquier texto va como HTML dentro del contenedor (`max-width:1100px; padding:10px 78px 0`). Las plantillas disponibles en el editor varían por institución: listarlas desde el nodo `editor_pagina` del `ui_map.yaml`.

## Manuales Markdown a página HTML
1. Si hay Mermaid: `python scripts/mermaid_prerender.py <manual.md> <tmp>`, abrir `http://127.0.0.1:8765/render.html` con el MCP y esperar `DONE` sin `ERR`; copiar los SVG a la carpeta de assets del generador.
2. Escribir un `build_<pagina>.py` que llame `md_to_saman(md, svgs)` entre `page_open()` y `page_close()`.
3. Subir con `create_topic` (tema nuevo) o, para cambiar el formato de un tema existente (por ejemplo PDF a HTML), `put_topic_html`: conserva id, título y posición.
4. Verificar con `verify_images` (todas las `<img>` con `naturalWidth > 0`) y `typography`.

Reglas del conversor: `##` = 20 px, `###` = 18 px, `####` = negrita 16 px; diagramas de más de 1000 px de ancho se muestran al 80 % con desplazamiento horizontal.

## Contenido embebido
Una pieza interactiva o figura autocontenida puede incrustarse con `<iframe srcdoc="...">` (mismo origen que Saman, sin subir archivos extra). Cómo se diseñan esas piezas es tema de otra skill; esta solo sabe publicarlas.
