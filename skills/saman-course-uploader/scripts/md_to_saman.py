"""Convierte un manual Markdown del repo en el cuerpo HTML de una pagina de Saman con el sistema tipografico del curso.

Cubre lo que usan los manuales de la Unidad 1: encabezados, parrafos, listas anidadas, tablas, citas, bloques de
codigo (resaltado con Pygments, estilos en linea), bloques ```mermaid (SVG prerenderizado), imagenes locales
(incrustadas como data URI, asi la pagina es un solo archivo) y admoniciones Docusaurus (:::info[Titulo] ... :::).

Mapeo de niveles (el titulo `#` y el front matter se omiten; la pagina pone su propio titulo):
    ##  -> h3 (20 px, 700)          ###  -> h4 (18 px, 700, azul)          ####  -> negrita 16 px

Uso:
    from md_to_saman import md_to_saman
    body = md_to_saman(md_path, mermaid_svgs=[ruta_svg_1, ...])   # lista de <p>, <h3>, <table>... (cadena HTML)
"""
import base64
import html
import mimetypes
import os
import re

from markdown_it import MarkdownIt
from markdown_it.renderer import RendererHTML
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer

from saman_html import (BODY, FONT, INK, LI_STYLE, LINK_STYLE, P_STYLE, UL_STYLE)

MONO = "font-family: Consolas, 'Courier New', monospace;"
PRE_STYLE = (f"{MONO} font-size: 14px; line-height: 1.5; {INK} background-color: #f6f8fa; border: 1px solid #d0d7de; "
             "border-radius: 4px; padding: 12px 16px; margin: 0 0 16px 0; overflow-x: auto; white-space: pre; text-align: left;")
CODE_INLINE = f"{MONO} font-size: 15px; background-color: #f1f3f5; border-radius: 3px; padding: 1px 4px;"
TH = (f"{FONT} font-size: 16px; font-weight: 700; line-height: 1.5; color: #ffffff; border-style: solid; "
      "border-color: #ecf0f1; padding: 8px; background-color: #e9683b; text-align: left; vertical-align: top;")
TD = f"{BODY} border-style: solid; border-color: #ecf0f1; padding: 8px; text-align: left; vertical-align: top;"
WIDE_PX = 1000   # diagramas mas anchos que esto se muestran al 80 % con desplazamiento horizontal
IMG = "display: block; margin: 0 auto; max-width: 100%; height: auto;"
ADM = {"info": ("#5454e9", "#f2f2ff"), "note": ("#5454e9", "#f2f2ff"), "tip": ("#2e9e6b", "#f0faf5"),
       "warning": ("#e9683b", "#fff4ef"), "danger": ("#e9683b", "#fff4ef")}


def _svg_normalize(svg):
    """Quita width/height relativos del <svg> raiz y los fija en px desde el viewBox (un <img> sin tamano se ve mal)."""
    m = re.search(r"<svg\b[^>]*>", svg)
    root = m.group(0)
    vb = re.search(r'viewBox="([\d.\-]+)[ ,]+([\d.\-]+)[ ,]+([\d.]+)[ ,]+([\d.]+)"', root)
    new = re.sub(r'\s(width|height|style)="[^"]*"', "", root)
    if vb:
        new = new[:-1] + f' width="{round(float(vb.group(3)))}" height="{round(float(vb.group(4)))}">'
    return svg.replace(root, new, 1)


def _data_uri(path):
    if path.lower().endswith(".svg"):
        raw = _svg_normalize(open(path, encoding="utf-8").read()).encode("utf-8")
        return "data:image/svg+xml;base64," + base64.b64encode(raw).decode()
    mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(open(path, "rb").read()).decode()


def _highlight(code, lang):
    try:
        lexer = get_lexer_by_name(lang) if lang else TextLexer()
    except Exception:
        lexer = TextLexer()
    out = highlight(code, lexer, HtmlFormatter(nowrap=True, noclasses=True, style="default"))
    return out.rstrip("\n")


