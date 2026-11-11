#!/usr/bin/env python3
"""
Universidad Icesi Academic Workshops & Assignments Renderer
Transforms Markdown input into official Universidad Icesi HTML & PDF documents.
Ensures zero overlap, running headers with page counters, brand color stripes,
and native support for Mermaid diagrams and SVG graphics.
"""

import os
import sys
import re
import base64
import argparse
from datetime import datetime
import html as html_module
import markdown_it
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter
from playwright.sync_api import sync_playwright

def extract_frontmatter(content):
    meta = {
        "course": "DISEÑO DE SOFTWARE I",
        "document_type": "GUÍA DE TALLER PRÁCTICO",
        "title": "Taller Académico",
        "period": "2026-02",
        "nrc": "",
        "group": "",
        "faculty": "Facultad Barberi de Ingeniería, Diseño y Ciencias aplicadas",
        "department": "Departamento de Computación y Sistemas Inteligentes",
        "professor": "",
        "due_date": "",
        "modality": "",
        "code": ""
    }

    body = content
    fm_match = re.search(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n", content, re.DOTALL)
    if fm_match:
        fm_text = fm_match.group(1)
        body = content[fm_match.end():]
        for line in fm_text.splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                meta[key.strip().lower()] = val.strip().strip("\"'")

    return meta, body

def convert_markdown_to_icesi_html(body_md, base_dir=None, collected_images=None):
    # Enable tables explicitly on CommonMark parser
    md = markdown_it.MarkdownIt("commonmark", {"html": True, "breaks": True}).enable("table")
    
    # Pre-process Mermaid blocks with placeholders so CommonMark does not mangle indentation into <pre><code>
    mermaid_blocks = []
    def stash_mermaid(match):
        idx = len(mermaid_blocks)
        diagram_code = match.group(1).strip()
        caption_match = re.search(r"caption:\s*(.+)$", diagram_code, re.MULTILINE)
        caption = ""
        if caption_match:
            caption = caption_match.group(1).strip()
            diagram_code = re.sub(r"caption:\s*(.+)$", "", diagram_code, flags=re.MULTILINE).strip()
        caption_html = f'<div class="figure-caption">{caption}</div>' if caption else ""
        escaped_diagram_code = html_module.escape(diagram_code)
        block_html = f'<div class="diagram-container"><div class="mermaid">\n{escaped_diagram_code}\n</div></div>{caption_html}'
        mermaid_blocks.append(block_html)
        return f"\n\nMERMAIDPLACEHOLDER{idx}BLOCK\n\n"

    processed_md = re.sub(r"```mermaid(.*?)```", stash_mermaid, body_md, flags=re.DOTALL)

    # Pre-process Docusaurus admonitions (:::info, :::tip, :::warning, :::note) into callout blocks
    def stash_admonition(match):
        adm_type = match.group(1).lower()
        title_raw = match.group(2)
        content_inner = match.group(3).strip()
        color_class = "callout-blue"
        default_title = "Nota / Información"
        if adm_type in ["tip", "success"]:
            color_class = "callout-green"
            default_title = "Recomendación / Tip"
        elif adm_type in ["warning", "danger", "caution"]:
            color_class = "callout-orange"
            default_title = "Atención / Importante"
        title_text = title_raw.strip("[]").strip() if title_raw else default_title
        inner_html = md.render(content_inner)
        idx = len(mermaid_blocks)
        block_html = f'<div class="callout {color_class}"><div class="callout-title">{title_text}</div>{inner_html}</div>'
        mermaid_blocks.append(block_html)
        return f"\n\nMERMAIDPLACEHOLDER{idx}BLOCK\n\n"

    processed_md = re.sub(r":::(\w+)(?:\[(.*?)\])?\s*\r?\n(.*?)\r?\n:::", stash_admonition, processed_md, flags=re.DOTALL)

    raw_html = md.render(processed_md)

    for idx, block_html in enumerate(mermaid_blocks):
        placeholder = f"MERMAIDPLACEHOLDER{idx}BLOCK"
        raw_html = re.sub(rf"<p>\s*{placeholder}\s*</p>", block_html, raw_html)
        raw_html = raw_html.replace(placeholder, block_html)

    # Convert images to base64 embedded figures to ensure reliable rendering in headless Chromium
    mime_map = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".svg": "image/svg+xml",
        ".gif": "image/gif",
        ".webp": "image/webp"
    }

    def replace_image(src, alt):
        src = src.strip()
        alt = alt.strip()
        resolved_path = None
        if os.path.isabs(src) and os.path.exists(src):
            resolved_path = src
        elif base_dir:
            cand = os.path.normpath(os.path.join(base_dir, src))
            if os.path.exists(cand):
                resolved_path = cand
        if not resolved_path:
            cand_cwd = os.path.normpath(os.path.join(os.getcwd(), src))
            if os.path.exists(cand_cwd):
                resolved_path = cand_cwd

        if resolved_path and os.path.exists(resolved_path):
            if collected_images is not None:
                collected_images.append(resolved_path)
            ext = os.path.splitext(resolved_path)[1].lower()
            mime = mime_map.get(ext, "image/png")
            with open(resolved_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            data_uri = f"data:{mime};base64,{b64}"
            img_cls = "svg-diagram" if ext == ".svg" else "bitmap-img"
            return f'<div class="figure-container"><img class="{img_cls}" src="{data_uri}" alt="{alt}" style="border-radius: 4px;" /></div>'
        ext = os.path.splitext(src)[1].lower() if src else ""
        img_cls = "svg-diagram" if ext == ".svg" else "bitmap-img"
        return f'<div class="figure-container"><img class="{img_cls}" src="{src}" alt="{alt}" style="border-radius: 4px;" /></div>'

    # Match markdown-rendered <p><img src="..." alt="..."></p> or standalone <img ...>
    def img_sub(m):
        return replace_image(m.group(1), m.group(2))
    raw_html = re.sub(r'<p>\s*<img\s+src="([^"]+)"\s+alt="([^"]*)"[^>]*>\s*</p>', img_sub, raw_html)
    raw_html = re.sub(r'<img\s+src="((?!data:)[^"]+)"\s+alt="([^"]*)"[^>]*>', img_sub, raw_html)

    # Convert figure caption paragraphs: <p><em>Figura X: ...</em></p> or <p>Figura X: ...</p>
    raw_html = re.sub(
        r'<p>\s*(?:<em>)?\s*(Figura\s+\d+[:\.].*?)\s*(?:</em>)?\s*</p>',
        r'<div class="figure-caption">\1</div>',
        raw_html
    )

    # Syntax highlight fenced code blocks via Pygments
    def highlight_code_block(match):
        lang = match.group(1).lower() if match.group(1) else ""
        raw_code = html_module.unescape(match.group(2))
        try:
            lexer = get_lexer_by_name(lang) if lang else TextLexer()
        except Exception:
            lexer = TextLexer()
        formatter = HtmlFormatter(nowrap=True)
        highlighted = highlight(raw_code, lexer, formatter).strip()
        lang_class = f" language-{lang}" if lang else ""
        return f'<pre class="code-block{lang_class}"><code class="hljs{lang_class}">{highlighted}</code></pre>'

    raw_html = re.sub(
        r'<pre><code(?:\s+class="language-([a-zA-Z0-9_\-]+)")?>([\s\S]*?)</code></pre>',
        highlight_code_block,
        raw_html
    )

    # Explicit Page Break markers support
    # Supports <!-- pagebreak -->, <!-- page-break -->, <!-- newpage -->, \pagebreak, ---pagebreak---
    raw_html = re.sub(
        r"(?:<!--\s*(?:page-?break|newpage|pb)\s*-->|\\pagebreak|---pagebreak---|&lt;!--\s*(?:page-?break|newpage|pb)\s*--&gt;)",
        '<div class="page-break"></div>',
        raw_html,
        flags=re.IGNORECASE
    )
    raw_html = re.sub(r'<p>\s*(<div class="page-break"></div>)\s*</p>', r'\1', raw_html)

    # Post-process Section Headers: turn <h2> or <h1> into Icesi section headers with numbered boxes
    section_counter = [0]
    def replace_heading(match):
        title_text = match.group(1).strip()
        num_match = re.match(r"^(\d+)[\.\s\-:]+(.*)", title_text)
        if num_match:
            sec_num = num_match.group(1)
            title = num_match.group(2).strip()
        else:
            section_counter[0] += 1
            sec_num = str(section_counter[0])
            title = title_text

        return f'''
        <div class="section-header-block">
            <div class="section-header">
                <div class="section-number-box">{sec_num}</div>
                <div class="section-title">{title}</div>
            </div>
            <div class="section-rule"></div>
        </div>
        '''

    html = re.sub(r"<h2[^>]*>(.*?)</h2>", replace_heading, raw_html)

    # Post-process Callout blocks (GitHub style blockquotes)
    def replace_callout(match):
        bq_content = match.group(1).strip()
        if "[!NOTE]" in bq_content or "[!INFO]" in bq_content:
            clean = re.sub(r"^<p>\s*\[!(NOTE|INFO)\]\s*", "<p>", bq_content, flags=re.IGNORECASE)
            return f'<div class="callout callout-blue"><div class="callout-title">Nota / Informacion</div>{clean}</div>'
        elif "[!WARNING]" in bq_content or "[!IMPORTANT]" in bq_content or "[!CAUTION]" in bq_content:
            clean = re.sub(r"^<p>\s*\[!(WARNING|IMPORTANT|CAUTION)\]\s*", "<p>", bq_content, flags=re.IGNORECASE)
            return f'<div class="callout callout-orange"><div class="callout-title">Atencion / Importante</div>{clean}</div>'
        elif "[!TIP]" in bq_content:
            clean = re.sub(r"^<p>\s*\[!TIP\]\s*", "<p>", bq_content, flags=re.IGNORECASE)
            return f'<div class="callout callout-green"><div class="callout-title">Recomendacion / Tip</div>{clean}</div>'
        return f'<div class="callout callout-blue">{bq_content}</div>'

    html = re.sub(r"<blockquote>(.*?)</blockquote>", replace_callout, html, flags=re.DOTALL)

    # Enhance tables with rubric-table class
    html = re.sub(r"<table>", '<table class="rubric-table">', html)

    return html

def get_font_faces(script_dir):
    fonts_dir = os.path.join(script_dir, "..", "resources", "fonts")
    regular_font = os.path.join(fonts_dir, "PlusJakartaSans-Regular.ttf")
    bold_font = os.path.join(fonts_dir, "PlusJakartaSans-Bold.ttf")
    
    font_css = ""
    if os.path.exists(regular_font):
        with open(regular_font, "rb") as f:
            b64_reg = base64.b64encode(f.read()).decode("utf-8")
        font_css += f"""
        @font-face {{
            font-family: 'Plus Jakarta Sans';
            src: url('data:font/ttf;base64,{b64_reg}') format('truetype');
            font-weight: 400;
            font-style: normal;
        }}
        """
    if os.path.exists(bold_font):
        with open(bold_font, "rb") as f:
            b64_bold = base64.b64encode(f.read()).decode("utf-8")
        font_css += f"""
        @font-face {{
            font-family: 'Plus Jakarta Sans';
            src: url('data:font/ttf;base64,{b64_bold}') format('truetype');
            font-weight: 700;
            font-style: normal;
        }}
        """
    return font_css

def build_full_html_document(meta, body_html, font_faces_css=""):
    mermaid_script = ""
    if '<div class="mermaid">' in body_html:
        mermaid_script = """
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({
            startOnLoad: true,
            theme: 'base',
            themeVariables: {
                primaryColor: '#CECDFD',
                primaryTextColor: '#111111',
                primaryBorderColor: '#5454E9',
                lineColor: '#5454E9',
                secondaryColor: '#F8F8FC',
                tertiaryColor: '#FFFFFF',
                fontSize: '15px',
                fontFamily: 'Plus Jakarta Sans, sans-serif'
            }
        });
    </script>
        """

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{meta['title']}</title>
    {mermaid_script}
    <style>
        {font_faces_css}

        :root {{
            --icesi-blue: #5454E9;
            --icesi-orange: #E9683B;
            --icesi-green: #4CB979;
            --icesi-lavender: #CECDFD;
            --icesi-gray-light: #ECECF2;
            --icesi-gray-medium: #88898C;
            --icesi-dark: #222222;

            /* User-selected calibration */
            --body-font-size: 9.3pt;
            --line-height: 1.50;
            --paragraph-spacing: 6.5px;
            --list-item-spacing: 3.0px;
            --heading-spacing: 16px;
            --page-margin-x: 22mm;
            --diagram-height: 75mm;
        }}

        .page-break {{
            break-before: page !important;
            page-break-before: always !important;
            clear: both;
            height: 0;
            margin: 0;
            padding: 0;
            border: none;
            display: block;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }}

        @media screen {{
            html {{
                background-color: #ECECF2;
            }}
            body {{
                font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                color: var(--icesi-dark);
                line-height: var(--line-height);
                font-size: var(--body-font-size);
                background-color: #FFFFFF;
                max-width: 860px;
                margin: 32px auto;
                padding: 48px 56px;
                box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
                border: 1px solid var(--icesi-gray-light);
                border-radius: 6px;
                box-sizing: border-box;
            }}
            .figure-container img.svg-diagram, .diagram-container img {{
                width: 100% !important;
                max-width: 100% !important;
                max-height: none !important;
                height: auto !important;
            }}
            .figure-container img.bitmap-img {{
                max-height: 520px !important;
                width: auto !important;
                max-width: 100% !important;
                height: auto !important;
            }}
        }}

        @media print {{
            body {{
                font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                color: var(--icesi-dark);
                line-height: var(--line-height);
                font-size: var(--body-font-size);
                background-color: #FFFFFF;
                max-width: 100% !important;
                margin: 0 !important;
                padding: 0 !important;
                box-shadow: none !important;
                border: none !important;
                border-radius: 0 !important;
            }}
            .figure-container img.svg-diagram, .diagram-container img {{
                width: 100% !important;
                max-width: 100% !important;
                max-height: 155mm !important;
                height: auto !important;
            }}
            .figure-container img.bitmap-img {{
                max-height: 85mm !important;
                width: auto !important;
                max-width: 100% !important;
                height: auto !important;
            }}
        }}

        /* Document Title and Header Info */
        .doc-eyebrow {{
            font-size: calc(var(--body-font-size) * 0.88);
            font-weight: 700;
            color: var(--icesi-blue);
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 3px;
        }}

        .doc-title {{
            font-size: calc(var(--body-font-size) * 1.72);
            font-weight: 800;
            color: #000000;
            line-height: 1.22;
            margin-bottom: calc(var(--paragraph-spacing) * 1.4);
        }}

        .entity-item {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: calc(var(--body-font-size) * 0.88);
            font-weight: 700;
            margin-bottom: 3px;
            color: #111111;
        }}

        .pill-bar {{
            width: 3.5px;
            height: 11px;
            border-radius: 1px;
            display: inline-block;
        }}

        .pill-blue {{ background-color: var(--icesi-blue); }}
        .pill-orange {{ background-color: var(--icesi-orange); }}
        .pill-green {{ background-color: var(--icesi-green); }}

        /* Metadata Activity Grid */
        .meta-section-heading {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: calc(var(--body-font-size) * 0.88);
            font-weight: 700;
            color: #111111;
            margin-top: calc(var(--heading-spacing) * 0.6);
            margin-bottom: 4px;
        }}

        .meta-grid {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: calc(var(--paragraph-spacing) * 1.5);
            border-top: 1px solid var(--icesi-gray-light);
            border-bottom: 1px solid var(--icesi-gray-light);
            break-inside: avoid !important;
            page-break-inside: avoid !important;
        }}

        .meta-grid tr {{
            border-bottom: 1px solid var(--icesi-gray-light);
        }}

        .meta-grid tr:last-child {{
            border-bottom: none;
        }}

        .meta-grid td {{
            padding: calc(var(--paragraph-spacing) * 0.8) 8px;
            font-size: calc(var(--body-font-size) * 0.88);
            line-height: 1.35;
        }}

        .meta-grid tr:nth-child(1) td:first-child {{
            border-left: 3px solid var(--icesi-blue);
        }}

        .meta-grid tr:nth-child(2) td:first-child {{
            border-left: 3px solid var(--icesi-green);
        }}

        .meta-grid tr td:nth-child(3) {{
            border-left: 1px solid var(--icesi-lavender);
        }}

        .meta-label {{
            font-weight: 700;
            color: #111111;
            text-transform: uppercase;
            width: 25%;
        }}

        .meta-value {{
            font-weight: 400;
            color: #333333;
            width: 25%;
        }}

        /* Section Headings with Solid Number Boxes - Strict Page Break Prevention */
        .section-header-block {{
            break-inside: avoid !important;
            page-break-inside: avoid !important;
            break-after: avoid !important;
            page-break-after: avoid !important;
            margin-top: var(--heading-spacing);
            margin-bottom: calc(var(--heading-spacing) * 0.3);
        }}

        .section-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 3px;
        }}

        .section-number-box {{
            background-color: var(--icesi-blue);
            color: #FFFFFF;
            font-weight: 800;
            font-size: calc(var(--body-font-size) * 1.2);
            width: calc(var(--body-font-size) * 2.5);
            height: calc(var(--body-font-size) * 2.5);
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 2px;
            flex-shrink: 0;
        }}

        .section-title {{
            font-size: calc(var(--body-font-size) * 1.24);
            font-weight: 700;
            color: #000000;
        }}

        .section-rule {{
            width: 100%;
            height: 1.2px;
            background-color: #000000;
            margin-bottom: calc(var(--paragraph-spacing) * 1.1);
        }}

        h3 {{
            font-size: calc(var(--body-font-size) * 1.05);
            font-weight: 700;
            color: #111111;
            margin-top: calc(var(--heading-spacing) * 0.6);
            margin-bottom: calc(var(--heading-spacing) * 0.25);
            break-after: avoid !important;
            page-break-after: avoid !important;
        }}

        p {{
            font-size: var(--body-font-size);
            line-height: var(--line-height);
            margin-bottom: var(--paragraph-spacing);
            text-align: justify;
        }}

        ol, ul {{
            margin-left: 18px;
            margin-bottom: calc(var(--paragraph-spacing) * 1.1);
        }}

        li {{
            font-size: var(--body-font-size);
            line-height: var(--line-height);
            margin-bottom: var(--list-item-spacing);
        }}

        /* Callouts - Smart Page Breaking for Long Content */
        .callout {{
            border-radius: 3px;
            background-color: #FFFFFF;
            border: 1px solid var(--icesi-gray-light);
            padding: calc(var(--paragraph-spacing) * 1.1) 12px;
            margin: calc(var(--paragraph-spacing) * 1.3) 0;
            font-size: calc(var(--body-font-size) * 0.95);
            line-height: calc(var(--line-height) * 0.95);
            break-inside: auto;
            page-break-inside: auto;
        }}

        .callout p {{
            font-size: inherit;
            line-height: inherit;
            margin-bottom: calc(var(--paragraph-spacing) * 0.8);
        }}

        .callout li {{
            font-size: inherit;
            line-height: inherit;
            margin-bottom: calc(var(--list-item-spacing) * 0.9);
            break-inside: avoid !important;
            page-break-inside: avoid !important;
        }}

        .callout-blue {{ border-left: 3.5px solid var(--icesi-blue); }}
        .callout-orange {{ border-left: 3.5px solid var(--icesi-orange); }}
        .callout-green {{ border-left: 3.5px solid var(--icesi-green); }}

        .callout-title {{
            font-size: calc(var(--body-font-size) * 0.92);
            font-weight: 700;
            text-transform: uppercase;
            margin-bottom: 4px;
            break-inside: avoid !important;
            break-after: avoid !important;
            page-break-after: avoid !important;
        }}

        .callout-blue .callout-title {{ color: var(--icesi-blue); }}
        .callout-orange .callout-title {{ color: var(--icesi-orange); }}
        .callout-green .callout-title {{ color: var(--icesi-green); }}

        /* Rubric / Tables - Replicates Exact Icesi Blue Header */
        .rubric-table {{
            width: 100%;
            border-collapse: collapse;
            margin: calc(var(--paragraph-spacing) * 1.2) 0;
            border: 1px solid var(--icesi-gray-light);
            break-inside: avoid !important;
            page-break-inside: avoid !important;
        }}

        .rubric-table thead {{
            display: table-header-group;
        }}

        .rubric-table tr {{
            break-inside: avoid !important;
            page-break-inside: avoid !important;
        }}

        .rubric-table th {{
            background-color: var(--icesi-blue);
            color: #FFFFFF;
            font-size: calc(var(--body-font-size) * 0.85);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            padding: calc(var(--paragraph-spacing) * 0.8) 8px;
            text-align: left;
            border: 1px solid var(--icesi-blue);
        }}

        .rubric-table td {{
            padding: calc(var(--paragraph-spacing) * 0.8) 8px;
            font-size: calc(var(--body-font-size) * 0.90);
            line-height: 1.38;
            border: 1px solid var(--icesi-gray-light);
        }}

        .rubric-table tr:nth-child(even) td {{
            background-color: #FBFBFE;
        }}

        /* Diagrams & Figures */
        .diagram-container, .figure-container {{
            border: 1px solid var(--icesi-gray-light);
            border-radius: 4px;
            padding: 12px;
            margin-top: calc(var(--paragraph-spacing) * 1.5);
            margin-bottom: 5px;
            background-color: #FFFFFF;
            text-align: center;
            break-inside: avoid !important;
            page-break-inside: avoid !important;
        }}

        .mermaid {{
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
        }}

        .mermaid svg {{
            max-width: 100% !important;
            max-height: 95mm !important;
            width: auto !important;
            height: auto !important;
        }}

        .diagram-container img, .figure-container img {{
            width: auto;
            max-width: 100%;
            height: auto;
            object-fit: contain;
        }}

        .figure-container img.svg-diagram, .diagram-container img {{
            width: 100%;
            max-width: 100%;
            height: auto;
        }}

        .diagram-caption, .figure-caption {{
            font-size: calc(var(--body-font-size) * 0.80);
            color: #555555;
            font-weight: 500;
            margin-top: 4px;
            margin-bottom: calc(var(--paragraph-spacing) * 2.6);
            text-align: center;
            line-height: 1.35;
            break-before: avoid !important;
            page-break-before: avoid !important;
        }}

        /* Inline code (badges in normal text) */
        :not(pre) > code {{
            font-family: 'Consolas', 'Fira Code', 'Cascadia Code', monospace;
            background-color: #F1F3F5;
            padding: 1.5px 4.5px;
            border-radius: 3px;
            font-size: calc(var(--body-font-size) * 0.90);
            color: #A31515;
            border: 1px solid #E2E8F0;
        }}

        /* Fenced Code Blocks (IDE Editor Light Style) */
        pre.code-block, pre {{
            background-color: #F8FAFC;
            border: 1px solid #CBD5E1;
            border-left: 3.5px solid var(--icesi-blue);
            border-radius: 4px;
            padding: 8px 12px;
            margin: calc(var(--paragraph-spacing) * 1.3) 0;
            overflow-x: auto;
            font-family: 'Consolas', 'Fira Code', 'Cascadia Code', monospace;
            font-size: calc(var(--body-font-size) * 0.86);
            line-height: 1.44;
            break-inside: avoid !important;
            page-break-inside: avoid !important;
        }}

        pre code {{
            font-family: inherit;
            background: transparent !important;
            padding: 0 !important;
            border: none !important;
            color: #1E293B; /* Default identifier / symbol text */
            font-size: inherit;
        }}

        /* Pygments Syntax Highlighting Tokens (Light Editor Theme) */
        .code-block .k, .code-block .kd, .code-block .kn, .code-block .kp, .code-block .kr {{
            color: #0033B3; /* IntelliJ/VS Keyword Blue */
            font-weight: 700;
        }}
        .code-block .kt {{
            color: #0033B3; /* Type keyword */
            font-weight: 700;
        }}
        .code-block .nc, .code-block .ne, .code-block .nn {{
            color: #267F99; /* Class / Interface / Enum Teal */
            font-weight: 700;
        }}
        .code-block .nf, .code-block .fm {{
            color: #795E26; /* Method / Function Warm Amber/Brown */
            font-weight: 600;
        }}
        .code-block .nd {{
            color: #9E7F00; /* Annotations (@Override, @FunctionalInterface) Gold/Amber */
            font-weight: 700;
        }}
        .code-block .s, .code-block .sa, .code-block .sb, .code-block .sc, .code-block .dl,
        .code-block .sd, .code-block .s2, .code-block .se, .code-block .sh, .code-block .si,
        .code-block .sx, .code-block .sr, .code-block .s1, .code-block .ss {{
            color: #067D17; /* Strings - Vibrant Forest Green */
        }}
        .code-block .m, .code-block .mb, .code-block .mf, .code-block .mh, .code-block .mi,
        .code-block .il, .code-block .mo {{
            color: #1750EB; /* Numeric Literals - Royal Blue */
            font-weight: 600;
        }}
        .code-block .c, .code-block .ch, .code-block .cm, .code-block .c1, .code-block .cs {{
            color: #64748B; /* Comments - Muted Slate Gray */
            font-style: italic;
        }}
        .code-block .cp, .code-block .cpf {{
            color: #7C3AED; /* Preprocessor / Directives */
        }}
        .code-block .o, .code-block .ow {{
            color: #334155; /* Operators (+, -, =, ==, ->) */
            font-weight: 600;
        }}
        .code-block .p {{
            color: #475569; /* Punctuation and brackets */
        }}
        .code-block .na, .code-block .nv, .code-block .vi, .code-block .vg, .code-block .vm {{
            color: #871094; /* Attributes / Fields / Variables - Rich Magenta/Purple */
        }}
        .code-block .gh, .code-block .gu {{
            color: #0F172A;
            font-weight: 700;
        }}
    </style>
