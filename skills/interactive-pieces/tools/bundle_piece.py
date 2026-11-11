"""Empaqueta una pieza interactiva en UN solo archivo HTML (kit incluido) y, opcionalmente, en un <iframe srcdoc>
listo para pegar en una página de Saman (Brightspace) o de cualquier LMS que acepte HTML.

Las piezas cargan el kit con rutas relativas (../../../_shared/dk-*.js). Este script lee esos archivos y los
incrusta dentro del HTML, así la pieza ya no depende de otros archivos. Solo biblioteca estándar de Python.

Uso:
    python bundle_piece.py <carpeta-de-la-pieza>/index.html                  # escribe <slug>.bundle.html al lado
    python bundle_piece.py <pieza>/index.html -o salida.html --iframe 720    # además imprime el <iframe srcdoc> (alto 720 px)
    python bundle_piece.py <pieza>/index.html --theme light                  # fija el tema (con --iframe es claro por defecto:
                                                                             # Saman no tiene tema oscuro)
"""
import argparse
import html
import re
import sys
from pathlib import Path

SCRIPT = re.compile(r'<script\s+src="([^"]+)"\s*>\s*</script>', re.I)
STYLE = re.compile(r'<link\s+[^>]*rel="stylesheet"[^>]*href="([^"]+)"[^>]*>|<link\s+[^>]*href="([^"]+)"[^>]*rel="stylesheet"[^>]*>', re.I)


def local(base, ref):
    """Ruta local de un recurso relativo; None si es remoto (CDN), que se deja como está."""
    if re.match(r"^(https?:)?//|^data:", ref):
        return None
    path = (base / ref.split("?")[0]).resolve()
    if not path.exists():
        sys.exit(f"No existe {ref} (buscado en {path}). ¿Está instalado el kit junto a la pieza?")
    return path


def bundle(index, theme=None):
    base = index.parent
    doc = index.read_text(encoding="utf-8")

    def inline_script(m):
        p = local(base, m.group(1))
        if p is None:
            return m.group(0)
        if theme and p.name == "dk-theme.js":  # tema fijo: no seguir al sistema ni a la página anfitriona
            return f"<script>document.documentElement.setAttribute('data-dkt', '{theme}');</script>"
        return "<script>\n" + p.read_text(encoding="utf-8").replace("</script", "<\\/script") + "\n</script>"

    def inline_style(m):
        p = local(base, m.group(1) or m.group(2))
        return m.group(0) if p is None else "<style>\n" + p.read_text(encoding="utf-8") + "\n</style>"

    doc = SCRIPT.sub(inline_script, doc)
    doc = STYLE.sub(inline_style, doc)
    return doc


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("index", type=Path, help="index.html de la pieza")
    ap.add_argument("-o", "--out", type=Path, help="archivo de salida (por defecto <slug>.bundle.html junto a la pieza)")
    ap.add_argument("--iframe", type=int, metavar="ALTO", help="imprime también el <iframe srcdoc> con ese alto en px")
    ap.add_argument("--theme", choices=["light", "dark"], help="fija el tema de la pieza")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")  # en Windows la consola usa cp1252 y rompería las tildes del iframe

    theme = a.theme or ("light" if a.iframe else None)
    doc = bundle(a.index.resolve(), theme)
    out = a.out or a.index.parent.parent / f"{a.index.parent.name}.bundle.html"
    out.write_text(doc, encoding="utf-8")
    print(f"OK {out} ({len(doc) // 1024} KB, autocontenido)", file=sys.stderr)
    if a.iframe:
        title = re.search(r"<title>(.*?)</title>", doc, re.S)
        title = html.unescape(title.group(1).strip()) if title else "Pieza interactiva"
        print(f'<iframe title="{html.escape(title)}" srcdoc="{html.escape(doc, quote=True)}" '
              f'style="width:100%;height:{a.iframe}px;border:1px solid #e3e4ea;border-radius:8px" loading="lazy" allowfullscreen></iframe>')


if __name__ == "__main__":
    main()
