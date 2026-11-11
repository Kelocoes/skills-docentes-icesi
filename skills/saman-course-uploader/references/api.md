# API de Brightspace (D2L) usada por la skill

Genérico: sin IDs de curso. `{ou}` = `course.ou`, `{lp}`/`{le}` = `platform.api` de `course.yaml`. Las operaciones listas están en `scripts/ops.js` y se generan con `render_op.py`; esta página explica lo que no cabe en un snippet. Verificado en Saman (Universidad Icesi) el 2026-10-22 con rol Profesor.

## Autenticación
- Lectura y escritura funcionan con las cookies del navegador, sin OAuth.
- Las escrituras exigen el header `X-Csrf-Token` con el valor de `localStorage['XSRF.Token']`.
- La sesión expira por inactividad: comprobar con `GET /d2l/api/lp/{lp}/users/whoami` (200 = activa).
- Versiones: `GET /d2l/api/versions/` si un endpoint falla por versión.

## Lectura (200 OK)

| Recurso | Endpoint |
| :--- | :--- |
| Mis matrículas | `/d2l/api/lp/{lp}/enrollments/myenrollments/` |
| Info del curso | `/d2l/api/lp/{lp}/courses/{ou}` |
| TOC completo | `/d2l/api/le/{le}/{ou}/content/toc` |
| Módulos raíz | `/d2l/api/le/{le}/{ou}/content/root/` |
| Un módulo / un tema | `/d2l/api/le/{le}/{ou}/content/modules/{id}` / `.../content/topics/{id}` |
| HTML de un tema | `/d2l/api/le/{le}/{ou}/content/topics/{id}/file` |
| Ítems de calificación | `/d2l/api/le/{le}/{ou}/grades/` |
| Carpetas de tareas | `/d2l/api/le/{le}/{ou}/dropbox/folders/` |
| Cuestionarios / debates | `/d2l/api/le/{le}/{ou}/quizzes/` / `.../discussions/forums/` |
| Archivos del curso | `/d2l/api/lp/{lp}/{ou}/managefiles/` |

`/rubrics` por API devuelve 400: las rúbricas se gestionan por UI.

## Escrituras verificadas

| Acción | Llamada | Operación |
| :--- | :--- | :--- |
| Crear módulo raíz | `POST content/root/` con `{Title, ShortTitle:"", Type:0, ModuleStartDate:null, ModuleEndDate:null, ModuleDueDate:null, IsHidden, IsLocked:false, Description:{Content,Type:"Html"}, Duration:null}` | `create_module` |
| Editar módulo | `PUT content/modules/{id}` con el mismo cuerpo. Hacer `GET` antes y reutilizar visibilidad y fechas. Actualiza en sitio, sin copias | `edit_module` |
| Reemplazar HTML de un tema | `PUT content/topics/{id}/file`, `multipart/form-data`, campo `file`. Responde 200 sin cuerpo | `put_topic_html` |
| Crear tema de archivo | `POST content/modules/{id}/structure/`, `multipart/mixed` (parte 1 JSON, parte 2 binario con `Content-Disposition: form-data; name=""; filename=...`) | `create_topic` |
| Renombrar tema | `PUT content/topics/{id}` reutilizando los valores del `GET`. El archivo no cambia | `rename_topic` |
| Eliminar tema | `DELETE content/topics/{id}`. Sin deshacer | `delete_topic` |
| Listar hijos de un módulo | `GET content/modules/{id}/structure/` (en orden) | `module_structure` |
| Eliminar módulo | `DELETE content/modules/{id}`. Sin deshacer; no borra los archivos de `/content/enforced/` (quedan huérfanos). Verificado 2026-10-23 | `delete_module` |
| Crear tarea | **Por la UI** (ver nota). Por API también se crea (`POST dropbox/folders/`, `DropboxType` 2 = individual, 1 = grupo, `SubmissionType` 0 = archivo), pero en la Unidad 1 el enlace creado a mano por API se veía como enlace y no como asignación; esa diferencia no se volvió a comparar (el tema de la UI y el de la API son ambos `TopicType 3`) | UI (`ui_map.yaml: dropbox_new`) |
| Leer tarea | `GET dropbox/folders/{id}` | `dropbox_info` |
| Instrucciones de tarea | `PUT dropbox/folders/{id}` con el objeto del `GET` **sin** `Id, CategoryId, Attachments, TotalFiles, UnreadFiles, FlaggedFiles, TotalUsers, TotalUsersWithSubmissions, TotalUsersWithFeedback, ActivityId, LinkAttachments` y con `CustomInstructions:{Content:'<html>',Type:'Html'}`. Responde 200 con el objeto actualizado y conserva nombre, visibilidad, tipo y regla de entregas. Verificado 2026-10-23 | `put_dropbox_instructions` |
| Eliminar tarea | `DELETE dropbox/folders/{id}`. Sin deshacer; borra sus entregas. Borrar también su tema (`delete_topic`). Verificado 2026-10-23 | `delete_dropbox` |

