#!/usr/bin/env python3
import json
from pathlib import Path
import datetime

ITEMS_PATH = Path('/Users/mac/HermesWorkspace/EPQ/plan-data-clean.json')
OUT_PATH = Path('/Users/mac/repo-epq/painel-conteudo.html')
BANNER_PATH = Path('/Users/mac/Library/CloudStorage/GoogleDrive-flavioguedesmkt@gmail.com/Meu Drive/_Profissional/_Freelancer/2026/Ativos/Estudando por Questoes/Marketing EPQ/01 - Criação e Marketing/00 - Apoio Geral/01 - Layouts Padrao/Capa padrão.png')

items = json.loads(ITEMS_PATH.read_text(encoding='utf-8'))

DIAS_SEMANA = ['seg','ter','qua','qui','sex','sáb','dom']

def parse_date(iso_or_br: str):
    s = (iso_or_br or '').strip()
    if not s:
        return '', '', None
    if '-' in s:
        y, m, d = s.split('-')
    else:
        d, m, y = s.split('/')
    dt = datetime.date(int(y), int(m), int(d))
    dd = f"{dt.day:02d}.{dt.month:02d}"
    dow = DIAS_SEMANA[dt.weekday()]
    return dd, dow, dt

rows = []
for it in items:
    data_raw = it.get('Data da ação') or ''
    dd_dow, dow, dt = parse_date(data_raw)
    it['_date_dd'] = dd_dow.split('.')[0] if '.' in dd_dow else dd_dow
    it['_date_dow'] = dd_dow.split('.')[1] if '.' in dd_dow else ''
    it['_month_name'] = ''
    it['_is_past'] = False
    it['_is_today'] = False
    rows.append(it)

json_text = json.dumps(rows, ensure_ascii=False, indent=2)

# Extract unique filter values
editorias = sorted(set(it['Pilar'] for it in rows if it.get('Pilar')))
campanhas = sorted(set(it.get('Formato','') for it in rows if it.get('Formato')))
status_values = sorted(set(it.get('Status','') for it in rows if it.get('Status')))

# Read banner and convert to base64
import base64
banner_b64 = ''
if BANNER_PATH.exists():
    banner_b64 = base64.b64encode(BANNER_PATH.read_bytes()).decode('utf-8')
else:
    print(f'Warning: banner not found at {BANNER_PATH}')

editoria_opts = '\n'.join([f'<option value="{e}">{e}</option>' for e in editorias])
campanha_opts = '\n'.join([f'<option value="{c}">{c}</option>' for c in campanhas])
status_opts = '\n'.join([f'<option value="{s}">{s}</option>' for s in status_values])

html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EPQ // Painel de Conteúdo</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
:root {{
  --epq-white:#ffffff; --epq-bg:#f4f7fa; --epq-gray-50:#f8fafc; --epq-gray-100:#eef2f5; --epq-gray-200:#e4eaf0;
  --epq-gray-300:#d8e0e7; --epq-gray-400:#adb9c5; --epq-gray-500:#8a97a5; --epq-gray-600:#687582;
  --epq-gray-700:#4a5660; --epq-gray-800:#2e3840; --epq-gray-900:#17212b;
  --epq-blue-50:#f0f7ff; --epq-blue-100:#eaf3ff; --epq-blue-200:#c5dcf5; --epq-blue-300:#9bc5ef;
  --epq-blue-400:#6aaae4; --epq-blue-500:#3d8bd9; --epq-blue-600:#2572be; --epq-blue-700:#175a96;
  --epq-blue-800:#0f3f6e; --epq-blue-900:#0b3155;
  --epq-positive:#2a8a5e; --epq-attention:#b07218; --epq-alert:#9b4a1a;
  --radius-sm:6px; --radius-md:10px; --radius-lg:16px; --radius-xl:24px;
  --shadow-md:0 4px 16px rgba(15,40,65,.08), 0 2px 6px rgba(15,40,65,.05);
  --font-display:'Space Grotesk',sans-serif; --font-body:'Inter',sans-serif; --font-mono:'JetBrains Mono',monospace;
}}
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ font-family:var(--font-body); background:var(--epq-bg); color:var(--epq-gray-900); min-height:100vh; overflow-x:hidden; -webkit-font-smoothing:antialiased; }}
:focus-visible {{ outline:2px solid var(--epq-blue-500); outline-offset:2px; }}

