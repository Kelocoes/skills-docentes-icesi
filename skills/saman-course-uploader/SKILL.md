---
name: saman-course-uploader
description: Publica y mantiene material de cualquier curso en Saman (Brightspace / D2L, Universidad Icesi) con el MCP de Playwright. La skill es genérica y no contiene IDs; lee la configuración del curso desde .agents/output-skill/saman-course-uploader/ (course.yaml, manifest.yaml, state.yaml). Incluye operaciones por API generadas con los valores del curso, un mapa de navegación de la plataforma para no explorar la UI, un generador de HTML con tipografía consistente y las reglas de seguridad para modificar un curso.
---

# Saman Course Uploader

Sube y mantiene contenido en **Saman** (Brightspace/D2L) para **cualquier curso**. La skill es la herramienta; los datos del curso (OU, IDs, qué se publica, tema visual, reglas) viven aparte, en el repo del curso:

```text
<repo>/.agents/output-skill/saman-course-uploader/
├── course.yaml     configuración estable: plataforma, OU, carpeta /content/enforced, tema, seguridad, rutas
├── manifest.yaml   qué fuente local se publica y dónde (lo decide el docente)
├── state.yaml      IDs creados: módulos, temas, tareas (lo escribe el agente)
├── log.md          bitácora cronológica, solo se agregan filas
└── course_notes.md (opcional) convenciones y control de calidad propios del curso
```

## 0. Antes de nada: ¿hay configuración?

```text
python <skill>/scripts/saman_config.py validate
```

- **OK:** continuar. `saman_config.py show` resume el curso.
- **No existe la carpeta:** curso nuevo. `python <skill>/scripts/saman_config.py init` copia las plantillas (`templates/*.example.yaml`); completar `course.yaml` (obligatorios: `platform.base_url`, `course.ou`, `course.name`, `storage.enforced_folder`), iniciar sesión y ejecutar la operación **`discover`**, que entrega usuario, organización (OU y zona horaria), rol, curso, versiones de API, carpeta `/content/enforced/` (`course.storage_path`), módulos, temas y tareas sin explorar la UI. Lo único que no sale de la API y hay que pedir al docente es el tema visual (banners) y los selectores del login. Registrar los IDs con `saman_config.py set-module | set-topic | set-dropbox`.
- **Errores:** el validador cruza los tres YAML (alias huérfanos, IDs repetidos, fuentes que no existen, curso protegido). Corregir antes de escribir en Saman.
- Si el repo tiene `course_notes.md`, leerlo: trae las convenciones y reglas del docente para ese curso.

## 1. Credenciales y sesión

- Las credenciales van en el `.env` de la raíz (`auth.env_vars` da los nombres de las variables). Verificar con `git check-ignore .env` que sigue ignorado. **Nunca** imprimir, resumir ni escribir la contraseña en archivos versionados, commits, logs o respuestas.
- Login: `browser_navigate` a `platform.base_url` (redirige al IdP) y llenar usuario y contraseña con `browser_fill_form` (targets `#usernameUserInput` y `input[type=password]`) y pulsar Ingresar, o la operación `login`. Comprobar con la operación `whoami` (200 = activa); la sesión expira por inactividad.
- **Permisos:** Claude Code bloquea que el agente escriba credenciales en el navegador (`Credential Materialization`). Hay que permitir `mcp__playwright__browser_fill_form` y `mcp__playwright__browser_run_code_unsafe` en `.claude/settings.local.json` del proyecto (`permissions.allow`, archivo ignorado por Git). Si no está permitido, pedir al docente que inicie sesión a mano en la ventana de Playwright; no buscar otra vía para introducir la contraseña.
- Antes de **cualquier escritura**: operación `check_course` y comparar nombre y OU con `course.yaml`. Si el curso está en `protected_courses` o el nombre no coincide, parar y preguntar.

## 2. Cómo se trabaja: operaciones generadas, no snippets copiados

Las operaciones están en `scripts/ops.js`. Se generan con los valores del curso:

```text
python <skill>/scripts/render_op.py --list
python <skill>/scripts/render_op.py topic_html --topic paso_01            # alias de state.yaml o id numérico
python <skill>/scripts/render_op.py put_topic_html --topic paso_01 --file ruta/pagina.html
python <skill>/scripts/render_op.py create_topic --module unidad_1 --title "Lectura 1" --file x.pdf
```

El script imprime el JavaScript listo (por stdout; el tipo y la descripción, por stderr) para pegarlo en `browser_evaluate` (`kind: evaluate`) o `browser_run_code_unsafe` (`kind: run_code`). Con `--out archivo.js` lo escribe a un archivo. Las operaciones destructivas exigen `--confirm`.

| Operación | Tipo | Para qué |
| :--- | :--- | :--- |
| `whoami`, `login`, `my_courses`, `check_course` | evaluate / run_code | sesión y verificación del curso |
| `discover`, `toc` | evaluate | leer estructura del curso (llenar o refrescar `state.yaml`) |
| `topic_html`, `topic_info`, `module_structure` | evaluate | HTML publicado (respaldo), `Url` vigente, visibilidad; hijos de un módulo en orden |
| `create_module`, `edit_module`, `delete_module` | run_code / evaluate | módulos (unidades); `edit_module` conserva visibilidad y fechas |
| `dropbox_info`, `put_dropbox_instructions`, `delete_dropbox` | evaluate / run_code | tareas: leer, cargar instrucciones HTML, eliminar (la tarea se crea por la UI) |
| `create_topic` | run_code | tema de archivo: HTML, PDF, DOCX, ZIP |
| `put_topic_html` | run_code | reemplazar el HTML de una página conservando id y posición |
| `rename_topic`, `delete_topic` | evaluate | renombrar; eliminar (con `--confirm` y respaldo previo) |
| `audit_topic` | run_code | compara lo publicado con el archivo local (solo lectura) |
| `verify_images`, `typography` | evaluate | control de calidad de una página abierta |

