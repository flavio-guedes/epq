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
</style>
</head>
<body>
<div class="page-body">
  <h1>Painel de Conteúdo</h1>
  <pre id="debug" style="margin-top:12px; color:#334155;"></pre>
</div>
<script>
const RAW = {json_text};
document.getElementById('debug').textContent = 'Itens carregados: ' + RAW.length + '\\nPrimeiro: ' + RAW[0].ID;
</script>
</body>
</html>
'''

OUT_PATH.write_text(html, encoding='utf-8')
print('written', OUT_PATH, 'size', len(html))
