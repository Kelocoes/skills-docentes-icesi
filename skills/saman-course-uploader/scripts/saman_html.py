"""Helpers para generar paginas HTML de Saman (Brightspace) con el sistema tipografico del curso.

Sistema (verificado midiendo estilos computados en Saman):
  - Todo el texto en Lato, color #202122.
  - 32 px titulo de seccion (700, #5454e9) | 20 px titulo de actividad (700)
    | 18 px titulo de lectura/subseccion (700, #5454e9) | 16 px todo lo demas (400 / negrita 700).
  - Cada p, li y td lleva su font-size explicito: la plantilla institucional escala los <p> dentro de <li>.
  - Los encabezados usan <span> con la fuente, nunca <strong> (sale en serif o con peso 900).

Uso:
    import sys; sys.path.insert(0, "<ruta>/.agents/skills/saman-course-uploader/scripts")
    from saman_html import *

La plataforma y los banners salen de `course.yaml` (platform.base_url y theme.*) en
`.agents/output-skill/saman-course-uploader/`. Sin configuracion o sin los campos de banner,
las paginas se generan igual pero sin imagenes de banner.
"""
import io

try:
    import saman_config as _cfg
    _COURSE = _cfg.load("course")
except Exception:   # sin carpeta de datos: valores neutros
    _COURSE = {}

_THEME = _COURSE.get("theme", {})
BASE_URL = _COURSE.get("platform", {}).get("base_url", "").rstrip("/")
IMG = f"{BASE_URL}{_THEME['banners_folder']}" if _THEME.get("banners_folder") else ""            # banners de seccion (Objetivos, Actividades, Recursos...)
UNIT_IMG = f"{BASE_URL}{_THEME['unit_banners_folder']}" if _THEME.get("unit_banners_folder") else ""   # banners de unidad
STYLER_OU = _THEME.get("content_styler_ou") or _COURSE.get("platform", {}).get("org_ou", "")
ACCENT = _THEME.get("accent", "#5454e9")
TH_BG = _THEME.get("table_header", "#e9683b")

FONT = "font-family: Lato, sans-serif;"
INK = "color: #202122;"
BODY = f"{FONT} font-size: 16px; line-height: 1.5; {INK}"
P_STYLE = f"{BODY} text-align: justify; margin: 0 0 12px 0;"
UL_STYLE = f"{BODY} margin: 0 0 12px 0; padding-left: 28px;"
LI_STYLE = f"{BODY} text-align: justify; margin: 0 0 6px 0;"
LINK_STYLE = f"{FONT} font-size: 16px; font-weight: 700; color: #006fbf;"
TH_STYLE = (f"{FONT} font-size: 16px; font-weight: 700; line-height: 1.5; color: #ffffff; border-style: solid; "
            f"border-color: #ecf0f1; padding: 8px; background-color: {TH_BG}; text-align: center; width: 25%;")
TD_STYLE = f"{BODY} border-style: solid; border-color: #ecf0f1; padding: 8px; text-align: center;"

CALLOUTS = {   # (color del borde, fondo)
    "nota": (ACCENT, "#f2f2ff"),
    "alerta": (TH_BG, "#fff4ef"),
}


def p(t):
    return f'<p style="{P_STYLE}">{t}</p>'


def ul(items):
    lis = "\n".join(f'<li style="{LI_STYLE}">{i}</li>' for i in items)
    return f'<ul style="{UL_STYLE}">\n{lis}\n</ul>'


def ol(items):
    lis = "\n".join(f'<li style="{LI_STYLE}">{i}</li>' for i in items)
    return f'<ol style="{UL_STYLE}">\n{lis}\n</ol>'


def h3(t):
    """Titulo de actividad: 20 px, 700."""
    return (f'<h3 style="margin: 24px 0 12px 0;"><span style="{FONT} font-size: 20px; font-weight: 700; '
            f'line-height: 1.3; {INK}">{t}</span></h3>')


