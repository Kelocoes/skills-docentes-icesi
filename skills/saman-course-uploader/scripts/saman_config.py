"""Carga y valida la configuracion de un curso para la skill saman-course-uploader.

Los datos del curso viven FUERA de la skill, en `<repo>/.agents/output-skill/saman-course-uploader/`:
  course.yaml    configuracion estable (OU, rutas, tema, seguridad)   -> la edita una persona
  manifest.yaml  que fuente local se publica y donde                  -> la decide el docente
  state.yaml     IDs creados (modulos, temas, tareas)                 -> lo escribe el agente
  log.md         bitacora cronologica (solo se agregan filas)

Uso desde la linea de comandos (desde cualquier carpeta del repo):
  python saman_config.py init [--repo RAIZ]        crea la carpeta de datos con las plantillas (curso nuevo)
  python saman_config.py where                     ruta de la carpeta de datos
  python saman_config.py validate                  revisa los tres YAML y sus referencias cruzadas
  python saman_config.py show                      resumen sin secretos
  python saman_config.py resolve <alias>           id (y modulo) de un modulo, tema o dropbox
  python saman_config.py set-module <alias> <id> [titulo]
  python saman_config.py set-topic <alias> <id> <modulo> <kind> [--url U] [--hidden]
  python saman_config.py set-dropbox <alias> <id> [topic]
  python saman_config.py log "<accion>" "<ids>"    agrega una fila a log.md

Uso como modulo:
  from saman_config import load, resolve
"""
import argparse
import datetime
import io
import os
import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("Falta PyYAML: pip install pyyaml")

DATA_SUBPATH = os.path.join(".agents", "output-skill", "saman-course-uploader")
ENV_OVERRIDE = "SAMAN_COURSE_DIR"
FILES = ("course", "manifest", "state")


def find_dir(start=None):
    """Busca la carpeta de datos subiendo desde `start` (o el cwd). SAMAN_COURSE_DIR la fija a mano."""
    if os.environ.get(ENV_OVERRIDE):
        return os.path.abspath(os.environ[ENV_OVERRIDE])
    cur = os.path.abspath(start or os.getcwd())
    while True:
        cand = os.path.join(cur, DATA_SUBPATH)
        if os.path.isdir(cand):
            return cand
        parent = os.path.dirname(cur)
        if parent == cur:
            raise FileNotFoundError(
                f"No hay {DATA_SUBPATH} en {start or os.getcwd()} ni en sus padres. "
                "Copiar templates/*.example.yaml alli o fijar SAMAN_COURSE_DIR.")
        cur = parent


def repo_root(data_dir=None):
    d = data_dir or find_dir()
    for _ in range(3):
        d = os.path.dirname(d)
    return d


def _read(path):
    with io.open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load(name=None, start=None):
    """load('course') -> dict; load() -> {'course':..., 'manifest':..., 'state':...} (los que existan)."""
    d = find_dir(start)
    names = [name] if name else FILES
    out = {}
    for n in names:
        p = os.path.join(d, n + ".yaml")
        if os.path.exists(p):
            out[n] = _read(p)
        elif name:
            raise FileNotFoundError(p)
    return out[name] if name else out


def _write_state(state, d):
    p = os.path.join(d, "state.yaml")
    state["refreshed"] = datetime.date.today().isoformat()
    header = ("# Estado de Saman: IDs creados y su relacion con el repo.\n"
              "# Lo escribe el agente (saman_config.py set-*). La historia esta en log.md.\n")
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(header)
        yaml.safe_dump(state, f, allow_unicode=True, sort_keys=False, default_flow_style=None, width=120)


def resolve(alias, state=None):
    """Devuelve (kind, entrada) para un alias de modulo, tema o dropbox."""
    st = state or load("state")
    for kind, key in (("module", "modules"), ("topic", "topics"), ("dropbox", "dropboxes")):
        if alias in (st.get(key) or {}):
            return kind, st[key][alias]
    raise KeyError(f"Alias desconocido: {alias}")


def validate(cfg=None):
    """Devuelve una lista de problemas (vacia = correcto)."""
    cfg = cfg or load()
    errs = []
    course = cfg.get("course")
    if not course:
        return ["Falta course.yaml"]
    c = course.get("course", {})
    for k in ("ou", "name"):
        if not c.get(k):
            errs.append(f"course.yaml: falta course.{k}")
    if not course.get("platform", {}).get("base_url"):
        errs.append("course.yaml: falta platform.base_url")
    if c.get("ou") in (c.get("protected_courses") or []):
        errs.append("course.yaml: el curso objetivo esta en protected_courses")
    st = cfg.get("state") or {}
    if st and st.get("course_ou") not in (None, c.get("ou")):
        errs.append(f"state.yaml: course_ou {st.get('course_ou')} no coincide con course.ou {c.get('ou')}")
    mods, tops, dbs = (st.get("modules") or {}), (st.get("topics") or {}), (st.get("dropboxes") or {})
    ids = {}
    for key, group in (("modules", mods), ("topics", tops), ("dropboxes", dbs)):
        for a, e in group.items():
            if not isinstance(e.get("id"), int):
                errs.append(f"state.yaml: {key}.{a} sin id numerico")
            elif key != "dropboxes":
                if (key, e["id"]) in ids:
                    errs.append(f"state.yaml: id {e['id']} repetido en {key} ({ids[(key, e['id'])]} y {a})")
                ids[(key, e["id"])] = a
    for a, e in tops.items():
        if e.get("module") not in mods:
            errs.append(f"state.yaml: topics.{a} apunta al modulo desconocido '{e.get('module')}'")
    man = cfg.get("manifest") or {}
    for it in man.get("items") or []:
        a, t = it.get("alias"), it.get("type")
        if t not in ("module_description", "page", "file", "assignment"):
            errs.append(f"manifest.yaml: {a}: tipo desconocido '{t}'")
        if t in ("page", "file", "assignment") and a not in tops:
            errs.append(f"manifest.yaml: {a} no existe en state.yaml (aun sin publicar; crearlo y registrar el ID)")
    root = repo_root()
    src = os.path.join(root, course.get("paths", {}).get("source_dir", ""))
    for it in man.get("items") or []:
        s = it.get("source", "")
        if s and not s.startswith("(") and not os.path.exists(os.path.join(src, s)):
            errs.append(f"manifest.yaml: {it.get('alias')}: no existe la fuente {s}")
    return errs