class SamanRenderer(RendererHTML):
    mermaid_svgs = []
    base_dir = "."
    _mm = 0

    # ---- bloques ----
    def heading_open(self, tokens, idx, options, env):
        lvl = tokens[idx].tag
        if lvl == "h2":
            return (f'<h3 style="margin: 28px 0 12px 0;"><span style="{FONT} font-size: 20px; font-weight: 700; '
                    f'line-height: 1.3; {INK}">')
        if lvl == "h3":
            return (f'<h4 style="margin: 22px 0 8px 0;"><span style="{FONT} font-size: 18px; font-weight: 700; '
                    'line-height: 1.3; color: #5454e9;">')
        return f'<p style="{P_STYLE} margin: 16px 0 6px 0;"><strong>'

    def heading_close(self, tokens, idx, options, env):
        return {"h2": "</span></h3>\n", "h3": "</span></h4>\n"}.get(tokens[idx].tag, "</strong></p>\n")

    def paragraph_open(self, tokens, idx, options, env):
        if tokens[idx].hidden:
            return ""
        kids = tokens[idx + 1].children or []
        real = [k for k in kids if k.type not in ("softbreak",)]
        if len(real) == 1 and real[0].type == "image":
            return '<p style="margin: 8px 0 4px 0; text-align: center;">'
        if real and real[0].type == "em_open" and real[-1].type == "em_close" and \
                "".join(k.content for k in real if k.type == "text").startswith("Figura"):
            return f'<p style="{P_STYLE} text-align: center; margin: 0 0 16px 0;">'
        return f'<p style="{P_STYLE}">'

    def paragraph_close(self, tokens, idx, options, env):
        return "" if tokens[idx].hidden else "</p>\n"

    def bullet_list_open(self, tokens, idx, options, env):
        return f'<ul style="{UL_STYLE}">\n'

    def ordered_list_open(self, tokens, idx, options, env):
        start = tokens[idx].attrGet("start")
        return f'<ol style="{UL_STYLE}"' + (f' start="{start}"' if start else "") + ">\n"

    def list_item_open(self, tokens, idx, options, env):
        return f'<li style="{LI_STYLE}">'

    def blockquote_open(self, tokens, idx, options, env):
        return ('<div style="border-left: 4px solid #b9b9d6; background-color: #f7f7fb; padding: 8px 16px; '
                'margin: 0 0 16px 0;">\n')

    def blockquote_close(self, tokens, idx, options, env):
        return "</div>\n"

    def hr(self, tokens, idx, options, env):
        return '<hr style="border: 0; border-top: 1px solid #ecf0f1; margin: 20px 0;">\n'

    def table_open(self, tokens, idx, options, env):
        return ('<table border="0" style="border-collapse: collapse; width: 100%; border-color: #ecf0f1; '
                'border-style: solid; margin: 0 0 16px 0;">\n')

    def th_open(self, tokens, idx, options, env):
        return f'<th style="{TH}" scope="col">'

    def td_open(self, tokens, idx, options, env):
        return f'<td style="{TD}">'

    def fence(self, tokens, idx, options, env):
        tok = tokens[idx]
        lang = (tok.info or "").strip().split()[0] if (tok.info or "").strip() else ""
        if lang == "mermaid":
            path = self.mermaid_svgs[self._mm]
            self._mm += 1
            alt = f"Diagrama {self._mm}"
            vb = re.search(r'viewBox="[\d.\-]+[ ,]+[\d.\-]+[ ,]+([\d.]+)', open(path, encoding="utf-8").read())
            width = float(vb.group(1)) if vb else 0
            if width > WIDE_PX:   # diagrama ancho: tamano legible (80 %) dentro de un contenedor con desplazamiento
                return (f'<p style="{P_STYLE} text-align: center; margin: 8px 0 4px 0;"><em>Desliza horizontalmente para ver el diagrama completo.</em></p>\n'
                        f'<div style="overflow-x: auto; border: 1px solid #ecf0f1; margin: 0 0 4px 0;"><img src="{_data_uri(path)}" '
                        f'alt="{alt}" style="display: block; max-width: none; height: auto; width: {round(width * 0.8)}px;"></div>\n')
            return (f'<p style="margin: 8px 0 4px 0; text-align: center;"><img src="{_data_uri(path)}" '
                    f'alt="{alt}" style="{IMG}"></p>\n')
        return f'<pre style="{PRE_STYLE}">{_highlight(tok.content, lang)}</pre>\n'

    # ---- en linea ----
    def code_inline(self, tokens, idx, options, env):
        return f'<span style="{CODE_INLINE}">{html.escape(tokens[idx].content)}</span>'

    def link_open(self, tokens, idx, options, env):
        href = html.escape(tokens[idx].attrGet("href") or "")
        return f'<a href="{href}" target="_blank" rel="noreferrer noopener" style="{LINK_STYLE}">'

    def image(self, tokens, idx, options, env):
        tok = tokens[idx]
        path = os.path.normpath(os.path.join(self.base_dir, tok.attrGet("src")))
        alt = html.escape(tok.content)
        return f'<img src="{_data_uri(path)}" alt="{alt}" style="{IMG}">'

    def softbreak(self, tokens, idx, options, env):
        return "\n"

    def hardbreak(self, tokens, idx, options, env):
        return "<br>\n"


def _admonition(kind, title, inner_html):
    border, bg = ADM.get(kind, ADM["note"])
    return (f'<div style="border-left: 4px solid {border}; background-color: {bg}; padding: 12px 16px; margin: 0 0 16px 0;">'
            f'<p style="{P_STYLE} margin: 0 0 6px 0;"><strong>{html.escape(title)}</strong></p>{inner_html}</div>\n')


def md_to_saman(md_path, mermaid_svgs=(), text=None, pieces=None):
    """text: Markdown ya editado (por defecto se lee md_path, que tambien fija la carpeta de las imagenes).
    pieces: funcion slug -> HTML para las lineas `@@piece:slug@@` (piezas interactivas incrustadas)."""
    if text is None:
        text = open(md_path, encoding="utf-8").read()
    text = re.sub(r"\A---\n.*?\n---\n", "", text, count=1, flags=re.S)   # front matter
    admons = []

    def grab(m):
        admons.append((m.group(1), m.group(2), m.group(3)))
        return f"\n@@ADM{len(admons) - 1}@@\n"

    text = re.sub(r"^:::(\w+)\[(.*?)\]\n(.*?)\n:::[ \t]*$", grab, text, flags=re.S | re.M)

    SamanRenderer.mermaid_svgs = list(mermaid_svgs)
    SamanRenderer._mm = 0
    SamanRenderer.base_dir = os.path.dirname(os.path.abspath(md_path))
    md = MarkdownIt("commonmark", renderer_cls=SamanRenderer).enable("table")
    out = md.render(text)
    # el mermaid de las admoniciones (si lo hubiera) usa el mismo contador; se renderizan despues, en orden

    def put(m):
        kind, title, inner = admons[int(m.group(1))]
        return _admonition(kind, title, md.render(inner))

    out = re.sub(r'<p style="[^"]*">@@ADM(\d+)@@</p>\n?', put, out)
    if pieces:
        out = re.sub(r'<p style="[^"]*">@@piece:([\w-]+)@@</p>\n?', lambda m: pieces(m.group(1)) + "\n", out)
    return out
