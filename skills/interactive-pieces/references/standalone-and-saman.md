# Piezas sin sitio web: sueltas o dentro de Saman

No hace falta un sitio de documentación para usar una pieza. Hay tres formas, de la más simple a la más integrada.

## 1. Preparar una carpeta de piezas (una sola vez por curso)

Desde la carpeta de tu curso (`<skill>` es la carpeta de esta skill, por ejemplo `~/.claude/skills/interactive-pieces`):

```bash
node <skill>/host/install.mjs --kit-dir piezas/_shared --no-frame --no-tests
node <skill>/host/new-piece.mjs piece piezas/semana-1/mi-pieza --kit-dir piezas/_shared
```

(Sin `--kit-dir`, los dos comandos asumen la carpeta de Docusaurus `static/interactive/_shared`.)

Queda así:

```text
piezas/
  _shared/            el kit (generado; no se edita)
  semana-1/
    mi-pieza/
      index.html      solo datos: actores, fases, pasos y textos
```

Plantillas: `piece` (secuencia por fases), `piece-canvas` (escena libre) y `piece-phone` (simulador de app móvil).

## 2. Abrirla como archivo

Doble clic en `piezas/semana-1/mi-pieza/index.html`. Funciona sin servidor ni internet porque el kit se carga con rutas relativas. Sirve para proyectarla en clase o enviarla comprimida (zip de la carpeta `piezas/` completa).

## 3. Publicarla en Saman (Brightspace)

Saman muestra las páginas HTML de un tema, pero no sirve la carpeta `_shared/` junto a ellas. Por eso la pieza se **empaqueta en un solo archivo**:

```bash
python <skill>/tools/bundle_piece.py piezas/semana-1/mi-pieza/index.html --iframe 720 > iframe.html
```

- `mi-pieza.bundle.html` es la pieza con el kit adentro (unos 80 KB). Se puede subir a Saman como un tema de archivo HTML.
- `iframe.html` contiene un `<iframe srcdoc="...">` listo para pegar dentro de una página HTML de Saman, entre el texto de la lección. Es lo que hace la skill `saman-course-uploader` al publicar una página con piezas.
- Con `--iframe` el tema queda en **claro**, porque Saman no tiene tema oscuro y si no la pieza seguiría el modo oscuro del sistema del estudiante. Para fijar otro tema: `--theme dark`.

Prueba siempre el `.bundle.html` en el navegador antes de subirlo: recorre todos los pasos y los interruptores.

## Enlazar o embeber un sitio completo

Si el curso ya tiene un sitio público de documentación, en Saman se puede crear un tema de tipo **enlace** o una página con `<iframe src="https://...">` hacia el capítulo. Las piezas siguen funcionando porque viven en el sitio.
