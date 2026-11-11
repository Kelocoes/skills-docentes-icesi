# Skills docentes Icesi

Cuatro *skills* para que un asistente de IA (Claude Code u otro agente que lea `SKILL.md`) prepare material de clase con la marca Icesi, un proceso pedagógico y herramientas ya probadas en cursos reales.

Presentado en **Los profes cuentan** (18 de noviembre de 2026).

## ¿Qué es una skill?

Una carpeta que el asistente lee **antes** de trabajar:

```text
mi-skill/
  SKILL.md       instrucciones en lenguaje natural: cuándo usarla y paso a paso
  references/    la memoria: reglas de marca, errores ya cometidos, catálogos
  scripts/       herramientas que se ejecutan igual siempre
  templates/     moldes listos para llenar
```

Sin skill, el asistente responde con lo que sabe en general: cada resultado sale con otro estilo y hay que corregirlo a mano. Con la skill, trabaja como un auxiliar que ya conoce el formato institucional, los componentes disponibles y los errores que no debe repetir. **El profe sigue revisando y decidiendo**: varias skills se detienen a pedir aprobación antes de construir o publicar.

## Las skills

| Skill | Qué hace | Entrada | Salida |
|---|---|---|---|
| [`interactive-pieces`](skills/interactive-pieces/SKILL.md) | Convierte un concepto o un gráfico estático en una **pieza interactiva** paso a paso (protocolos, flujos, arquitecturas, estado). Decide primero qué error del estudiante evita; luego arma la pieza con un kit de motores probados y la prueba en un navegador real. | Un tema, un capítulo o un gráfico | Una carpeta `index.html` que se abre sola, se embebe en un sitio o se empaqueta para Saman |
| [`icesi-academic-workshops`](skills/icesi-academic-workshops/SKILL.md) | Talleres, guías, exámenes y rúbricas con la **imagen institucional**: encabezado con logo en cada página, metadatos, rúbrica sobre 5.0 y nivel de uso de IA declarado. | Markdown, Word, PDF o texto | HTML y PDF listos para publicar o imprimir |
| [`slides-generator`](skills/slides-generator/SKILL.md) | Presentaciones Reveal.js con la marca Icesi en **dos fases**: entrevista y plan (que el profe aprueba) y luego construcción. | Un tema y una conversación | HTML (animable, con piezas y video) y PDF |
| [`saman-course-uploader`](skills/saman-course-uploader/SKILL.md) | **Publica en Saman** (Brightspace) páginas, archivos y piezas embebidas, controlando el navegador. Lee antes de escribir, crea lo nuevo **oculto**, compara lo publicado con lo local y nunca toca calificaciones ni inscripciones. | Tu material y la configuración de tu curso | Temas y módulos en tu curso de Saman |

Cómo se conectan:

```text
tema de clase ──► interactive-pieces ──► pieza .html ──┐
             ──► icesi-academic-workshops ──► taller PDF ─┼──► saman-course-uploader ──► Saman
             ──► slides-generator ──► slides HTML/PDF ───┘
```

## Cómo usarlo

### 1. Instalar (una vez)

Necesitas [Claude Code](https://claude.com/claude-code), Git, Python 3.10+ y Node.js 18+.

```bash
git clone https://github.com/Kelocoes/skills-docentes-icesi.git
pip install markdown-it-py pygments playwright
python -m playwright install chromium

# Copia las skills a tu carpeta personal (macOS / Linux / Git Bash)
mkdir -p ~/.claude/skills && cp -r skills-docentes-icesi/skills/* ~/.claude/skills/
```

En Windows PowerShell la copia es:

```powershell
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse skills-docentes-icesi\skills\* "$HOME\.claude\skills\"
```

> El repositorio es privado: pide acceso al autor antes de clonarlo.

### 2. Abrir el asistente en la carpeta de tu curso

```bash
cd mi-curso
claude
```

Comprueba que las ve: *"¿Qué skills tienes disponibles?"*

### 3. Pedir en español, como a un auxiliar

| Quiero… | Escribe algo como | Obtienes |
|---|---|---|
| Un taller o examen | *Convierte taller-1.md en un taller de Icesi para el curso X, NRC 12345. Uso de IA: colaboración.* | `taller-1.html` y `taller-1.pdf` con la marca Icesi |
| Una pieza interactiva | *Crea una pieza que explique paso a paso cómo viaja una petición HTTP. El error común es creer que el servidor recuerda al cliente.* | Una carpeta `index.html` que se abre con doble clic |
| La pieza dentro de Saman | *Empaqueta la pieza para pegarla en una página de Saman.* | Un solo HTML o un `<iframe srcdoc>` (tema claro) |
| Las slides de una semana | *Quiero las slides de la semana 5 sobre patrones creacionales, 25 diapositivas.* | Primero un plan para aprobar; luego HTML y PDF |
| Publicar en Saman | *Publica semana-3.html como tema oculto en la Unidad 1 de mi curso.* | El tema creado oculto, verificado contra el archivo local |

Consejos:

- Si el asistente no usa la skill, nómbrala: *"usa la skill de talleres"*.
- Revisa siempre el resultado antes de publicarlo; las skills de slides y Saman se detienen a pedir tu aprobación.
- Para Saman, la primera vez el asistente te guía para crear la configuración de tu curso, y tú inicias sesión en la ventana del navegador.

Detalles, requisitos y problemas frecuentes: [`INSTALL.md`](INSTALL.md). Cómo usar piezas sin sitio web o dentro de Saman: [`skills/interactive-pieces/references/standalone-and-saman.md`](skills/interactive-pieces/references/standalone-and-saman.md).

## Buenas prácticas

- **Revisa todo lo que se publica.** La IA acelera, pero el contenido sigue siendo responsabilidad del profe (así lo pidieron los mismos estudiantes en la encuesta de percepción).
- **Declara el uso de IA** en tus materiales cuando aplique; la skill de talleres ya trae el campo de nivel de uso.
- **No subas datos de estudiantes** a las conversaciones con el asistente.
- Las credenciales de Saman van en un `.env` local que nunca se sube a git (ver `skills/saman-course-uploader/SKILL.md`, sección 1).

## Mejorar las skills

Cada skill tiene un archivo de lecciones o memoria (`references/`). Si encuentras un error o una mejora, pídele al asistente que la anote allí: así la siguiente persona no lo repite.
