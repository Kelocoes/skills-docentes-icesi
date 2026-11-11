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

## Empezar

Lee [`INSTALL.md`](INSTALL.md): instalar toma unos minutos y trae un ejemplo de pedido para cada skill.

## Buenas prácticas

- **Revisa todo lo que se publica.** La IA acelera, pero el contenido sigue siendo responsabilidad del profe (así lo pidieron los mismos estudiantes en la encuesta de percepción).
- **Declara el uso de IA** en tus materiales cuando aplique; la skill de talleres ya trae el campo de nivel de uso.
- **No subas datos de estudiantes** a las conversaciones con el asistente.
- Las credenciales de Saman van en un `.env` local que nunca se sube a git (ver `skills/saman-course-uploader/SKILL.md`, sección 1).

## Mejorar las skills

Cada skill tiene un archivo de lecciones o memoria (`references/`). Si encuentras un error o una mejora, pídele al asistente que la anote allí: así la siguiente persona no lo repite.
