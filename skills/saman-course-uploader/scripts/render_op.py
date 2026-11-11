"""Genera el JavaScript de una operacion de Saman ya con los valores del curso.

  python render_op.py --list                      operaciones, tipo y parametros
  python render_op.py <op> [--param valor ...]    imprime el JS listo (por stdout)
  python render_op.py <op> ... --out archivo.js   lo escribe a un archivo

Los parametros llevan el nombre del marcador en minusculas: --topic, --module, --dropbox, --file, --title,
--filename, --mime, --hidden, --desc-file. `--topic` y `--module` aceptan un alias de state.yaml
o un id numerico. Las operaciones destructivas (safety.confirm_before) exigen --confirm.
La descripcion de la operacion y el tipo (evaluate | run_code) salen por stderr.
"""
import argparse
import io
import json
import mimetypes
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import saman_config as cfgmod  # noqa: E402

OPS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ops.js")
HEADER = re.compile(r"^//### op: (?P<name>\S+) \| kind: (?P<kind>\S+) \| params: (?P<params>.*?) \| desc: (?P<desc>.*)$")
MARK = re.compile(r"\{\{([A-Z_]+)\}\}")


def parse_ops():
    ops, cur = {}, None
    with io.open(OPS_FILE, encoding="utf-8") as f:
        for line in f.read().splitlines():
            m = HEADER.match(line)
            if m:
                cur = dict(m.groupdict()); cur["body"] = []; ops[cur["name"]] = cur
            elif cur is not None:
                cur["body"].append(line)
    for o in ops.values():
        o["body"] = "\n".join(o["body"]).strip() + "\n"
    return ops


def globals_from(cfg):
    p, c, a = cfg["course"]["platform"], cfg["course"]["course"], cfg["course"].get("auth", {}).get("idp", {})
    return {
        "BASE_URL": p["base_url"].rstrip("/"), "OU": str(c["ou"]),
        "LP": p["api"]["lp"], "LE": p["api"]["le"],
        "ENFORCED": cfg["course"].get("storage", {}).get("enforced_folder", ""),
        "IDP_USER_SELECTOR": a.get("user_selector", ""), "IDP_PASSWORD_LABEL": a.get("password_label", ""),
        "IDP_SUBMIT_LABEL": a.get("submit_label", ""),
    }


def js_str(s):
    """Contenido seguro para ir dentro de comillas simples de JS."""
    return s.replace("\\", "/").replace("'", "\\'")


def main(argv=None):
    for s in (sys.stdout, sys.stderr):   # rutas con ñ y tildes: la consola de Windows usa cp1252 por defecto
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("op", nargs="?")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--confirm", action="store_true")
    for k in ("topic", "module", "dropbox", "file", "filename", "title", "mime", "hidden", "desc-file"):
        ap.add_argument("--" + k)
    a = ap.parse_args(argv)
    ops = parse_ops()

    if a.list or not a.op:
        for n, o in ops.items():
            print(f"{n:16} {o['kind']:9} {o['params']:40} {o['desc'][:90]}")
        return 0
    if a.op not in ops:
        sys.exit(f"Operacion desconocida: {a.op}. Ver --list")
    op = ops[a.op]

    cfg = cfgmod.load()
    errs = [e for e in cfgmod.validate(cfg) if not e.startswith("manifest.yaml")]
    if errs:
        sys.exit("Configuracion invalida:\n" + "\n".join(errs))
    safety = cfg["course"].get("safety", {})
    if a.op in (safety.get("confirm_before") or []) and not a.confirm:
        sys.exit(f"'{a.op}' esta en safety.confirm_before: pedir confirmacion al docente y repetir con --confirm "
                 "(respaldo previo con topic_html).")

    vals = globals_from(cfg)
    state = cfg.get("state") or {}

    def ident(v):
        if v is None:
            return None
        if re.fullmatch(r"\d+", v):
            return v
        try:
            return str(cfgmod.resolve(v, state)[1]["id"])
        except KeyError:
            sys.exit(f"'{v}' no es un id ni un alias de state.yaml (registrarlo con saman_config.py set-topic/set-module).")

    if a.topic: vals["TOPIC"] = ident(a.topic)
    if a.module: vals["MODULE"] = ident(a.module)
    if a.dropbox: vals["DROPBOX"] = ident(a.dropbox)
    if a.file:
        path = os.path.abspath(a.file)
        if not os.path.exists(path):
            sys.exit(f"No existe el archivo: {path}")
        vals["FILE"] = js_str(path.replace("\\", "/"))
        vals["FILENAME"] = js_str(a.filename or os.path.basename(path))
        vals["MIME"] = a.mime or mimetypes.guess_type(path)[0] or "application/octet-stream"
    vals["TITLE_JSON"] = json.dumps(a.title or "", ensure_ascii=False)
    vals["DESC_FILE"] = js_str(os.path.abspath(a.desc_file).replace("\\", "/")) if a.desc_file else ""
    default_hidden = bool(safety.get("default_hidden", True))
    vals["HIDDEN"] = ("true" if default_hidden else "false") if a.hidden is None else ("true" if a.hidden.lower() == "true" else "false")

    body = MARK.sub(lambda m: vals.get(m.group(1), m.group(0)), op["body"])
    missing = sorted(set(MARK.findall(body)))
    if missing:
        sys.exit(f"Faltan parametros para '{a.op}': " + ", ".join("--" + m.lower().replace("_", "-") for m in missing)
                 + f"  (params: {op['params']})")

    desc = MARK.sub(lambda m: vals.get(m.group(1), m.group(0)), op["desc"])
    sys.stderr.write(f"[{a.op}] {op['kind']}: {desc}\n")
    if a.out:
        with io.open(a.out, "w", encoding="utf-8", newline="\n") as f:
            f.write(body)
        sys.stderr.write(f"escrito {a.out}\n")
    else:
        sys.stdout.write(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