Nota sobre asignaciones: `Crear nuevo > Asignación` en la UI crea el **tema** en cuanto se hace clic (su id aparece en `returnUrl`, `TopicType 3`, `Url` tipo `quickLink.d2l?...type=dropbox&rCode=...`, `ActivityId` `.../activities/dropbox/...`) y el **dropbox** al pulsar `Guardar y cerrar`. Después se lee el id del dropbox con `discover`/`dropbox_info` y se cargan las instrucciones por API. Un dropbox recién creado tiene `GradeItemId: null` y `Assessment.Rubrics: []`: ítem de calificación y rúbrica siguen sin probarse.

## Reordenar elementos
La API pública **no** lo permite: `PUT content/modules/{id}/structure/` responde 405 y los endpoints `.../structure/reorder` y `/unstable/.../order` dan 404. El menú Opciones del módulo no ofrece "Reordenar". Hasta probar el arrastre en la UI, controlar el orden subiendo en secuencia (los temas se añaden al final) y verificarlo con `module_structure`.

## Versiones y datos que entrega `discover`
Versiones vigentes el 2026-10-23: `lp 1.64`, `le 1.100` (las configuradas, 1.63 y 1.99, siguen funcionando). `discover` devuelve también usuario (`whoami.Identifier`), organización (`organization/info`: OU, nombre y zona horaria), rol (`enrollments/myenrollments/{ou}`) y la carpeta de archivos del curso (`courses/{ou}.Path`), que es el `storage.enforced_folder`.

## Efectos laterales y reglas del sistema de archivos
- **`PUT .../file` sirve tambien para ZIP y DOCX** (verificado 2026-11-09 con `urbantransit-integration.zip` y `Plantilla_LAB-PAT.docx`): reemplaza el archivo del tema, el nombre pasa a `<nombre> - Copy.<ext>` y los bytes servidos coinciden con los subidos. Un dropbox admite `DueDate` en el mismo `PUT dropbox/folders/{id}` de las instrucciones (ISO en UTC).
- **`PUT .../file` crea una copia**: guarda el contenido en `<nombre> - Copy.html` (luego `- Copy (1)`, ...) y reapunta el tema; el archivo anterior queda huérfano. La URL vigente se lee con `topic_info` (campo `Url`). Registrarla en `state.yaml`.
- **`PUT .../file` puede volver visible lo oculto** (verificado 2026-10-26): tras reemplazar el HTML de un tema creado oculto, el tema y su submódulo padre quedaron visibles. Después de cada `put_topic_html` en contenido oculto, releer `IsHidden` del tema y de su módulo y, si cambió, restaurarlo con `PUT topics/{id}` / `PUT modules/{id}` reutilizando los valores del `GET` con `IsHidden: true`. También se vio que, después de ocultar un submódulo y su tema con `PUT`, los demás temas del submódulo (creados ocultos) aparecieron visibles; se ocultaron uno por uno con `PUT topics/{id}` y quedaron estables. Regla práctica: tras tocar visibilidad o reemplazar HTML, auditar con `GET content/toc` el `IsHidden` de todo el submódulo y no solo del tema editado. Crear submódulos en la Unidad 2 no anidó la Unidad 3 (el efecto de la Unidad 1 no se repitió).
- **`Url` es obligatorio al crear un tema de archivo** y debe coincidir con el nombre del archivo, bajo `storage.enforced_folder`. Con `Url:""` el tema se crea pero queda `IsBroken:true`.
- Con un nombre de archivo sin colisión la URL queda exacta; si ya existe, D2L añade `- Copy`.
- Los temas se añaden **al final** del módulo. No hay endpoint de reordenar verificado: para controlar el orden, subir en secuencia o borrar y volver a subir (con permiso del docente).
- Un PDF de 14 MB subió sin problemas. El visor de PDF (`d2l-pdf-viewer`, canvas) puede verse gris 2 a 15 s mientras renderiza.
- Enlace estable a un tema desde HTML: `{base}/d2l/le/content/{ou}/viewContent/{topic}/View`.
- Para pasar un archivo local al navegador: `browser_run_code_unsafe` no tiene `fs`. Crear un `<input type=file>` temporal, llenarlo con `page.setInputFiles` y leerlo dentro de `fetch` (lo hacen las operaciones `run_code`).

