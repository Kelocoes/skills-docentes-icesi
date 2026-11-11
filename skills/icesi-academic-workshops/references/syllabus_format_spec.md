# Universidad Icesi Academic Document Format Specification

This specification formalizes the visual identity, typographical hierarchy, and structural layout extracted from official Universidad Icesi academic syllabi and course programs (based on syllabus reference 117289eb-743d-4b00-8f97-1681132fa98f.pdf).

---

## 1. Page Geometry & Dimensions

- Paper Size: Standard A4 (210mm x 297mm / 595.28pt x 841.89pt).
- Margins:
  - Top: 25mm (accounting for running header).
  - Bottom: 20mm.
  - Left: 20mm.
  - Right: 20mm.

---

## 2. Typography

- Primary Typeface: Plus Jakarta Sans (clean, geometric humanist sans-serif).
- Fallbacks: Arial, Helvetica, sans-serif.
- Hierarchical Scale:
  - Document Title (H1): 22pt - 26pt, Bold (700), Color: #111111.
  - Eyebrow / Supertitle: 9pt - 10pt, Bold (700), All Caps, Tracking 1.5px, Color: #5454E9.
  - Section Titles (H2): 14pt - 16pt, Bold (700), Color: #000000.
  - Subsection Titles (H3): 12pt - 13pt, Semi-Bold (600), Color: #222222.
  - Body Text: 9.5pt - 10.5pt, Regular (400), Line Height: 1.45 - 1.5, Color: #222222.
  - Captions / Metadata Labels: 7.5pt - 8.5pt, Bold (700), All Caps, Color: #555555.
  - Metadata Values: 9pt - 10pt, Regular (400), Color: #111111.
  - Running Header / Page Numbers: 8pt - 9pt, Regular / Medium, Color: #88898C.

---

## 3. Structural Components

### 3.1 Running Header
Each page carries an official running header:
1. Left: Universidad Icesi Logo (height: ~16mm / 45px).
2. Vertical Separator: 1.5pt solid rule, Color: #CECDFD, height: 32px.
3. Center Information Block:
   - Line 1: `UNIVERSIDAD ICESI` (Bold, 8pt, tracking +0.5pt).
   - Line 2: `[DOCUMENT_TYPE]: [DOCUMENT_TITLE]` (Bold, 9pt).
   - Line 3: `Período: [PERIOD] · NRC: [NRC] · [EXTRA_METADATA]` (Regular, 8pt, muted dark gray).
4. Right: Page Counter `Pág. [CURRENT] de [TOTAL]` (Right aligned, 8pt, gray #88898C).
5. Accent Multi-Color Bar:
   - Spans 100% of the text width.
   - Thickness: 3pt.
   - Color distribution:
     - 65% Azul Icesi (#5454E9)
     - 15% Naranja Icesi (#E9683B)
     - 10% Verde Icesi (#4CB979)
     - 10% Lavanda Icesi (#CECDFD)
   - Followed by a 0.5pt subtle separator (#ECECF2).

### 3.2 Eyebrow and Main Title
At the start of the first page:
- Eyebrow (e.g., `GUÍA DE TALLER PRÁCTICO` or `CONSIGNA DE EVALUACIÓN`): uppercase, Azul Icesi (#5454E9).
- Main Title: Large bold text displaying workshop name.

### 3.3 Faculty and Department Identifiers
Small vertical pill banners preceding the institution entities:
- Faculty line preceded by a vertical blue bar (3pt x 12pt, #5454E9).
- Department line preceded by a vertical orange bar (3pt x 12pt, #E9683B).

### 3.4 Identification Metadata Grid
A tabular 2-column or 4-column structured grid:
- Heading preceded by vertical blue bar (#5454E9): `INFORMACIÓN DE LA ACTIVIDAD`.
- Grid cells contain uppercase label on left and value on right.
- Left-side accent line of the grid:
  - First row left border: Azul Icesi (#5454E9).
  - Second row left border: Verde Icesi (#4CB979).
- Vertical cell dividers: Light gray (#ECECF2) or accent color.

### 3.5 Section Headers with Number Boxes
Numbered sections feature an iconic design:
- A colored solid square box (#5454E9) containing the section number in bold white text (e.g., `[ 1 ]`, `[ 2 ]`).
- Section title text in bold black to the right of the box.
- A full-width horizontal rule beneath the entire section header block (1.5pt solid black/dark gray).

### 3.6 Tables and Rubrics
- Header row: Background #5454E9 with white bold uppercase text.
- Column borders: 0.5pt light gray (#ECECF2).
- Row striping: Alternating white and light gray (#F8F8FC) rows.
- Clear alignment: Left-aligned text, centered codes/percentages.

### 3.7 Diagrams, Images, and Code
- SVG and Mermaid Diagrams: Centered within content cards, bordered with 1pt #ECECF2.
- Code snippets: Sans-serif or Monospace (Fira Code, JetBrains Mono, Consolas) in light background (#F4F4F8) with subtle border (#DCDCE5).
- Callout boxes: Left border 4pt in accent color (Blue for Notes, Orange for Warnings, Green for Tips).