def h4(t):
    """Titulo de lectura o subseccion: 18 px, 700, azul."""
    return (f'<h4 style="margin: 20px 0 6px 0;"><span style="{FONT} font-size: 18px; font-weight: 700; '
            f'line-height: 1.3; color: {ACCENT};">{t}</span></h4>')


def subtitle(t):
    """Subtitulo dentro de una seccion (nivel 16 px en negrita)."""
    return f'<p style="{P_STYLE} margin: 16px 0 6px 0;"><strong>{t}</strong></p>'


def link(href, t):
    return f'<a href="{href}" target="_blank" rel="noreferrer noopener" style="{LINK_STYLE}">{t}</a>'


def banner(name, alt, w=240, h=100, margin="8px 0"):
    """Banner de seccion (archivo dentro de theme.banners_folder). Sin carpeta configurada devuelve cadena vacia."""
    if not IMG:
        return ""
    return f'<p style="margin: {margin};"><img src="{IMG}/{name}" alt="{alt}" title="{alt}" width="{w}" height="{h}"></p>'


def activity_open():
    """Abre el contenedor de actividades; page_close() lo cierra."""
    return '<div style="padding-bottom: 0px;">'


def meta_table(headers, values):
    ths = "\n".join(f'<th style="{TH_STYLE}" scope="col">{h}</th>' for h in headers)
    tds = "\n".join(f'<td style="{TD_STYLE}">{v}</td>' for v in values)
    return (f'<table border="0" style="border-collapse: collapse; width: 100%; border-color: #ecf0f1; '
            f'border-style: solid; margin: 0 0 16px 0;">\n<tbody>\n<tr>\n{ths}\n</tr>\n<tr>\n{tds}\n</tr>\n</tbody>\n</table>')


def callout(kind, title, text):
    border, bg = CALLOUTS[kind]
    return (f'<div style="border-left: 4px solid {border}; background-color: {bg}; padding: 12px 16px; margin: 0 0 16px 0;">'
            f'<p style="{P_STYLE} margin: 0 0 6px 0;"><strong>{title}</strong></p>'
            f'<p style="{P_STYLE} margin: 0;">{text}</p></div>')


def page_open(unit_banner=None, unit_alt=None, heading="Introducción"):
    """Cabecera de la pagina. unit_banner: archivo en theme.unit_banners_folder (por defecto theme.default_unit_banner;
    sin ninguno configurado no se pone imagen)."""
    unit_banner = unit_banner or _THEME.get("default_unit_banner")
    unit_alt = unit_alt or _THEME.get("default_unit_alt", "Banner de la unidad")
    img = (f'<img src="{UNIT_IMG}/{unit_banner}" alt="{unit_alt}" title="{unit_alt}" style="max-width: 100%;">'
           if unit_banner and UNIT_IMG else "")
    return f'''<!DOCTYPE html>
<html><head><link rel="stylesheet" href="https://s.brightspace.com/lib/fonts/0.6.1/fonts.css"><link rel="stylesheet" href="https://templates.lcs.brightspace.com/lib/assets/css/styles.min.css"><link rel="stylesheet" href="{BASE_URL}/d2l/le/contentstyler/{STYLER_OU}/files/View" data-override="override"><script src="https://templates.lcs.brightspace.com/lib/assets/js/scripts.min.js" defer=""></script></head><body style="color: rgb(32, 33, 34); font-family: Lato, sans-serif; font-size: 16px;"><div style="width: 100%;"></div>
<div style="width: 100%; max-width: 1100px; margin: auto;">
<div style="color: #00266e; padding: 10px 78px 0 78px;">
<h2 style="margin: 0; font-size: 36px;">{img}</h2>
<h2 style="margin: 0 0 8px 0;"><span style="{FONT} font-size: 32px; font-weight: 700; line-height: 1.3; color: {ACCENT};">{heading}</span></h2>'''


def page_close():
    return '''</div>
<div style="padding-top: 40px; padding-right: 20px; padding-bottom: 0px;">
<p>&nbsp;</p>
</div>
</div>
</div></body></html>
'''


def write_page(path, parts):
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(parts))
