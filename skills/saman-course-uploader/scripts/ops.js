// Operaciones de Saman (Brightspace / D2L) como plantillas para el MCP de Playwright.
// NO se pegan a mano: `python render_op.py <op> --param valor` sustituye los {{MARCADORES}}
// con la configuracion del curso (.agents/output-skill/saman-course-uploader/) y escribe el JS listo.
//
// Formato: cada operacion empieza con una linea "//### op: <nombre> | kind: evaluate|run_code | params: A,B | desc: ..."
//   kind evaluate -> pegar en browser_evaluate;  kind run_code -> pegar en browser_run_code_unsafe.
// Marcadores globales: {{BASE_URL}} {{OU}} {{LP}} {{LE}} {{ENFORCED}} {{IDP_USER_SELECTOR}} {{IDP_PASSWORD_LABEL}} {{IDP_SUBMIT_LABEL}}
// Marcadores de parametro: {{TOPIC}} {{MODULE}} {{FILE}} ... y {{TITLE_JSON}} (titulo ya escapado como cadena JS).
// Todo lo que escribe usa el header X-Csrf-Token tomado de localStorage['XSRF.Token'].

//### op: whoami | kind: evaluate | params: - | desc: 200 = sesion activa; si redirige o falla, repetir el login
async () => (await fetch('{{BASE_URL}}/d2l/api/lp/{{LP}}/users/whoami')).status