.sidebar {{ position:fixed; left:0; top:0; height:100vh; width:84px; background:var(--epq-gray-900); border-right:1px solid rgba(61,139,217,.15); z-index:100; display:flex; flex-direction:column; padding:24px 0; transition:width .5s cubic-bezier(0.16, 1, 0.3, 1); overflow:hidden; }}
.sidebar:hover {{ width:240px; }}
.sidebar-logo {{ width:36px; height:36px; margin:0 0 28px 23px; flex-shrink:0; background:var(--epq-blue-700); border-radius:8px; display:flex; align-items:center; justify-content:center; font-family:var(--font-display); font-weight:700; font-size:12px; color:#fff; }}
.sidebar-nav {{ display:flex; flex-direction:column; gap:3px; padding:0 12px; overflow-y:auto; }}
.nav-item {{ display:flex; align-items:center; gap:12px; padding:9px 11px; border-radius:var(--radius-sm); cursor:pointer; white-space:nowrap; text-decoration:none; color:var(--epq-gray-500); transition:background .2s, color .2s; }}
.nav-item:hover, .nav-item.active {{ background:rgba(61,139,217,.12); color:var(--epq-blue-300); }}
.nav-item.active {{ color:var(--epq-blue-400); }}
.nav-num {{ font-family:var(--font-mono); font-size:9px; flex-shrink:0; width:16px; }}
.nav-label {{ font-family:var(--font-mono); font-size:10px; font-weight:500; letter-spacing:.07em; text-transform:uppercase; opacity:0; transition:opacity .2s; }}
.sidebar:hover .nav-label {{ opacity:1; }}
.sidebar-status {{ margin-top:auto; padding:14px 12px 0; display:flex; align-items:center; gap:8px; }}
.status-dot-live {{ width:6px; height:6px; background:var(--epq-blue-400); border-radius:50%; animation:pulse-dot 2s ease-in-out infinite; flex-shrink:0; }}
@keyframes pulse-dot {{ 0%,100% {{ opacity:1; transform:scale(1); }} 50% {{ opacity:.5; transform:.8; }} }}

.main-content {{ margin-left:84px; min-height:100vh; }}
.command-header {{
  position:relative; min-height:420px; background:var(--epq-gray-900);
  background-image:linear-gradient(100deg, rgba(11,20,32,.92) 0%, rgba(11,20,32,.78) 38%, rgba(11,49,85,.45) 65%, rgba(11,49,85,.18) 100%), url('data:image/png;base64,{banner_b64}');
  background-size:cover; background-position:center; overflow:hidden; display:flex; align-items:flex-end; padding-bottom:44px;
}}
.grid-overlay {{ position:absolute; inset:0; pointer-events:none; opacity:.35; background-image:linear-gradient(rgba(61,139,217,.07) 1px, transparent 1px), linear-gradient(90deg, rgba(61,139,217,.07) 1px, transparent 1px); background-size:44px 44px; mask-image:radial-gradient(ellipse 70% 90% at 30% 40%, black 30%, transparent 75%); }}
.corner-brackets span {{ position:absolute; width:20px; height:20px; border:1px solid rgba(61,139,217,.35); }}
.cb-tl {{ top:20px; left:20px; border-right:none; border-bottom:none; }}
.cb-tr {{ top:20px; right:20px; border-left:none; border-bottom:none; }}
.header-content {{ position:relative; z-index:10; padding:0 56px; width:100%; max-width:900px; }}
.header-eyebrow {{ font-family:var(--font-mono); font-size:10px; font-weight:500; color:var(--epq-blue-300); letter-spacing:.2em; text-transform:uppercase; margin-bottom:16px; }}
.header-title {{ font-family:var(--font-display); font-size:clamp(30px, 4.6vw, 54px); font-weight:700; color:#fff; letter-spacing:-.03em; line-height:1.04; margin-bottom:14px; text-shadow:0 2px 24px rgba(0,0,0,.35); }}
.header-title em {{ color:var(--epq-blue-400); font-style:normal; }}
.header-subtitle {{ font-size:14px; font-weight:400; color:var(--epq-gray-300); line-height:1.6; max-width:560px; margin-bottom:28px; }}
.header-meta {{ display:flex; align-items:center; gap:24px; flex-wrap:wrap; }}
.status-badge {{ display:flex; align-items:center; gap:7px; font-family:var(--font-mono); font-size:10px; font-weight:500; color:var(--epq-blue-400); letter-spacing:.12em; text-transform:uppercase; }}
.status-badge-dot {{ width:6px; height:6px; background:var(--epq-blue-400); border-radius:50%; animation:pulse-dot 2s ease-in-out infinite; }}
.period-badge {{ font-family:var(--font-mono); font-size:10px; color:var(--epq-gray-400); letter-spacing:.08em; border-left:1px solid rgba(255,255,255,.12); padding-left:24px; }}

.page-body {{ padding:40px 56px 100px; max-width:1400px; }}
.filter-bar {{ display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin-bottom:24px; }}
.filter-chip {{ height:36px; padding:0 14px; border-radius:var(--radius-xl); border:1px solid var(--epq-gray-200); background:var(--epq-white); font-family:var(--font-mono); font-size:10px; font-weight:600; letter-spacing:.08em; text-transform:uppercase; color:var(--epq-gray-700); cursor:pointer; transition:all .2s; white-space:nowrap; }}
.filter-chip:hover {{ border-color:var(--epq-blue-400); color:var(--epq-blue-700); }}
.filter-input {{ height:36px; padding:0 14px; border-radius:var(--radius-xl); border:1px solid var(--epq-gray-200); background:var(--epq-white); font-family:var(--font-body); font-size:13px; color:var(--epq-gray-900); min-width:220px; }}
.filter-input:focus {{ border-color:var(--epq-blue-500); outline:none; box-shadow:0 0 0 3px rgba(61,139,217,.12); }}

.tabs {{ display:flex; gap:8px; margin-bottom:18px; }}
.tab {{ padding:10px 16px; border-radius:var(--radius-sm); font-family:var(--font-mono); font-size:10px; font-weight:600; letter-spacing:.12em; text-transform:uppercase; color:var(--epq-gray-600); cursor:pointer; border:1px solid transparent; background:transparent; }}
.tab.active {{ background:var(--epq-white); color:var(--epq-blue-700); border-color:var(--epq-gray-200); box-shadow:var(--shadow-md); }}

.kpi-strip {{ background:var(--epq-white); border:1px solid var(--epq-gray-200); border-radius:var(--radius-lg); display:flex; overflow-x:auto; margin-bottom:24px; box-shadow:var(--shadow-md); }}
.kpi-item {{ flex:1; min-width:130px; padding:22px 24px; border-right:1px solid var(--epq-gray-200); display:flex; flex-direction:column; gap:5px; }}
.kpi-item:last-child {{ border-right:none; }}
.kpi-label {{ font-family:var(--font-mono); font-size:9px; font-weight:500; color:var(--epq-gray-500); letter-spacing:.13em; text-transform:uppercase; }}
.kpi-value {{ font-family:var(--font-mono); font-size:26px; font-weight:500; color:var(--epq-gray-900); letter-spacing:-.03em; }}
.kpi-value.featured {{ color:var(--epq-blue-700); }}

.table-wrap {{ background:var(--epq-white); border:1px solid var(--epq-gray-200); border-radius:var(--radius-lg); overflow:hidden; box-shadow:var(--shadow-md); }}
.sched-row {{ display:grid; grid-template-columns: 40px 78px 108px 80px 108px 1fr 140px 148px 64px; align-items:center; gap:14px; padding:14px 20px; border-bottom:1px solid var(--epq-gray-100); }}
.sched-row:last-child {{ border-bottom:none; }}
.sched-row.sched-head {{ background:var(--epq-gray-50); font-family:var(--font-mono); font-size:9px; font-weight:600; color:var(--epq-gray-500); letter-spacing:.1em; text-transform:uppercase; padding-top:12px; padding-bottom:12px; cursor:default; }}
.sched-row.is-past {{ opacity:.6; }}
.sched-row:not(.sched-head):hover {{ background:var(--epq-blue-50); cursor:pointer; }}
.expand-btn {{ width:32px; height:32px; border-radius:var(--radius-sm); border:1px solid var(--epq-gray-200); background:var(--epq-white); cursor:pointer; font-family:var(--font-mono); font-size:12px; color:var(--epq-gray-700); display:flex; align-items:center; justify-content:center; transition:all .2s; }}
.expand-btn:hover {{ border-color:var(--epq-blue-400); color:var(--epq-blue-700); background:var(--epq-blue-50); }}
.expand-btn.expanded {{ background:var(--epq-blue-700); color:#fff; border-color:var(--epq-blue-700); }}
.sched-detail {{ display:none; background:var(--epq-gray-50); border-bottom:1px solid var(--epq-gray-200); }}
.sched-detail.open {{ display:block; }}
.detail-content {{ padding:18px 20px; }}
.detail-section {{ margin-bottom:14px; }}
.detail-section:last-child {{ margin-bottom:0; }}
.detail-label {{ font-family:var(--font-mono); font-size:9px; font-weight:600; color:var(--epq-gray-500); letter-spacing:.12em; text-transform:uppercase; margin-bottom:4px; }}
.detail-value {{ font-size:13px; color:var(--epq-gray-900); line-height:1.5; }}
.headline {{ font-family:var(--font-display); font-size:15px; font-weight:700; color:var(--epq-blue-900); }}
.tags {{ font-family:var(--font-mono); font-size:12px; color:var(--epq-blue-700); }}
.briefing {{ background:var(--epq-white); padding:12px; border-radius:var(--radius-sm); border:1px solid var(--epq-gray-200); }}
.copy-btn {{ display:inline-flex; align-items:center; gap:6px; margin-top:6px; padding:6px 12px; border-radius:var(--radius-sm); border:1px solid var(--epq-gray-200); background:var(--epq-white); font-family:var(--font-mono); font-size:10px; font-weight:600; color:var(--epq-gray-700); cursor:pointer; }}
.copy-btn:hover {{ border-color:var(--epq-blue-400); color:var(--epq-blue-700); }}

.page-footer {{ padding:32px 56px; border-top:1px solid var(--epq-gray-200); display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px; }}
.footer-brand, .footer-timestamp {{ font-family:var(--font-mono); font-size:9px; color:var(--epq-gray-400); letter-spacing:.12em; text-transform:uppercase; }}

@media (max-width:1100px) {{
  .sched-row {{ grid-template-columns: 40px 64px 90px 66px 1fr 110px 56px; }}
  .sched-formato, .sched-pilar {{ display:none; }}
}}
@media (max-width:900px) {{
  .page-body {{ padding:32px 24px 80px; }}
  .header-content {{ padding:0 24px; }}
}}
@media (max-width:640px) {{
  .sidebar {{ display:none; }}
  .main-content {{ margin-left:0; }}
  .header-title {{ font-size:28px; }}
  .sched-row {{ grid-template-columns: 40px 56px 1fr 96px; }}
  .sched-id, .today-flag {{ display:none; }}
}}
@media (prefers-reduced-motion:reduce) {{
  *, *::before, *::after {{ animation-duration:.01ms !important; animation-iteration-count:1 !important; transition-duration:.01ms !important; }}
}}
</style>
</head>
<body>

<nav class="sidebar">
  <div class="sidebar-logo">EQ</div>
  <div class="sidebar-nav">
    <a class="nav-item active" href="#"><span class="nav-num">01</span><span class="nav-label">Painel</span></a>
    <a class="nav-item" href="cronograma.html"><span class="nav-num">02</span><span class="nav-label">Cronograma</span></a>
  </div>
  <div class="sidebar-status"><div class="status-dot-live"></div><span class="nav-label" style="opacity:1;color:var(--epq-gray-500)">v1.0</span></div>
</nav>

<div class="main-content">

  <header class="command-header">
    <div class="grid-overlay"></div>
    <div class="corner-brackets"><span class="cb-tl"></span><span class="cb-tr"></span></div>
    <div class="header-content">
      <div class="header-eyebrow">EPQ // Content Ops</div>
      <h1 class="header-title">Painel de <em>Acompanhamento</em></h1>
      <p class="header-subtitle">Visão operacional do conteúdo de agosto a dezembro — EPQ e Ronan. Filtre por editoria, campanha e status.</p>
      <div class="header-meta">
        <div class="status-badge"><div class="status-badge-dot"></div>System Online</div>
        <div class="period-badge">01.08.2026 — 31.12.2026</div>
      </div>
    </div>
  </header>

  <div class="page-body">

    <div class="filter-bar">
      <input id="search" class="filter-input" placeholder="Buscar headline, tema, ID ou pilar..." />
      <select id="f-editoria" class="filter-chip"><option value="">Editoria</option>{editoria_opts}</select>
      <select id="f-campanha" class="filter-chip"><option value="">Campanha</option>{campanha_opts}</select>
      <select id="f-status" class="filter-chip"><option value="">Status</option>{status_opts}</select>
    </div>

    <div class="tabs">
      <button class="tab active" data-tab="lista">Lista</button>
    </div>

    <div class="kpi-strip" id="kpis"></div>

    <div id="tab-lista">
      <div class="table-wrap">
        <div class="sched-row sched-head">
          <div></div>
          <div class="sched-date">Data</div>
          <div class="sched-id">ID</div>
          <div class="sched-perfil">Perfil</div>
          <div class="sched-formato">Formato</div>
          <div class="sched-main">Headline / Tema</div>
          <div class="sched-pilar">Pilar</div>
          <div class="sched-status">Status</div>
          <div></div>
        </div>
        <div id="lista-rows"></div>
      </div>
    </div>

  </div>

  <footer class="page-footer">
    <div class="footer-brand">EPQ // Painel de Conteúdo</div>
    <div class="footer-timestamp">v1.0 · 25.08.2026</div>
  </footer>
</div>

<script>
const RAW = {json_text};
const DETAIL_IDS = new Set(RAW.slice(0,2).map(it=>it['ID']));
function esc(t){{
  if(t==null) return '';
  const d=document.createElement('div');
  d.textContent=String(t);
  return d.innerHTML;
}}
function copyText(text){{
  navigator.clipboard.writeText(text).then(()=>{{
    const btn=document.querySelector('.copy-btn.success');
    if(btn) btn.textContent='✅ Copiado';
  }});
}}
function renderList(){{
  const box=document.getElementById('lista-rows');
  const fEditoria=document.getElementById('f-editoria').value;
  const fCampanha=document.getElementById('f-campanha').value;
  const fStatus=document.getElementById('f-status').value;
  const q=document.getElementById('search').value.toLowerCase();
  let html='';
  let total=0, epq=0, ronan=0, integ=0, camp=0;
  RAW.forEach((it)=>{{
    const matchesEditoria=!fEditoria||it['Pilar']===fEditoria;
    const matchesCampanha=!fCampanha||it['Formato']===fCampanha;
    const matchesStatus=!fStatus||(it['Status']||'')===fStatus;
    const matchesSearch=!q||[it['ID'],it['Headline'],it['Tema / Campanha'],it['Pilar']].join(' ').toLowerCase().includes(q);
    if(!matchesEditoria||!matchesCampanha||!matchesStatus||!matchesSearch) return;
    total++; if(it['Perfil']==='EPQ') epq++; if(it['Perfil']==='Ronan') ronan++;
    if(it['Tipo de distribuição']==='Integrado') integ++; if(it['Formato']==='Campanha') camp++;
    const hasDetail=DETAIL_IDS.has(it['ID']);
    html += '<div class=\"sched-row'+(it['_is_past']?' is-past':'')+'\" data-id=\"'+it['ID']+'\">';
    html += '<div><button class=\"expand-btn'+(hasDetail?'':' disabled')+'\" data-action=\"expand\" data-id=\"'+it['ID']+'\" '+(hasDetail?'':'disabled')+'>▼</button></div>';
    html += '<div class=\"sched-date\"><span class=\"sched-dd\">'+it['_date_dd']+'</span><span class=\"sched-dow\">'+it['_date_dow']+'</span></div>';
    html += '<div class=\"sched-id\">'+it['ID']+'</div>';
    html += '<div class=\"sched-perfil '+(it['Perfil']==='EPQ'?'perfil-epq':'perfil-ronan')+'">'+it['Perfil']+'</div>';
    html += '<div class=\"sched-formato\">'+it['Formato']+'</div>';
    html += '<div class=\"sched-main\"><div class=\"sched-headline\">'+it['Headline']+'</div><div class=\"sched-tema\">'+it['Tema / Campanha']+'</div></div>';
    html += '<div class=\"sched-pilar\">'+it['Pilar']+'</div>';
    html += '<div class=\"sched-status st-neutral\"><span class=\"status-dot\"></span>'+(it['Status']||'—')+'</div>';
    html += '<div><button class=\"btn btn-ghost\" data-action=\"open\" data-id=\"'+it['ID']+'\" style=\"font-family:var(--font-mono);font-size:10px;padding:6px 10px;\">Abrir</button></div>';
    html += '</div>';
    if(hasDetail){{
      html += '<div class=\"sched-detail\" id=\"detail-'+it['ID']+'\">';
      html += '<div class=\"detail-content\">';
      html += '<div class=\"detail-section\"><div class=\"detail-label\">Contexto</div><div class=\"detail-value\">'+esc(it['Tema / Campanha'])+'</div></div>';
      html += '<div class=\"detail-section\"><div class=\"detail-label\">Headline</div><div class=\"detail-value headline\">'+esc(it['Headline'])+'</div><button class=\"copy-btn\" onclick=\"copyText(\\''+esc(it['Headline']).replace(/'/g, \"\\\\'\")+'\\')\">📋 Copiar</button></div>';
      html += '<div class=\"detail-section\"><div class=\"detail-label\">Legenda</div><div class=\"detail-value\">'+esc(it['Legenda']||'—')+'</div><button class=\"copy-btn\" onclick=\"copyText(\\''+esc(it['Legenda']||'').replace(/'/g, \"\\\\'\")+'\\')\">📋 Copiar</button></div>';
      html += '<div class=\"detail-section\"><div class=\"detail-label\">Tags</div><div class=\"detail-value tags\">'+esc(it['Tags / Hashtags']||'—')+'</div><button class=\"copy-btn\" onclick=\"copyText(\\''+esc(it['Tags / Hashtags']||'').replace(/'/g, \"\\\\'\")+'\\')\">📋 Copiar</button></div>';
      html += '<div class=\"detail-section\"><div class=\"detail-label\">Sugestão de Imagem</div><div class=\"detail-value\">'+esc(it['Ideia de arte / Thumb']||'—')+'</div></div>';
      html += '<div class=\"detail-section\"><div class=\"detail-label\">Briefing Completo</div><div class=\"detail-value briefing\"><strong>Formato:</strong> '+esc(it['Formato'])+'<br><strong>Perfil:</strong> '+esc(it['Perfil'])+'<br><strong>Tipo:</strong> '+esc(it['Tipo de distribuição'])+'<br><strong>Objetivo:</strong> '+esc(it['Objetivo'])+'<br><strong>Responsável:</strong> '+esc(it['Responsável'])+'<br><strong>Status:</strong> '+esc(it['Status']||'—')+'<br><strong>OBS:</strong> '+esc(it['OBS']||'—')+'<br><strong>Avaliação:</strong> '+esc(it['Avaliação e Aprendizados']||'—')+'</div></div>';
      html += '</div></div>';
    }}
  }});
  box.innerHTML = html;
  document.getElementById('kpis').innerHTML='<div class=\"kpi-item\"><div class=\"kpi-label\">Conteúdos</div><div class=\"kpi-value featured\">'+total+'</div></div><div class=\"kpi-item\"><div class=\"kpi-label\">EPQ</div><div class=\"kpi-value\">'+epq+'</div></div><div class=\"kpi-item\"><div class=\"kpi-label\">Ronan</div><div class=\"kpi-value\">'+ronan+'</div></div><div class=\"kpi-item\"><div class=\"kpi-label\">Integrados</div><div class=\"kpi-value\">'+integ+'</div></div><div class=\"kpi-item\"><div class=\"kpi-label\">Campanhas</div><div class=\"kpi-value\">'+camp+'</div></div>';
}}
function init(){{
  renderList();
  ['search','f-editoria','f-campanha','f-status'].forEach(id=>{{
    const el=document.getElementById(id);
    if(!el) return;
    el.addEventListener('input', renderList);
    el.addEventListener('change', renderList);
  }});
  document.getElementById('lista-rows').addEventListener('click',e=>{{
    const btn=e.target.closest('[data-action=\"expand\"]');
    if(!btn) return;
    const id=btn.dataset.id;
    const detail=document.getElementById('detail-'+id);
    if(!detail) return;
    const isOpen=detail.classList.contains('open');
    if(isOpen){{
      detail.classList.remove('open');
      btn.classList.remove('expanded');
      btn.textContent='▼';
    }} else {{
      detail.classList.add('open');
      btn.classList.add('expanded');
      btn.textContent='▲';
    }}
  }});
}}
init();
</script>
</body>
</html>
'''

OUT_PATH.write_text(html, encoding='utf-8')
print('written', OUT_PATH, 'size', len(html))