</head>
<body>

    <!-- Eyebrow and Main Title -->
    {f'<div class="doc-eyebrow">{meta["document_type"]}</div>' if meta['document_type'] else ''}
    <h1 class="doc-title">{meta['title']}</h1>

    <!-- University Entities -->
    <div class="entity-item">
        <span class="pill-bar pill-blue"></span>
        <span>{meta['faculty']}</span>
    </div>
    <div class="entity-item">
        <span class="pill-bar pill-orange"></span>
        <span>{meta['department']}</span>
    </div>

    <!-- Activity Information Grid -->
    <div class="meta-section-heading"><span class="pill-bar pill-blue"></span><span>INFORMACI&Oacute;N DE LA ACTIVIDAD</span></div>
    <table class="meta-grid">
        <tr>
            <td class="meta-label">Curso</td><td class="meta-value">{meta['course']}</td>
            <td class="meta-label">C&oacute;digo</td><td class="meta-value">{meta['code']}</td>
        </tr>
        <tr>
            <td class="meta-label">Docentes</td><td class="meta-value">{meta['professor']}</td>
            <td class="meta-label">Fecha de entrega</td><td class="meta-value">{meta['due_date']}</td>
        </tr>
        <tr>
            <td class="meta-label">Per&iacute;odo</td><td class="meta-value">{meta['period']}</td>
            <td class="meta-label">Modalidad</td><td class="meta-value">{meta['modality']}</td>
        </tr>
    </table>

    <!-- Main Workshop Content -->
    {body_html}

