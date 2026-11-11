---
name: slides-generator
description: Universidad Icesi Reveal.js slide presentation generator — Master orchestrator for two-phase interactive planning (planning-slides) and presentation implementation (implement-slides).
category: software-dev
---

# Skill: `slides-generator`

## Overview
This skill acts as the **master orchestrator** for creating institutional, brand-compliant slide presentations (powered by Reveal.js + Icesi Design System) and exporting them to PDF slide decks.

The presentation generation process is strictly divided into **2 distinct, sequential phases**. The agent MUST read and apply the instructions from the respective reference documentation and sub-skills before executing each phase.

---

## Required Reference Documentation & Sub-Skills Architecture

The master orchestrator relies on authoritative reference manuals and auxiliary sub-skills located under `skills/slides-generator/references/`:

### Core Manuals (MUST be inspected by agent):
- **`memory.md`** (`skills/slides-generator/references/memory.md`): Historical log, slide layout classification (Covers, Dividers, Sidebars, Cards), and contrast fixes.
- **`formatting_rules.md`** (`skills/slides-generator/references/formatting_rules.md`): Strict CSS pixel bounds (1280x720), typography hierarchy, safe margin limits, and density constraints.

### Auxiliary Sub-Skills:
1. **`planning-slides`** (`skills/slides-generator/references/skills/planning-slides/SKILL.md`): Auxiliary skill for Phase 1. Guides discovery, wayfinding, pedagogical critique, and spec plan generation.
2. **`implement-slides`** (`skills/slides-generator/references/skills/implement-slides/SKILL.md`): Auxiliary skill for Phase 2. Assembles HTML slides from component catalog and exports PDF via Decktape.
3. **`slides-iconification`** (`skills/slides-generator/references/skills/slides-iconification/SKILL.md`): Auxiliary skill for semantic SVG icons (strictly no emojis).
4. **`slides-svg-graphics`** (`skills/slides-generator/references/skills/slides-svg-graphics/SKILL.md`): Auxiliary skill for raw SVG infographics and sidebar graphics.
5. **`slides-mermaid-diagrams`** (`skills/slides-generator/references/skills/slides-mermaid-diagrams/SKILL.md`): Auxiliary skill for sequence and flowchart diagrams.

---

## Output Directory Hygiene Rules

All execution outputs MUST be initialized using the automated helper script:
```powershell
powershell -ExecutionPolicy Bypass -File <skill>/scripts/init_skill_output.ps1 -SkillName "slides-generator" -ExecutedBy "<UserOrAgent>" -Prompt "<OriginalPrompt>"
```

On macOS or Linux: `bash <skill>/scripts/init_skill_output.sh slides-generator "<UserOrAgent>" "<OriginalPrompt>"`.
`<skill>` is the folder of this skill (for example `~/.claude/skills/slides-generator`). Run it from the folder where you want `output-skills/` to be created.

The output directory `output-skills/slides-generator/[MM-DD-YYYY]_[counter]/` MUST contain ONLY the necessary operational files:
- `spec/<topic>-plan.md` — Specification plan generated during Phase 1.
- `slides/<topic>/<topic>.html` — Reveal.js HTML presentation generated during Phase 2.
- `slides/<topic>/<topic>.pdf` — Compiled high-resolution PDF slide deck generated during Phase 2.
- `dist/main.js` & `dist/main.css` — Bundled JS/CSS dependencies with embedded official SVG logos.
- `INFO.md` — Execution metadata log.

Do NOT copy unreferenced assets, temporary scripts, or scratch files into the output directory.

---

## Two-Phase Workflow & Execution Instructions

### Phase 1: Planning & Specification Approval (Mandatory Pause)

1. **Initialize Output Directory**:
   - Run `init_skill_output.ps1` to establish `TARGET_DIR` (`output-skills/slides-generator/[MM-DD-YYYY]_[counter]/`).

2. **Targeted Documentation Inspection for Phase 1 (Lazy Reading)**:
   - The agent **MUST** inspect ONLY:
     - `skills/slides-generator/references/skills/planning-slides/SKILL.md`
     - `skills/slides-generator/references/formatting_rules.md` (only if verifying canvas sizes/margins)

3. **Execute Streamlined Planning & Concise Spec Creation**:
   - Conduct interactive discovery (learning objectives, target audience, scope boundaries).
   - Apply pedagogical critique: self-contained slides, zero emojis, explicit visual choices.
   - Write a **concise structural specification plan** (mapping Topic, Slide Title, Layout Function Name, and bullet points/code pseudocódigo) strictly under `<TARGET_DIR>/spec/<topic>-plan.md`. Do NOT draft full raw HTML or massive inline SVGs inside the plan document to minimize token consumption.

4. **Present Spec Artifact & MANDATORY STOP**:
   - Present the generated specification plan as a markdown artifact for user review.
   - **MANDATORY STOP**: The agent **MUST STOP** and wait for the user to analyze, refine, or explicitly approve the specification plan.
   - **Do NOT proceed to Phase 2 (HTML/PDF generation) until the user gives explicit feedback or approval.**

---

### Phase 2: Implementation & PDF Export (After User Approval)

5. **Targeted Documentation Inspection for Phase 2 (Lazy Reading)**:
   - Upon receiving user approval, the agent **MUST** inspect ONLY the skills required for the target presentation:
     - `skills/slides-generator/references/skills/implement-slides/SKILL.md`
     - `skills/slides-generator/references/skills/slides-iconification/SKILL.md`
     - `skills/slides-generator/references/skills/slides-svg-graphics/SKILL.md` (ONLY if custom complex SVG graphics are needed)
     - `skills/slides-generator/references/skills/slides-mermaid-diagrams/SKILL.md` (ONLY if Mermaid sequence diagrams are present)

6. **Assemble HTML Presentation**:
   - Verify that `dist/main.js` and `dist/main.css` are in place in `<TARGET_DIR>/dist/` (with embedded official SVG logos).
   - Generate `<TARGET_DIR>/slides/<topic>/<topic>.html` using the catalog- **Content**: `icesi.slideStandard`, `icesi.slideTwoCols`, `icesi.slideThreeCols`, `icesi.slideTwoCards`, `icesi.slideThreeCards`, `icesi.slideFourCards`, `icesi.slideCards(title, cardsArray)`
- **Dynamic Cards Rule**: Avoid overusing 4-card grids when 2 or 3 cards or custom column layouts fit better. `slideTwoCards`, `slideThreeCards`, and `slideCards` support flexible card counts and embedded inline SVG icons in card headers.
- **Pedagogical Depth & Coherence Rule**: Never compress multiple rich documentation files into a sparse summary deck. Expand slides naturally (25–35+ slides) so each concept is explained step-by-step with concrete code examples, custom Raw SVG diagrams, and high-contrast styling without gaps., `slideSidebarLeftBlue`, etc.).

7. **Export PDF Deck**:
   - Serve over HTTP and run Decktape against the HTML presentation:
     ```powershell
     npx -y http-server . -p 8085 -s
     npx -y decktape reveal --load-pause 2000 "http://localhost:8085/<TARGET_DIR>/slides/<topic>/<topic>.html" "<TARGET_DIR>/slides/<topic>/<topic>.pdf" --size 1280x720
     ```

8. **Clean Output Verification**:
   - Terminate `http-server`, update `INFO.md`, and verify that only `spec/`, `slides/`, `dist/`, and `INFO.md` remain in `<TARGET_DIR>/`.

---

## Requirements and Prerequisites

- Node.js & npm (`npx` support for Decktape PDF export).
- Embedded brand logos (`resources/logos/`) and fonts (`PlusJakartaSans`).