## Borrar archivos huérfanos (solo UI)
No hay endpoint de API verificado. Ver el nodo `manage_files` en `ui_map.yaml`. Antes de borrar: listar los temas (`toc`), construir el conjunto de `Url` en uso y no tocar nunca un archivo en uso ni los que coincidan con `safety.protected_name_patterns`.

## Errores conocidos

| Síntoma | Causa | Arreglo |
| :--- | :--- | :--- |
| `browser_navigate` a Saman redirige al IdP | Sesión expirada | Repetir login (`login` en `ops.js`) y comprobar `whoami` |
| El login se deniega: `Credential Materialization` | Claude Code no deja que el agente escriba credenciales con `browser_fill_form` / `browser_run_code_unsafe` | Agregar ambas herramientas a `permissions.allow` en `.claude/settings.local.json` (y reiniciar o abrir `/hooks` si la carpeta `.claude/` no existía al iniciar la sesión), o iniciar sesión a mano en la ventana de Playwright |
| `locator.check: ... is not a valid selector` en Gestionar archivos | El `title` con comillas dentro de un selector CSS | `page.getByTitle('Seleccionar "<nombre>"', {exact: true})` |
| Tema creado con `IsBroken: true` | `Url` vacío o no coincide con el archivo | Borrar el tema (con permiso) y crearlo de nuevo con `Url` |
| `GET /rubrics` da 400 | La API no expone rúbricas | Gestionar por UI |
| Un enlace de tarea no se ve como asignación | Se creó por API (`TopicType 3`) | Crearla por la UI |
| Aparecen `... - Copy (N).html` en Gestionar archivos | Cada `PUT .../file` genera uno | Subir pocas veces; limpiar huérfanos propios por UI |
| Captura del tema cortada | El visor de Contenido está en un iframe | Abrir la `Url` vigente del tema y capturar `fullPage` |
| `fetch` de una imagen con espacios falla desde `/content/...` | URL sin codificar | Usar `encodeURI(ruta)` desde una página `/d2l/...` |
| `getByRole('button',{name:'Cancelar'}).first()` cierra la página | El diálogo de código fuente tapa el botón | Cerrar el diálogo con Escape |
| Heredocs largos de Python/JS fallan en Git Bash de Windows | Comillas y apóstrofes | Escribir el archivo con la herramienta Write y ejecutarlo |
| Salida con `�` en rutas con ñ | Consola de Windows en cp1252 | Los scripts de la skill ya fuerzan UTF-8; en scripts propios usar `sys.stdout.reconfigure(encoding="utf-8")` |

## Submódulos y mover elementos (verificado 2026-10-26)

- **Crear submódulo:** `POST content/modules/{padre}/structure/` con el cuerpo de `create_module` (`Type: 0`). 200, devuelve `ParentModuleId`. **Efecto lateral observado:** tras crear 4 submódulos en la Unidad 1, el módulo hermano Unidad 2 (271214) quedó como hijo de la Unidad 1. Comprobar siempre `GET content/root/` después y corregir.
- **Mover elementos y cambiar nivel (única vía):** UI de Lecciones (`/d2l/le/lessons/{ou}/units/{id}`), dentro del iframe `smart-curriculum`. Enfocar el botón `Acción de reordenar elemento de <título>` (`.focus()`; el clic falla por interceptación), `Enter` activa el modo, `ArrowUp/ArrowDown` mueven entre hermanos, `ArrowRight` anida en el hermano anterior, `ArrowLeft` sube un nivel, `Enter` confirma. Verificar con `GET content/modules/{id}/structure/` tras cada movimiento. Receta: subir el submódulo sobre sus elementos y anidar cada elemento con `ArrowRight`.
- Mover conserva ids, visibilidad y la tarea (TopicType 3).