</body>
</html>
"""

def get_header_template(meta, logo_uri):
    period_str = meta.get('period', '').strip()
    nrc_str = meta.get('nrc', '').strip()
    if period_str and nrc_str:
        sub_text = f"Per&iacute;odo: {period_str} &middot; NRC: {nrc_str}"
    elif period_str:
        sub_text = f"Per&iacute;odo: {period_str}"
    elif nrc_str:
        sub_text = f"NRC: {nrc_str}"
    else:
        sub_text = ""

    sub_span = f'<span style="font-size: 8.5pt; color: #555555;">{sub_text}</span>' if sub_text else ""

    return f"""
    <div style="width: 100%; margin: 0 var(--page-margin-x, 22mm); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; -webkit-print-color-adjust: exact; box-sizing: border-box;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
            <div style="display: flex; align-items: center; gap: 18px;">
                <img src="{logo_uri}" style="height: 72px; width: auto; object-fit: contain;">
                <div style="width: 2px; height: 68px; background-color: #CECDFD;"></div>
                <div style="display: flex; flex-direction: column; justify-content: center; gap: 4px;">
                    <span style="font-size: 8.5pt; font-weight: 700; color: #000000; text-transform: uppercase; letter-spacing: 0.8px;">UNIVERSIDAD ICESI</span>
                    <span style="font-size: 10.5pt; font-weight: 700; color: #111111; text-transform: uppercase;">PROGRAMA DE CURSO: {meta['course']}</span>
                    {sub_span}
                </div>
            </div>
            <div style="font-size: 9pt; color: #88898C; font-weight: 500; align-self: flex-start; margin-top: 6px;">
                P&aacute;g. <span class="pageNumber"></span> de <span class="totalPages"></span>
            </div>
        </div>
        <div style="height: 3px; width: 100%; background: linear-gradient(to right, #5454E9 0% 70%, #E9683B 70% 88%, #4CB979 88% 94%, #CECDFD 94% 100%);"></div>
        <div style="height: 1px; width: 100%; background: #ECECF2; margin-top: 1px;"></div>
    </div>
    """

def get_next_output_dir(skill_name="icesi-academic-workshops"):
    base_output = os.path.abspath("output-skills")
    skill_output_root = os.path.join(base_output, skill_name)
    today_str = datetime.now().strftime("%m-%d-%Y")
    
    counter = 1
    while True:
        candidate = os.path.join(skill_output_root, f"{today_str}_{counter:02d}")
        if not os.path.exists(candidate):
            os.makedirs(candidate, exist_ok=True)
            return candidate
        counter += 1

def create_info_md(output_dir, executed_by, prompt):
    info_path = os.path.join(output_dir, "INFO.md")
    content = f"""# Execution Metadata

