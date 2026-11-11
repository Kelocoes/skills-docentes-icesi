---
name: icesi-academic-workshops
description: Generates official Universidad Icesi academic workshops, assignments, exams, prompts, and rubrics from Markdown or user text into branded HTML and pixel-perfect PDF documents with native Mermaid diagrams, SVGs, and dynamic running headers.
category: general
---

# Universidad Icesi Academic Workshops & Assignments Skill

## Overview
This skill provides an automated, generic workflow to transform user-provided source documents (e.g., DOCX, PDF, raw text), Markdown drafts, or educational prompts into official Universidad Icesi academic deliverables (workshops, laboratory guides, exams, and rubrics).

It generates a standalone HTML document adhering strictly to the institutional syllabus design system and compiles it into a high-fidelity PDF using headless Chromium. The system features:
- Institutional typography (Plus Jakarta Sans).
- Running header on every page with official Icesi vector logo, vertical separator, course identification, period/NRC, dynamic page numbers (Pag. X de Y), and the signature 4-color stripe.
- Strict page-break protection avoiding split section headers, cut-off callouts, or fragmented tables.
- Native rendering of Mermaid flowcharts, inline SVGs, and embedded diagram figures (PNG, JPG, SVG).
- Standardized metadata activity grids and Icesi-blue evaluation rubrics with Generative AI (IAG) level declarations.

---

## Requirements and Prerequisites

1. **Python 3.10+**:
   - Built-in `os`, `sys`, `re`, `base64`, `argparse`, `datetime`, `shutil`.
   - `markdown-it-py` (for CommonMark and GFM table parsing).
   - `playwright` (with Chromium browser installed).
2. **Institutional Assets**:
   - Stored self-contained in `skills/icesi-academic-workshops/resources/`:
     - Vector Logos: `resources/logos/ICESI_logo_prin_descriptor_RGB_POSITIVO_0924.svg` and white variant.
     - Brand Fonts: `resources/fonts/PlusJakartaSans-Regular.ttf` and `PlusJakartaSans-Bold.ttf`.
     - Palette Reference: `resources/colors.md`.

---

## Workflow and Execution Guide

When a user requests creating or converting any academic deliverable (workshop, exam, lab guide, rubric):

### Step 1: Ingest Source Resources and Extract Assets
1. Read or parse the source material (e.g., DOCX, PDF, markdown, or plain text prompt).
2. Extract all structural requirements, instructions, and embedded media/diagram assets (PNG, JPG, SVG).
3. Compose a clean Markdown draft adhering to the standard template structure:
   - **Frontmatter Metadata**:
     ```yaml
     ---
     course: COMPUTACION EN INTERNET II
     document_type: GUIA DE TALLER PRACTICO / EVALUACION PRACTICA
     title: "Taller 01: Arquitectura de Servicios y Modelo de Dominio"
     period: "2026-02"
     nrc: "12489"
     group: "001"
     faculty: FACULTAD DE INGENIERIA, DISENO Y CIENCIAS APLICADAS
     department: DEPARTAMENTO DE COMPUTACION Y SISTEMAS INTELIGENTES
     professor: Docente Encargado
     due_date: "15 de Octubre de 2026"
     modality: Individual / Equipos
     code: 09769 - TIC
     ---
     ```
   - **Body Elements**:
     - `## Section Title`: Converted to an official Icesi section header with a blue square number box (`[ 1 ]`, `[ 2 ]`) and full-width line rule.
     - `<!-- pagebreak -->` or `\pagebreak`: Forces an immediate clean page break to push sections, rubrics, or requirements to the top of a new sheet.
     - `> [!NOTE]` or `> [!INFO]`: Generates an Icesi blue callout card.
     - `> [!WARNING]` or `> [!IMPORTANT]`: Generates an Icesi orange callout card.
     - `> [!TIP]`: Generates an Icesi green callout card.
     - Tables (`| Col 1 | Col 2 |`): Formatted with `#5454E9` solid blue header row and alternating row striping.
     - Diagrams: Fenced code blocks with ```` ```mermaid ```` rendered directly into scalable SVG vectors.
     - Embedded Images: Standard markdown `![Caption](image_name.png)` automatically resolved, base64-encoded, and wrapped in styled figure cards.

### Step 2: Render to HTML & PDF
Execute the automated renderer script:

```powershell
python skills/icesi-academic-workshops/scripts/render_workshop.py --input <path_to_markdown> --executed-by "<User_or_Agent>" --prompt "<Task_description>"
```

### Step 3: Self-Contained Execution Output Storage
All extracted characteristics, information rescued from input resources, source markdown files, and media/diagram assets MUST be consolidated directly within the execution output directory:

`output-skills/icesi-academic-workshops/[MM-DD-YYYY]_[counter]/`

Every execution folder contains the complete, reproducible package:
1. `INFO.md`: Documents execution timestamp, user/agent, and exact prompt.
2. `[document_name].md`: The complete markdown specification.
3. `[document_name].html`: Standalone HTML preview with embedded fonts and base64 assets.
4. `[document_name].pdf`: Final branded PDF document with A4 geometry, running headers, and zero overlap.
5. `[extracted_asset].png/.svg/.jpg`: All diagram images, schema figures, and visual assets extracted from source resources.

---

## Directory Layout

```text
skills/icesi-academic-workshops/
├── SKILL.md
├── references/
│   └── syllabus_format_spec.md
├── resources/
│   ├── colors.md
│   ├── fonts/
│   │   ├── PlusJakartaSans-Bold.ttf
│   │   └── PlusJakartaSans-Regular.ttf
│   └── logos/
│       ├── ICESI_logo_prin_descriptor_BYN_RGB_POSITIVO_0924.svg
│       ├── ICESI_logo_prin_descriptor_RGB_POSITIVO_0924.svg
│       └── ICESI_logo_prin_descriptor_WHITE.svg
├── scripts/
│   └── render_workshop.py
└── templates/
    └── workshop_example.md
```
