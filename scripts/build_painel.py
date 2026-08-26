#!/usr/bin/env python3
import json
from pathlib import Path
import datetime

ITEMS_PATH = Path('/Users/mac/HermesWorkspace/EPQ/plan-data-clean.json')
OUT_PATH = Path('/Users/mac/repo-epq/painel-conteudo.html')

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

# Gera HTML de detalhes para os 2 primeiros itens
detail_items = rows[:2]
detail_rows = '\n'.join([
    f'''
    <div class="sched-row sched-detail">
      <div class="detail-content">
        <div class="detail-section">
          <div class="detail-label">Contexto</div>
          <div class="detail-value">{it['Tema / Campanha']}</div>
        </div>
        <div class="detail-section">
          <div class="detail-label">Headline</div>
          <div class="detail-value headline">{it['Headline']}</div>
          <button class="copy-btn" onclick="copyText('{it['Headline']}')" title="Copiar headline">📋 Copiar</button>
        </div>
        <div class="detail-section">
          <div class="detail-label">Legenda</div>
          <div class="detail-value">{it['Legenda']}</div>
          <button class="copy-btn" onclick="copyText('{it['Legenda']}')" title="Copiar legenda">📋 Copiar</button>
        </div>
        <div class="detail-section">
          <div class="detail-label">Tags</div>
          <div class="detail-value tags">{it['Tags / Hashtags']}</div>
          <button class="copy-btn" onclick="copyText('{it['Tags / Hashtags']}')" title="Copiar tags">📋 Copiar</button>
        </div>
        <div class="detail-section">
          <div class="detail-label">Sugestão de Imagem</div>
          <div class="detail-value">{it['Ideia de arte / Thumb'] or '—'}</div>
        </div>
        <div class="detail-section">
          <div class="detail-label">Briefing Completo</div>
          <div class="detail-value briefing">
            <strong>Formato:</strong> {it['Formato']}<br>
            <strong>Perfil:</strong> {it['Perfil']}<br>
            <strong>Tipo:</strong> {it['Tipo de distribuição']}<br>
            <strong>Objetivo:</strong> {it['Objetivo']}<br>
            <strong>Responsável:</strong> {it['Responsável']}<br>
            <strong>Status:</strong> {it['Status'] or '—'}<br>
            <strong>OBS:</strong> {it['OBS'] or '—'}<br>
            <strong>Avaliação:</strong> {it['Avaliação e Aprendizados'] or '—'}
          </div>
        </div>
      </div>
    </div>
    '''
    for it in detail_items
])

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
body {{ font-family:var(--font-body); background:var(--epq-bg); color:var(--epq-gray-900); }}
.page-body {{ padding:24px; }}
.sched-table {{ background:var(--epq-white); border:1px solid var(--epq-gray-200); border-radius:var(--radius-lg); overflow:hidden; box-shadow:var(--shadow-md); }}
.sched-row {{ display:grid; grid-template-columns:78px 108px 80px 108px 1fr 140px 148px 64px; align-items:center; gap:14px; padding:14px 20px; border-bottom:1px solid var(--epq-gray-100); cursor:pointer; }}
.sched-row:last-child {{ border-bottom:none; }}
.sched-row.sched-head {{ background:var(--epq-gray-50); font-family:var(--font-mono); font-size:9px; font-weight:600; color:var(--epq-gray-500); letter-spacing:.1em; text-transform:uppercase; padding-top:12px; padding-bottom:12px; cursor:default; }}
.sched-row.is-past {{ opacity:.6; }}
.sched-row:not(.sched-head):hover {{ background:var(--epq-blue-50); }}
.sched-detail {{ display:block; cursor:default; background:var(--epq-gray-50); padding:0; }}
.sched-detail .detail-content {{ padding:18px 20px; }}
.detail-section {{ margin-bottom:14px; }}
.detail-section:last-child {{ margin-bottom:0; }}
.detail-label {{ font-family:var(--font-mono); font-size:9px; font-weight:600; color:var(--epq-gray-500); letter-spacing:.12em; text-transform:uppercase; margin-bottom:4px; }}
.detail-value {{ font-size:13px; color:var(--epq-gray-900); line-height:1.5; }}
.headline {{ font-family:var(--font-display); font-size:15px; font-weight:700; color:var(--epq-blue-900); }}
.tags {{ font-family:var(--font-mono); font-size:12px; color:var(--epq-blue-700); }}
.briefing {{ background:var(--epq-white); padding:12px; border-radius:var(--radius-sm); border:1px solid var(--epq-gray-200); }}
.copy-btn {{ display:inline-flex; align-items:center; gap:6px; margin-top:6px; padding:6px 12px; border-radius:var(--radius-sm); border:1px solid var(--epq-gray-200); background:var(--epq-white); font-family:var(--font-mono); font-size:10px; font-weight:600; color:var(--epq-gray-700); cursor:pointer; }}
.copy-btn:hover {{ border-color:var(--epq-blue-400); color:var(--epq-blue-700); }}
</style>
</head>
<body>
<div class="page-body">
  <h1>Painel de Conteúdo</h1>
  <div class="sched-table">
    <div class="sched-row sched-head">
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
<script>
const RAW = {json_text};
function esc(t){{const d=document.createElement('div');d.textContent=t;return d.innerHTML}}
function renderList(){{
  const box=document.getElementById('lista-rows');
  let html='';
  RAW.forEach((it,idx)=>{{
    const isDetail = idx < 2;
    html += '<div class=\"sched-row'+(it['_is_past']?' is-past':'')+'\" data-id=\"'+it['ID']+'\">';
    html += '<div class=\"sched-date\"><span class=\"sched-dd\">'+it['_date_dd']+'</span><span class=\"sched-dow\">'+it['_date_dow']+'</span></div>';
    html += '<div class=\"sched-id\">'+it['ID']+'</div>';
    html += '<div class=\"sched-perfil '+(it['Perfil']==='EPQ'?'perfil-epq':'perfil-ronan')+'">'+it['Perfil']+'</div>';
    html += '<div class=\"sched-formato\">'+it['Formato']+'</div>';
    html += '<div class=\"sched-main\"><div class=\"sched-headline\">'+it['Headline']+'</div><div class=\"sched-tema\">'+it['Tema / Campanha']+'</div></div>';
    html += '<div class=\"sched-pilar\">'+it['Pilar']+'</div>';
    html += '<div class=\"sched-status st-neutral\"><span class=\"status-dot\"></span>'+(it['Status']||'—')+'</div>';
    html += '<div><button class=\"btn btn-ghost\" data-action=\"open\" data-id=\"'+it['ID']+'\" style=\"font-family:var(--font-mono);font-size:10px;padding:6px 10px;\">Abrir</button></div>';
    html += '</div>';
    if(isDetail) html += '<div class=\"sched-row sched-detail\"><div class=\"detail-content">'+document.getElementById('detail-'+it['ID']).innerHTML+'</div></div>';
  }});
  box.innerHTML = html;
}}
function copyText(text){{
  navigator.clipboard.writeText(text).then(()=>alert('Copiado!'));
}}
function init(){{
  // Pre-render detail blocks for first 2 items
  const container = document.createElement('div');
  container.id = 'detail-container';
  container.style.display = 'none';
  RAW.slice(0,2).forEach(it=>{{
    const div = document.createElement('div');
    div.id = 'detail-'+it['ID'];
    div.innerHTML = `
      <div class=\"detail-section\">
        <div class=\"detail-label\">Contexto</div>
        <div class=\"detail-value\">${{esc(it['Tema / Campanha'])}}</div>
      </div>
      <div class=\"detail-section\">
        <div class=\"detail-label\">Headline</div>
        <div class=\"detail-value headline\">${{esc(it['Headline'])}}</div>
        <button class=\"copy-btn\" onclick=\"copyText('${{esc(it['Headline']).replace(/'/g, "\\'")}}')\">📋 Copiar</button>
      </div>
      <div class=\"detail-section\">
        <div class=\"detail-label\">Legenda</div>
        <div class=\"detail-value\">${{esc(it['Legenda']||'—')}}</div>
        <button class=\"copy-btn\" onclick=\"copyText('${{esc(it['Legenda']||'').replace(/'/g, "\\'")}}')\">📋 Copiar</button>
      </div>
      <div class=\"detail-section\">
        <div class=\"detail-label\">Tags</div>
        <div class=\"detail-value tags\">${{esc(it['Tags / Hashtags']||'—')}}</div>
        <button class=\"copy-btn\" onclick=\"copyText('${{esc(it['Tags / Hashtags']||'').replace(/'/g, "\\'")}}')\">📋 Copiar</button>
      </div>
      <div class=\"detail-section\">
        <div class=\"detail-label\">Sugestão de Imagem</div>
        <div class=\"detail-value\">${{esc(it['Ideia de arte / Thumb']||'—')}}</div>
      </div>
      <div class=\"detail-section\">
        <div class=\"detail-label\">Briefing Completo</div>
        <div class=\"detail-value briefing\">
          <strong>Formato:</strong> ${{esc(it['Formato'])}}<br>
          <strong>Perfil:</strong> ${{esc(it['Perfil'])}}<br>
          <strong>Tipo:</strong> ${{esc(it['Tipo de distribuição'])}}<br>
          <strong>Objetivo:</strong> ${{esc(it['Objetivo'])}}<br>
          <strong>Responsável:</strong> ${{esc(it['Responsável'])}}<br>
          <strong>Status:</strong> ${{esc(it['Status']||'—')}}<br>
          <strong>OBS:</strong> ${{esc(it['OBS']||'—')}}<br>
          <strong>Avaliação:</strong> ${{esc(it['Avaliação e Aprendizados']||'—')}}
        </div>
      </div>
    `;
    container.appendChild(div);
  }});
  document.body.appendChild(container);
  renderList();
}}
init();
</script>
</body>
</html>
'''

OUT_PATH.write_text(html, encoding='utf-8')
print('written', OUT_PATH, 'size', len(html))