def _log(action, ids):
    p = os.path.join(find_dir(), "log.md")
    row = f"| {datetime.date.today().isoformat()} | {action.replace('|', '/')} | {ids} |\n"
    with io.open(p, "a", encoding="utf-8", newline="\n") as f:
        f.write(row)


def init(repo):
    """Copia templates/*.example.yaml a <repo>/.agents/output-skill/saman-course-uploader/ sin pisar nada."""
    import shutil
    tpl = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")
    dest = os.path.join(os.path.abspath(repo), DATA_SUBPATH)
    os.makedirs(dest, exist_ok=True)
    for n in FILES:
        target = os.path.join(dest, n + ".yaml")
        if os.path.exists(target):
            print(f"ya existe, no se toca: {target}")
        else:
            shutil.copyfile(os.path.join(tpl, n + ".example.yaml"), target)
            print(f"creado: {target}")
    log = os.path.join(dest, "log.md")
    if not os.path.exists(log):
        nl = chr(10)
        with io.open(log, "w", encoding="utf-8", newline=nl) as f:
            f.write(nl.join(["# Bitacora de Saman", "", "Solo se agregan filas (saman_config.py log).", "",
                             "| Fecha | Accion | IDs |", "| :--- | :--- | :--- |", ""]))
        print(f"creado: {log}")
    print("Siguiente paso: completar course.yaml, ejecutar la operacion `discover` y registrar IDs con set-module/set-topic.")


def main(argv=None):
    for s in (sys.stdout, sys.stderr):   # rutas con ñ y tildes: la consola de Windows usa cp1252 por defecto
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("init"); i.add_argument("--repo", default=os.getcwd())
    sub.add_parser("where")
    sub.add_parser("validate")
    sub.add_parser("show")
    r = sub.add_parser("resolve"); r.add_argument("alias")
    m = sub.add_parser("set-module"); m.add_argument("alias"); m.add_argument("id", type=int); m.add_argument("title", nargs="?", default="")
    t = sub.add_parser("set-topic"); t.add_argument("alias"); t.add_argument("id", type=int)
    t.add_argument("module"); t.add_argument("kind", choices=["page", "file", "assignment", "link"])
    t.add_argument("--url"); t.add_argument("--hidden", action="store_true")
    d = sub.add_parser("set-dropbox"); d.add_argument("alias"); d.add_argument("id", type=int); d.add_argument("topic", nargs="?")
    lg = sub.add_parser("log"); lg.add_argument("action"); lg.add_argument("ids", nargs="?", default="-")
    a = ap.parse_args(argv)

    if a.cmd == "init":
        init(a.repo); return 0
    if a.cmd == "where":
        print(find_dir()); return 0
    if a.cmd == "validate":
        errs = validate()
        print("OK" if not errs else "\n".join(errs)); return 1 if errs else 0
    if a.cmd == "show":
        cfg = load(); c = cfg["course"]
        print(f"curso {c['course']['ou']} - {c['course']['name']} @ {c['platform']['base_url']}")
        st = cfg.get("state") or {}
        print(f"modulos: {len(st.get('modules') or {})}  temas: {len(st.get('topics') or {})}  dropboxes: {len(st.get('dropboxes') or {})}")
        print(f"manifest: {len((cfg.get('manifest') or {}).get('items') or [])} elementos"); return 0
    if a.cmd == "resolve":
        print(yaml.safe_dump({a.alias: resolve(a.alias)[1]}, allow_unicode=True, default_flow_style=True).strip()); return 0

    d_ = find_dir(); st = load("state")
    if a.cmd == "set-module":
        st.setdefault("modules", {})[a.alias] = {"id": a.id, **({"title": a.title} if a.title else {})}
    elif a.cmd == "set-topic":
        e = {"id": a.id, "module": a.module, "kind": a.kind}
        if a.url: e["url"] = a.url
        if a.hidden: e["hidden"] = True
        st.setdefault("topics", {})[a.alias] = e
    elif a.cmd == "set-dropbox":
        e = {"id": a.id}
        if a.topic: e["topic"] = a.topic
        st.setdefault("dropboxes", {})[a.alias] = e
    elif a.cmd == "log":
        _log(a.action, a.ids); print("fila agregada a log.md"); return 0
    _write_state(st, d_)
    print("state.yaml actualizado"); return 0


if __name__ == "__main__":
    sys.exit(main())