Detalles, efectos laterales (`- Copy.html` huérfanos), cuerpos de las llamadas y tabla de errores: [`references/api.md`](./references/api.md).

**Sin API pública:** reordenar elementos (405/404; ver `references/api.md`).

**Aún sin probar** (probar con cuidado, en un módulo de prueba oculto que se borra al terminar, y documentar en `references/api.md` y `references/ui_map.yaml` al hacerlo): reordenar arrastrando en la UI, rúbrica nativa, ítem de calificación y cierre de una tarea, cuestionarios, debates, mover elementos entre módulos.

## 3. Navegar la UI sin explorar a ciegas

Solo cuando la API no alcanza (crear una asignación nativa, borrar archivos huérfanos, rúbricas). El orden es siempre:

1. **API** (operaciones de arriba).
2. **URL directa** del nodo en [`references/ui_map.yaml`](./references/ui_map.yaml) (plantillas con `{base}`, `{ou}`, `{module}`, `{topic}`).
3. **Acciones del nodo** con su selector por rol y nombre (`actions`), sin capturas intermedias. Leer con `browser_evaluate` o `browser_snapshot` (texto) antes que con capturas de pantalla.
4. **Exploración acotada** solo si el mapa no cubre el caso: máximo 5 snapshots, y **escribir lo aprendido en `ui_map.yaml`** (nodo o acción nueva, con `verified` y fecha) en la misma sesión.

Particularidades (iframe de Contenido, Shadow DOM, modo estudiante) están en `ui_map.yaml > global.ui_quirks`.

## 4. Reglas de seguridad

Los valores concretos (visibilidad por defecto, patrones protegidos, qué requiere confirmación) están en `course.yaml > safety`. La skill exige:

1. **Leer antes de escribir:** `topic_html`/`topic_info` o `toc` del elemento objetivo, y decir al docente qué se va a reemplazar.
2. **Sin borrados** de módulos, temas, tareas o archivos sin pedido explícito del docente. El borrado por API no se deshace: respaldar antes el HTML con `topic_html`.
3. **Visibilidad:** lo nuevo se crea según `safety.default_hidden` (oculto por defecto). Nunca cambiar la visibilidad de contenido existente por iniciativa propia.
4. **No tocar** calificaciones, publicación de notas ni inscripciones (`safety.forbidden`).
5. **Archivos o temas que coincidan con `safety.protected_name_patterns`:** nunca editarlos, moverlos ni borrarlos.
6. **Borrar archivos de curso (UI):** solo los que el agente creó, sin uso (cruzar con la `Url` de todos los temas de `toc`), con la selección verificada antes de confirmar.
7. **Cambios en lote:** un caso testigo, validar con el docente, luego replicar.
8. **Registrar** cada ID nuevo con `saman_config.py set-*` y cada cambio con `saman_config.py log "<acción>" "<ids>"`. Registrar también la `Url` vigente tras cada `put_topic_html`.
9. **Validar el material antes de subirlo:** una página publicada que repite un dato erróneo lo propaga a los estudiantes. Las verificaciones de contenido propias del curso están en `course_notes.md`.

## 5. Flujo de publicación

```text
[manifest.yaml: qué publicar] -> [saman_config.py validate] -> [login + check_course]
 -> [leer estado actual: toc / topic_info / topic_html]
 -> [generar HTML con saman_html.py (si aplica)] -> [revisar localmente]
 -> [crear (create_topic / create_module) o reemplazar (put_topic_html)]
 -> [topic_info: refrescar Url vigente] -> [audit_topic + verify_images + typography]
 -> [set-topic / log]
```

- **Elemento nuevo:** `create_topic` o `create_module`, luego `set-topic`/`set-module`.
- **Elemento existente:** `put_topic_html` (el tema conserva id y posición). Subir pocas veces: cada subida deja un archivo huérfano.
- **Asignación nativa:** crear por la UI (nodo `dialog_crear_elemento > asignacion`), registrar el dropbox y cargar las instrucciones por `PUT dropbox/folders/{id}`.
- **Auditar alineación repo y Saman:** `audit_topic` por cada página del manifest; resumir diferencias al docente.

## 6. Páginas HTML con tipografía consistente

`scripts/saman_html.py` y `scripts/md_to_saman.py` (más `mermaid_prerender.py`) generan HTML con el sistema tipográfico y esquivan las trampas de la plantilla institucional. Lee `theme` de `course.yaml`. Guía en [`references/page_templates.md`](./references/page_templates.md). Las figuras interactivas (kit DK) son otra skill; esta solo publica el HTML resultante.

## 7. Mantenimiento

Si Saman cambia (menú, versión de API, selectores), actualizar `ops.js`, `references/api.md` y `references/ui_map.yaml` en la misma sesión en que se detecte. Los hallazgos propios de un curso van en su `course_notes.md`, no aquí.
