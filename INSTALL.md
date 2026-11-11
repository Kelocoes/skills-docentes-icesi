# Instalación

## 1. Requisitos (una vez)

| Herramienta | Para qué | Cómo comprobar |
|---|---|---|
| [Claude Code](https://claude.com/claude-code) (u otro agente que lea `SKILL.md`) | El asistente que usa las skills | `claude --version` |
| Git | Clonar este repo | `git --version` |
| Python 3.10+ | Talleres, empaquetar piezas, Saman | `python --version` |
| Node.js 18+ | Slides y piezas | `node --version` |

Paquetes de Python:

```bash
pip install markdown-it-py pygments playwright
python -m playwright install chromium
```

## 2. Instalar las skills

```bash
git clone https://github.com/Kelocoes/skills-docentes-icesi.git
```

Elige **una** de dos opciones:

- **Para todos tus proyectos** (recomendado): copia las carpetas a tu carpeta personal de skills.

  ```bash
  # macOS / Linux / Git Bash
  mkdir -p ~/.claude/skills && cp -r skills-docentes-icesi/skills/* ~/.claude/skills/
  ```

  ```powershell
  # Windows PowerShell
  New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
  Copy-Item -Recurse skills-docentes-icesi\skills\* "$HOME\.claude\skills\"
  ```

- **Solo para un curso**: copia `skills/*` dentro de la carpeta del curso, en `.claude/skills/` (o en `.agents/skills/` si tu agente usa esa convención).

Para actualizar después: `git pull` en el repo y vuelve a copiar.

## 3. Comprobar

Abre una terminal en la carpeta de tu curso, ejecuta `claude` y pregunta:

```text
¿Qué skills tienes disponibles?
```

Deben aparecer `interactive-pieces`, `icesi-academic-workshops`, `slides-generator` y `saman-course-uploader`.

## 4. Primer pedido con cada skill

Escribe como le hablarías a un auxiliar. Ejemplos:

**Taller** (`icesi-academic-workshops`)
```text
Convierte taller-1.md en un taller de Icesi para el curso <curso>, NRC <nrc>, periodo 202620.
Nivel de uso de IA: colaboración. Rúbrica sobre 5.0 con tres criterios.
```
Resultado: `output-skills/icesi-academic-workshops/<fecha>/taller-1.html` y `.pdf`.

**Pieza interactiva** (`interactive-pieces`)
```text
Crea una pieza interactiva que explique paso a paso <concepto> para la semana 3.
El error común de los estudiantes es <error>. Déjala en piezas/semana-3/.
```
La skill pregunta lo que falte, construye la pieza y la prueba. Para Saman: `references/standalone-and-saman.md`.

**Presentación** (`slides-generator`)
```text
Quiero las slides de la semana 5 sobre <tema>, 25 diapositivas, para estudiantes de <semestre>.
```
Primero te entrevista y escribe un plan; **no construye hasta que lo apruebes**.

**Saman** (`saman-course-uploader`)
```text
Configura mi curso de Saman <nombre del curso> y publica la página semana-3.html como tema oculto en la Unidad 1.
```
La primera vez crea `.agents/output-skill/saman-course-uploader/` con la configuración del curso (a partir de `templates/*.example.yaml`). Inicias sesión en la ventana del navegador; el asistente no escribe tu contraseña si no lo autorizas explícitamente.

## Problemas frecuentes

- **El asistente no usa la skill:** nómbrala en el pedido ("usa la skill de talleres").
- **Error de Playwright o Chromium:** vuelve a ejecutar `python -m playwright install chromium`.
- **Las slides en PDF salen en blanco:** el PDF se exporta sirviendo el HTML por HTTP (`npx http-server`); la skill lo hace sola, no abras el HTML como archivo para exportar.
- **La pieza se ve oscura dentro de Saman:** empaquétala con `tools/bundle_piece.py --iframe` (fija el tema claro).
