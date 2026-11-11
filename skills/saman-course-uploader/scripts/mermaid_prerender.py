"""Prerenderiza los bloques ```mermaid de un .md a SVG usando el navegador de Playwright MCP.

Uso:
    python mermaid_prerender.py <manual.md> <carpeta_salida>      # deja el servidor corriendo (Ctrl+C / matar el proceso al terminar)
Luego, con el MCP: browser_navigate a http://127.0.0.1:8765/render.html, browser_wait_for "DONE" y comprobar que no haya "ERR".
Los SVG quedan en <carpeta_salida>/01.svg, 02.svg ... en orden de aparicion; copiarlos al repo como mermaid_NN.svg
(p. ej. body_of_knowledge/saman/build/assets/paso_03_1/) y pasarlos a md_to_saman(md, mermaid_svgs=[...]).
Mermaid se carga desde cdn.jsdelivr.net (version fija); la fuente es Arial para que el ancho del texto sea igual dentro de <img>.
"""
import http.server
import json
import os
import re
import sys
import urllib.parse

md_path, out_dir = sys.argv[1], os.path.abspath(sys.argv[2])
os.makedirs(os.path.join(out_dir, "mm"), exist_ok=True)
blocks = re.findall(r"```mermaid\n(.*?)```", open(md_path, encoding="utf-8").read(), re.S)
json.dump(blocks, open(os.path.join(out_dir, "mm", "blocks.json"), "w", encoding="utf-8"), ensure_ascii=False)
open(os.path.join(out_dir, "render.html"), "w", encoding="utf-8").write("""<!doctype html><meta charset="utf-8"><body><div id="out"></div>
<script type="module">
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.esm.min.mjs';
mermaid.initialize({startOnLoad:false, theme:'base', securityLevel:'loose', themeVariables:{primaryColor:'#CECDFD',primaryTextColor:'#111111',primaryBorderColor:'#5454E9',lineColor:'#5454E9',secondaryColor:'#F8F8FC',tertiaryColor:'#FFFFFF',fontSize:'15px',fontFamily:'Arial, Helvetica, sans-serif'}});
const blocks = await (await fetch('/mm/blocks.json')).json();
const res = [];
for (let i=0;i<blocks.length;i++){
  try { const {svg} = await mermaid.render('m'+i, blocks[i]);
    await fetch('/save?name='+String(i+1).padStart(2,'0')+'.svg', {method:'POST', body:svg}); res.push('ok '+(i+1)); }
  catch(e){ res.push('ERR '+(i+1)+' '+e.message); }
}
document.getElementById('out').textContent = 'DONE ' + res.join(' | ');
</script>""")
print(len(blocks), "bloques; sirviendo en http://127.0.0.1:8765/render.html")


class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=out_dir, **k)

    def do_POST(self):
        name = os.path.basename(urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)["name"][0])
        data = self.rfile.read(int(self.headers["Content-Length"]))
        open(os.path.join(out_dir, name), "wb").write(data)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")


http.server.ThreadingHTTPServer(("127.0.0.1", 8765), H).serve_forever()