- **Executed By:** {executed_by}
- **Date & Time:** {datetime.now().isoformat()}
- **Prompt:** {prompt}
"""
    with open(info_path, "w", encoding="utf-8") as f:
        f.write(content)

def render_workshop(markdown_path, output_pdf=None, executed_by="Agent", prompt="Render Workshop"):
    if not os.path.exists(markdown_path):
        print(f"[Error] Input markdown not found: {markdown_path}", file=sys.stderr)
        return False

    with open(markdown_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    font_faces_css = get_font_faces(script_dir)

    base_dir = os.path.dirname(os.path.abspath(markdown_path))
    meta, body_md = extract_frontmatter(md_text)
    collected_images = []
    body_html = convert_markdown_to_icesi_html(body_md, base_dir=base_dir, collected_images=collected_images)
    full_html = build_full_html_document(meta, body_html, font_faces_css=font_faces_css)

    # Output directory handling
    if output_pdf:
        final_pdf_path = os.path.abspath(output_pdf)
        out_dir = os.path.dirname(final_pdf_path)
    else:
        out_dir = get_next_output_dir()
        create_info_md(out_dir, executed_by, prompt)
        base_name = os.path.splitext(os.path.basename(markdown_path))[0]
        final_pdf_path = os.path.join(out_dir, f"{base_name}.pdf")

    # Copy input markdown file and all extracted/referenced images to output directory
    import shutil
    dest_md_path = os.path.join(out_dir, os.path.basename(markdown_path))
    if os.path.abspath(markdown_path) != os.path.abspath(dest_md_path):
        try:
            shutil.copy2(markdown_path, dest_md_path)
        except Exception:
            pass

    for img_path in set(collected_images):
        abs_img = os.path.abspath(img_path)
        abs_out = os.path.abspath(out_dir)
        # Do not copy if image already resides within out_dir or one of its subdirectories (e.g. img/)
        if abs_img.startswith(abs_out + os.sep) or abs_img == abs_out:
            continue
        dest_img = os.path.join(out_dir, os.path.basename(img_path))
        if abs_img != os.path.abspath(dest_img):
            try:
                shutil.copy2(img_path, dest_img)
            except Exception:
                pass

    # Save the generated HTML file alongside PDF for full inspection/debugging
    base_name = os.path.splitext(os.path.basename(final_pdf_path))[0]
    final_html_path = os.path.join(out_dir, f"{base_name}.html")
    with open(final_html_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    # Encode logo
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logo_file = os.path.join(script_dir, "..", "resources", "logos", "ICESI_logo_prin_descriptor_RGB_POSITIVO_0924.svg")
    logo_file = os.path.abspath(logo_file)

    if os.path.exists(logo_file):
        with open(logo_file, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode("utf-8")
        logo_uri = f"data:image/svg+xml;base64,{logo_b64}"
    else:
        logo_uri = ""

    header_html = get_header_template(meta, logo_uri)

    print(f"[Info] Launching Playwright to render PDF: {final_pdf_path}")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(full_html, wait_until="networkidle")
        
        # Wait for Mermaid diagrams to complete SVG rendering if present
        if '<div class="mermaid">' in full_html:
            try:
                page.wait_for_selector(".mermaid svg", timeout=10000)
            except Exception as e:
                print(f"[Warning] Mermaid wait exception: {e}")
        
        page.wait_for_timeout(500)

        page.pdf(
            path=final_pdf_path,
            format="A4",
            print_background=True,
            display_header_footer=True,
            header_template=header_html,
            footer_template='<div style="font-size: 1px;"></div>',
            margin={"top": "30mm", "bottom": "18mm", "left": "22mm", "right": "22mm"}
        )
        browser.close()

    if os.path.exists(final_pdf_path) and os.path.getsize(final_pdf_path) > 0:
        print(f"[Success] PDF generated successfully: {final_pdf_path} ({os.path.getsize(final_pdf_path)} bytes)")
        print(f"[Success] HTML source saved: {final_html_path}")
        return True
    else:
        print("[Error] Playwright PDF generation failed.", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="Render Universidad Icesi Workshop Markdown to PDF")
    parser.add_argument("--input", required=True, help="Path to input Markdown file")
    parser.add_argument("--output", help="Optional path for output PDF file")
    parser.add_argument("--executed-by", default="Agent", help="Identifier of executor")
    parser.add_argument("--prompt", default="Render Workshop", help="Prompt or task trigger")

    args = parser.parse_args()
    ok = render_workshop(args.input, args.output, args.executed_by, args.prompt)
    if not ok:
        sys.exit(1)

if __name__ == "__main__":
    main()