//### op: login | kind: run_code | params: - | desc: login por codigo en la pantalla del IdP. Sustituir <USER> y <PASSWORD> leyendo el .env (Read); no escribirlos en archivos versionados ni repetirlos en respuestas
async (page) => {
  await page.locator('{{IDP_USER_SELECTOR}}').fill('<USER>');
  await page.getByRole('textbox', { name: '{{IDP_PASSWORD_LABEL}}' }).fill('<PASSWORD>');
  await page.getByRole('button', { name: '{{IDP_SUBMIT_LABEL}}' }).click();
  await page.waitForURL(/\/d2l\//, { timeout: 30000 });
  return await page.evaluate(async () => (await fetch('/d2l/api/lp/{{LP}}/users/whoami')).status);
}

//### op: my_courses | kind: evaluate | params: - | desc: cursos de la cuenta (confirmar que el OU del curso es el correcto antes de escribir)
async () => (await (await fetch('/d2l/api/lp/{{LP}}/enrollments/myenrollments/?pageSize=100')).json())
  .Items.map(i => ({id: i.OrgUnit.Id, name: i.OrgUnit.Name, type: i.OrgUnit.Type.Code}))

//### op: check_course | kind: evaluate | params: - | desc: devuelve nombre y OU del curso configurado; compararlos con course.yaml antes de cualquier escritura
async () => { const r = await fetch('/d2l/api/lp/{{LP}}/courses/{{OU}}'); const c = r.ok ? await r.json() : {};
  return {status: r.status, ou: c.Identifier || c.OrgUnitId, name: c.Name, code: c.Code}; }

//### op: toc | kind: evaluate | params: - | desc: arbol de modulos y temas sin las descripciones HTML
async () => {
  const t = await (await fetch('/d2l/api/le/{{LE}}/{{OU}}/content/toc')).json();
  const f = m => ({id: m.ModuleId, title: m.Title, hidden: m.IsHidden,
    topics: m.Topics.map(x => ({id: x.TopicId, title: x.Title, hidden: x.IsHidden, type: x.TopicType, url: x.Url, activity: x.ActivityId})),
    modules: m.Modules.map(f)});
  return t.Modules.map(f);
}

//### op: discover | kind: evaluate | params: - | desc: datos para llenar course.yaml y state.yaml sin explorar la UI: curso, versiones de API, carpeta /content/enforced/, modulos, temas y tareas
async () => {
  const j = async u => { const r = await fetch(u); return r.ok ? r.json() : {error: r.status, url: u}; };
  const info = await j('/d2l/api/lp/{{LP}}/courses/{{OU}}');
  const versions = await j('/d2l/api/versions/');
  const toc = await j('/d2l/api/le/{{LE}}/{{OU}}/content/toc');
  const folders = await j('/d2l/api/le/{{LE}}/{{OU}}/dropbox/folders/');
  const topics = [], mods = [];
  const walk = (m, parent) => { mods.push({id: m.ModuleId, parent, title: m.Title, hidden: m.IsHidden});
    m.Topics.forEach(x => topics.push({id: x.TopicId, module: m.ModuleId, title: x.Title, type: x.TopicType, hidden: x.IsHidden, url: x.Url, activity: x.ActivityId}));
    m.Modules.forEach(s => walk(s, m.ModuleId)); };
  (toc.Modules || []).forEach(m => walk(m, null));
  const enforced = [...new Set(topics.map(t => (t.url || '').match(/^\/content\/enforced\/[^\/]+/)).filter(Boolean).map(m => m[0]))];
  const vs = (Array.isArray(versions) ? versions : versions.Versions || []).filter(v => ['lp', 'le'].includes(v.ProductCode)).map(v => v.ProductCode + ' ' + v.LatestVersion);
  const who = await j('/d2l/api/lp/{{LP}}/users/whoami');
  const org = await j('/d2l/api/lp/{{LP}}/organization/info');
  const enr = await j('/d2l/api/lp/{{LP}}/enrollments/myenrollments/{{OU}}');
  return {user_id: who.Identifier, org: {ou: org.Identifier, name: org.Name, timezone: org.TimeZone}, role: enr.Access && enr.Access.ClasslistRoleName,
    course: {ou: info.Identifier, name: info.Name, code: info.Code, template: info.CourseTemplate && info.CourseTemplate.Name, storage_path: info.Path},
    versions: vs, enforced_folders: enforced, modules: mods, topics,
    dropboxes: Array.isArray(folders) ? folders.map(f => ({id: f.Id, name: f.Name, hidden: f.IsHidden, due: f.DueDate, gradeItem: f.GradeItemId})) : folders};
}

//### op: topic_html | kind: evaluate | params: TOPIC | desc: HTML publicado de un tema (leer antes de reemplazar o borrar; sirve de respaldo). Devuelve el texto completo
async () => (await fetch('/d2l/api/le/{{LE}}/{{OU}}/content/topics/{{TOPIC}}/file')).text()

//### op: topic_info | kind: evaluate | params: TOPIC | desc: metadatos de un tema (Url vigente, visibilidad, tipo, IsBroken)
async () => { const t = await (await fetch('/d2l/api/le/{{LE}}/{{OU}}/content/topics/{{TOPIC}}')).json();
  return {id: t.Id, title: t.Title, url: t.Url, hidden: t.IsHidden, type: t.TopicType, broken: t.IsBroken, activity: t.ActivityId}; }

//### op: create_module | kind: run_code | params: TITLE, DESC_FILE(opcional), HIDDEN(true por defecto) | desc: crea un modulo raiz. Devuelve el Id para registrarlo en state.yaml
async (page) => {
  const descPath = '{{DESC_FILE}}';
  if (descPath) { await page.evaluate(() => { const i = document.createElement('input'); i.type = 'file'; i.id = 'tmpdesc'; document.body.appendChild(i); });
    await page.setInputFiles('#tmpdesc', descPath); }
  return await page.evaluate(async () => {
    const H = {'X-Csrf-Token': localStorage.getItem('XSRF.Token'), 'Content-Type': 'application/json'};
    const f = document.getElementById('tmpdesc');
    const desc = f && f.files[0] ? await f.files[0].text() : '<p></p>';
    const body = {Title: {{TITLE_JSON}}, ShortTitle: '', Type: 0, ModuleStartDate: null, ModuleEndDate: null, ModuleDueDate: null,
      IsHidden: {{HIDDEN}}, IsLocked: false, Description: {Content: desc, Type: 'Html'}, Duration: null};
    const r = await fetch('/d2l/api/le/{{LE}}/{{OU}}/content/root/', {method: 'POST', headers: H, body: JSON.stringify(body)});
    const m = await r.json();
    return {status: r.status, id: m.Id, title: m.Title, hidden: m.IsHidden};
  });
}

//### op: edit_module | kind: run_code | params: MODULE, TITLE, DESC_FILE(opcional) | desc: cambia titulo y/o descripcion de un modulo conservando visibilidad y fechas (GET previo). Sin DESC_FILE conserva la descripcion. TITLE vacio conserva el titulo
async (page) => {
  const descPath = '{{DESC_FILE}}';
  if (descPath) { await page.evaluate(() => { const i = document.createElement('input'); i.type = 'file'; i.id = 'tmpdesc'; document.body.appendChild(i); });
    await page.setInputFiles('#tmpdesc', descPath); }
  return await page.evaluate(async () => {
    const H = {'X-Csrf-Token': localStorage.getItem('XSRF.Token'), 'Content-Type': 'application/json'};
    const u = '/d2l/api/le/{{LE}}/{{OU}}/content/modules/{{MODULE}}';
    const cur = await (await fetch(u)).json();
    const f = document.getElementById('tmpdesc');
    const desc = f && f.files[0] ? await f.files[0].text() : (cur.Description && cur.Description.Html) || '';
    const body = {Title: {{TITLE_JSON}} || cur.Title, ShortTitle: cur.ShortTitle || '', Type: 0, ModuleStartDate: cur.ModuleStartDate, ModuleEndDate: cur.ModuleEndDate,
      ModuleDueDate: cur.ModuleDueDate, IsHidden: cur.IsHidden, IsLocked: cur.IsLocked, Description: {Content: desc, Type: 'Html'}, Duration: cur.Duration ?? null};
    return (await fetch(u, {method: 'PUT', headers: H, body: JSON.stringify(body)})).status;   // 200
  });
}

//### op: put_topic_html | kind: run_code | params: TOPIC, FILE, FILENAME | desc: reemplaza el HTML de una pagina existente desde un archivo local (conserva id y posicion). Efecto lateral: crea "<nombre> - Copy.html" y deja huerfano el anterior; leer antes con topic_html y subir pocas veces
async (page) => {
  await page.evaluate(() => { const i = document.createElement('input'); i.type = 'file'; i.id = 'tmpup'; document.body.appendChild(i); });
  await page.setInputFiles('#tmpup', '{{FILE}}');
  return await page.evaluate(async () => {
    const f = document.getElementById('tmpup').files[0];
    const fd = new FormData(); fd.append('file', f, '{{FILENAME}}');
    const r = await fetch('/d2l/api/le/{{LE}}/{{OU}}/content/topics/{{TOPIC}}/file',
      {method: 'PUT', headers: {'X-Csrf-Token': localStorage.getItem('XSRF.Token')}, body: fd});   // sin Content-Type: lo pone el navegador
    const t = await (await fetch('/d2l/api/le/{{LE}}/{{OU}}/content/topics/{{TOPIC}}')).json();
    return {status: r.status, url: t.Url, bytes: f.size};   // registrar la url vigente en state.yaml
  });
}

//### op: create_topic | kind: run_code | params: MODULE, TITLE, FILE, MIME, HIDDEN(true por defecto) | desc: crea un tema de archivo (HTML, PDF, DOCX, ZIP...) al final de un modulo. multipart/mixed armado a mano (FormData no sirve). Url obligatorio = {{ENFORCED}}/<archivo>
async (page) => {
  await page.evaluate(() => { const i = document.createElement('input'); i.type = 'file'; i.id = 'tmpup'; document.body.appendChild(i); });
  await page.setInputFiles('#tmpup', '{{FILE}}');
  return await page.evaluate(async () => {
    const f = document.getElementById('tmpup').files[0];
    const b = '----saman' + Date.now();
    const meta = {Title: {{TITLE_JSON}}, ShortTitle: '', Type: 1, TopicType: 1, Url: '{{ENFORCED}}/' + f.name,
      StartDate: null, EndDate: null, DueDate: null, IsHidden: {{HIDDEN}}, IsLocked: false, OpenAsExternalResource: false,
      Description: null, MajorUpdate: false, ActivityId: null};
    const e = new TextEncoder();
    const h1 = e.encode(`--${b}\r\nContent-Type: application/json\r\n\r\n${JSON.stringify(meta)}\r\n`);
    const h2 = e.encode(`--${b}\r\nContent-Disposition: form-data; name=""; filename="${f.name}"\r\nContent-Type: {{MIME}}\r\n\r\n`);
    const t = e.encode(`\r\n--${b}--\r\n`);
    const r = await fetch('/d2l/api/le/{{LE}}/{{OU}}/content/modules/{{MODULE}}/structure/', {method: 'POST',
      headers: {'X-Csrf-Token': localStorage.getItem('XSRF.Token'), 'Content-Type': `multipart/mixed; boundary=${b}`},
      body: new Blob([h1, h2, f, t])});
    const j = await r.json();
    return {status: r.status, id: j.Id, broken: j.IsBroken, url: j.Url, bytes: f.size};   // broken debe ser false
  });
}

//### op: rename_topic | kind: evaluate | params: TOPIC, TITLE | desc: renombra un tema reutilizando los valores del GET (no cambia su archivo)
async () => {
  const H = {'X-Csrf-Token': localStorage.getItem('XSRF.Token'), 'Content-Type': 'application/json'};
  const u = '/d2l/api/le/{{LE}}/{{OU}}/content/topics/{{TOPIC}}';
  const c = await (await fetch(u)).json();
  const body = {Title: {{TITLE_JSON}}, ShortTitle: c.ShortTitle || '', Type: 1, TopicType: c.TopicType, Url: c.Url, StartDate: c.StartDate, EndDate: c.EndDate,
    DueDate: c.DueDate, IsHidden: c.IsHidden, IsLocked: c.IsLocked, OpenAsExternalResource: c.OpenAsExternalResource,
    Description: {Content: (c.Description && c.Description.Html) || '', Type: 'Html'}, MajorUpdate: false, ActivityId: c.ActivityId};
  return (await fetch(u, {method: 'PUT', headers: H, body: JSON.stringify(body)})).status;   // 200
}

//### op: delete_topic | kind: evaluate | params: TOPIC | desc: ELIMINA un tema (sin deshacer). Requiere --confirm y respaldo previo con topic_html; nunca con temas cuyo titulo coincida con safety.protected_name_patterns. Un tema de asignacion no borra su dropbox: usar delete_dropbox
async () => (await fetch('/d2l/api/le/{{LE}}/{{OU}}/content/topics/{{TOPIC}}',
  {method: 'DELETE', headers: {'X-Csrf-Token': localStorage.getItem('XSRF.Token')}})).status   // 200

//### op: delete_module | kind: evaluate | params: MODULE | desc: ELIMINA un modulo con todo su contenido (sin deshacer). Requiere --confirm. Verificado el 2026-10-23 en un modulo de prueba. Los archivos de /content/enforced/ no se borran: quedan huerfanos
async () => (await fetch('/d2l/api/le/{{LE}}/{{OU}}/content/modules/{{MODULE}}',
  {method: 'DELETE', headers: {'X-Csrf-Token': localStorage.getItem('XSRF.Token')}})).status   // 200

//### op: module_structure | kind: evaluate | params: MODULE | desc: hijos directos de un modulo en orden (id, titulo, tipo, visibilidad, url, actividad). Util para verificar el orden tras subir
async () => (await (await fetch('/d2l/api/le/{{LE}}/{{OU}}/content/modules/{{MODULE}}/structure/')).json())
  .map(t => ({id: t.Id, title: t.Title, type: t.Type, topicType: t.TopicType, hidden: t.IsHidden, url: t.Url, activity: t.ActivityId}))

//### op: dropbox_info | kind: evaluate | params: DROPBOX | desc: carpeta de tarea: instrucciones, cierre, visibilidad, item de calificacion y rubricas
async () => { const f = await (await fetch('/d2l/api/le/{{LE}}/{{OU}}/dropbox/folders/{{DROPBOX}}')).json();
  return {id: f.Id, name: f.Name, hidden: f.IsHidden, due: f.DueDate, gradeItem: f.GradeItemId, rubrics: f.Assessment && f.Assessment.Rubrics, type: f.DropboxType, submissionType: f.SubmissionType, instructions: f.CustomInstructions && f.CustomInstructions.Html}; }

//### op: put_dropbox_instructions | kind: run_code | params: DROPBOX, FILE | desc: carga las instrucciones HTML de una tarea desde un archivo local conservando el resto de la carpeta (GET, quitar campos de solo lectura, PUT). Verificado el 2026-10-23
async (page) => {
  await page.evaluate(() => { const i = document.createElement('input'); i.type = 'file'; i.id = 'tmpins'; document.body.appendChild(i); });
  await page.setInputFiles('#tmpins', '{{FILE}}');
  return await page.evaluate(async () => {
    const H = {'X-Csrf-Token': localStorage.getItem('XSRF.Token'), 'Content-Type': 'application/json'};
    const u = '/d2l/api/le/{{LE}}/{{OU}}/dropbox/folders/{{DROPBOX}}';
    const cur = await (await fetch(u)).json();
    const body = {...cur};
    ['Id', 'CategoryId', 'Attachments', 'TotalFiles', 'UnreadFiles', 'FlaggedFiles', 'TotalUsers', 'TotalUsersWithSubmissions', 'TotalUsersWithFeedback', 'ActivityId', 'LinkAttachments'].forEach(k => delete body[k]);
    body.CustomInstructions = {Content: await document.getElementById('tmpins').files[0].text(), Type: 'Html'};
    const r = await fetch(u, {method: 'PUT', headers: H, body: JSON.stringify(body)});
    const after = await (await fetch(u)).json();
    return {status: r.status, name: after.Name, hidden: after.IsHidden, instructionsChars: (after.CustomInstructions.Html || '').length};
  });
}

//### op: delete_dropbox | kind: evaluate | params: DROPBOX | desc: ELIMINA una carpeta de tarea (sin deshacer; borra sus entregas). Requiere --confirm. Verificado el 2026-10-23. Borrar tambien el tema de asignacion con delete_topic
async () => (await fetch('/d2l/api/le/{{LE}}/{{OU}}/dropbox/folders/{{DROPBOX}}',
  {method: 'DELETE', headers: {'X-Csrf-Token': localStorage.getItem('XSRF.Token')}})).status   // 200

//### op: audit_topic | kind: run_code | params: TOPIC, FILE | desc: compara el HTML publicado de un tema con un archivo local (normaliza saltos de linea). Solo lectura
async (page) => {
  await page.evaluate(() => { const i = document.createElement('input'); i.type = 'file'; i.id = 'tmpaud'; document.body.appendChild(i); });
  await page.setInputFiles('#tmpaud', '{{FILE}}');
  return await page.evaluate(async () => {
    const norm = s => s.replace(/\r\n/g, '\n').replace(/\s+$/g, '');
    const loc = norm(await document.getElementById('tmpaud').files[0].text());
    const pub = norm(await (await fetch('/d2l/api/le/{{LE}}/{{OU}}/content/topics/{{TOPIC}}/file')).text());
    let i = 0; while (i < loc.length && i < pub.length && loc[i] === pub[i]) i++;
    return {equal: loc === pub, local: loc.length, published: pub.length, firstDiff: loc === pub ? null : i,
      localCtx: loc.slice(Math.max(0, i - 40), i + 80), publishedCtx: pub.slice(Math.max(0, i - 40), i + 80)};
  });
}

//### op: verify_images | kind: evaluate | params: - | desc: en una pagina publicada abierta (Url del tema), lista las imagenes que no cargaron
() => [...document.images].filter(i => !i.naturalWidth).map(i => i.src.slice(0, 120))

//### op: typography | kind: evaluate | params: - | desc: mide familia/tamano/peso de cada nodo de texto de la pagina abierta. Esperado (saman_html.py): Lato 32/700, 20/700, 18/700, 16/400 y 16/700; codigo en Consolas 14/15
() => { const out = {}; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n;
  while (n = w.nextNode()) { const t = n.nodeValue.trim(); if (!t || t === ' ') continue; const cs = getComputedStyle(n.parentElement);
    const k = cs.fontFamily.split(',')[0].replace(/"/g, '') + ' | ' + cs.fontSize + ' | w' + cs.fontWeight; out[k] = (out[k] || 0) + 1; } return out; }
