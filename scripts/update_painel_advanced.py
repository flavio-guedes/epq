import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

token_path = os.path.expanduser('~/.hermes/google_token.json')
creds = Credentials.from_authorized_user_file(token_path, [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.metadata'
])
service = build('drive', 'v3', credentials=creds)
root_id = '1z6Y3JwfKfupA95KT_Il_X8xs5vqfMNeJ'

def list_children(parent_id):
    results = []
    page_token = None
    while True:
        resp = service.files().list(
            q=f"'{parent_id}' in parents and trashed = false",
            fields="nextPageToken, files(id,name,mimeType)",
            pageToken=page_token,
            pageSize=1000
        ).execute()
        results.extend(resp.get('files', []))
        page_token = resp.get('nextPageToken')
        if not page_token:
            break
    return sorted(results, key=lambda x: x['name'])

def build_tree_html(parent_id, depth=0, max_depth=10):
    children = list_children(parent_id)
    if not children:
        return ''
    html_parts = []
    html_parts.append('<div class="tree-group">')
    for idx, child in enumerate(children):
        is_last = (idx == len(children) - 1)
        is_folder = child['mimeType'] == 'application/vnd.google-apps.folder'
        has_children = is_folder and depth < max_depth
        
        classes = ['tree-node']
        if has_children:
            classes.append('has-children')
        if is_last:
            classes.append('last')
            
        html_parts.append(f'<div class="{" ".join(classes)}" style="padding-left:{(depth * 18)}px">')
        html_parts.append('<div class="tree-row">')
        if has_children:
            html_parts.append(f'<span class="tree-toggle" data-target="tree-{child["id"]}">▶</span>')
        else:
            html_parts.append('<span class="tree-toggle-placeholder"></span>')
        html_parts.append(f'<span class="tree-icon">{"📁" if is_folder else "📄"}</span>')
        html_parts.append(f'<span class="tree-label">{child["name"]}</span>')
        if is_folder:
            html_parts.append(f'<a class="tree-link" href="https://drive.google.com/drive/folders/{child["id"]}" target="_blank" rel="noopener">abrir</a>')
        html_parts.append('</div>')
        
        if has_children:
            child_html = build_tree_html(child['id'], depth + 1, max_depth)
            html_parts.append(f'<div class="tree-children" id="tree-{child["id"]}" style="display:none;">')
            html_parts.append(child_html)
            html_parts.append('</div>')
        
        html_parts.append('</div>')
    html_parts.append('</div>')
    return '\n'.join(html_parts)

tree_html = build_tree_html(root_id)

# Read current HTML
with open('/Users/mac/HermesWorkspace/epq-temp/painel-estrutura/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Replace editorias section with expandable cards
old_editorias = '''      <div id="section-editorias" class="section">
        <div class="section-title">editorias</div>
        <p style="color:var(--text-secondary);font-size:12px;margin-bottom:10px;">Cada editoria contém os mesmos formatos. Dentro de cada formato, as categorias de job.</p>
        <div style="display:flex;flex-direction:column;gap:10px;">
          <div class="job"><div class="job-icon">◆</div><div class="job-info"><div class="job-name">Concursos</div><div class="job-meta">Feed · Stories · Carrossel · Reels · Ads · Banner · Impresso</div><div class="job-path"><span>social</span><span class="sep">·</span><span>ads</span><span class="sep">·</span><span>banner</span><span class="sep">·</span><span>impresso</span></div></div></div>
          <div class="job"><div class="job-icon">◆</div><div class="job-info"><div class="job-name">Dicas de Estudo</div><div class="job-meta">Feed · Stories · Carrossel · Reels · Ads · Banner · Impresso</div><div class="job-path"><span>social</span><span class="sep">·</span><span>ads</span><span class="sep">·</span><span>banner</span><span class="sep">·</span><span>impresso</span></div></div></div>
          <div class="job"><div class="job-icon">◆</div><div class="job-info"><div class="job-name">Institucional</div><div class="job-meta">Feed · Stories · Carrossel · Reels · Ads · Banner · Impresso</div><div class="job-path"><span>social</span><span class="sep">·</span><span>ads</span><span class="sep">·</span><span>banner</span><span class="sep">·</span><span>impresso</span></div></div></div>
        </div>
      </div>'''

# Get editoria data from Drive
editorias_data = []
for ed in list_children(root_id):
    if ed['name'] in ['Concursos', 'Dicas de Estudo', 'Institucional']:
        formatos = []
        for fmt in list_children(ed['id']):
            if fmt['mimeType'] == 'application/vnd.google-apps.folder':
                cats = [c['name'] for c in list_children(fmt['id']) if c['mimeType'] == 'application/vnd.google-apps.folder']
                formatos.append({'name': fmt['name'], 'categorias': cats})
        editorias_data.append({'name': ed['name'], 'formatos': formatos})

editoria_cards_html = ''
for ed in editorias_data:
    formatos_html = ''
    for fmt in ed['formatos']:
        cats_html = ', '.join(fmt['categorias'])
        formatos_html += f'<div style="font-size:11.5px;color:var(--text-secondary);margin-bottom:6px;"><strong style="color:var(--text);font-weight:500;">{fmt["name"]}</strong> — {cats_html}</div>'
    
    editoria_cards_html += f'''
    <div class="editoria-card" onclick="toggleEditoria(this)">
      <div class="editoria-header">
        <div class="job-icon">◆</div>
        <div class="job-info">
          <div class="job-name">{ed['name']}</div>
          <div class="job-meta">{len(ed['formatos'])} formatos · clique para expandir</div>
        </div>
        <span class="editoria-toggle">▶</span>
      </div>
      <div class="editoria-body" style="display:none;">
        {formatos_html}
      </div>
    </div>'''

new_editorias = f'''      <div id="section-editorias" class="section">
        <div class="section-title">editorias</div>
        <p style="color:var(--text-secondary);font-size:12px;margin-bottom:10px;">Cada editoria contém os mesmos formatos. Clique para expandir e ver as categorias.</p>
        <div style="display:flex;flex-direction:column;gap:10px;">
          {editoria_cards_html}
        </div>
      </div>'''

html = html.replace(old_editorias, new_editorias)

# 2. Replace jobs section with filters
old_jobs = '''      <div id="section-jobs" class="section">
        <div class="section-title">jobs padrão</div>
        <p style="color:var(--text-secondary);font-size:12px;margin-bottom:10px;">Cada job usa a mesma estrutura: <strong style="color:var(--text);">01 - Apoio › 01 - Referencia + 02 - Briefing · 03 - Arquivo Finalizado › OLD</strong></p>
        <div style="display:flex;flex-direction:column;gap:10px;">
          <div class="job"><div class="job-icon">◈</div><div class="job-info"><div class="job-name">EPQ_social_stories_1080x1920</div><div class="job-meta">Concursos › Stories › social</div><div class="job-path"><span>01 - Apoio</span><span class="sep">›</span><span>01 - Referencia</span><span class="sep">+</span><span>02 - Briefing</span><span class="sep">›</span><span>03 - Arquivo Finalizado</span><span class="sep">›</span><span>OLD</span></div></div></div>
          <div class="job"><div class="job-icon">◈</div><div class="job-info"><div class="job-name">EPQ_social_feed_1080x1080</div><div class="job-meta">Concursos › Feed › social</div><div class="job-path"><span>01 - Apoio</span><span class="sep">›</span><span>01 - Referencia</span><span class="sep">+</span><span>02 - Briefing</span><span class="sep">›</span><span>03 - Arquivo Finalizado</span><span class="sep">›</span><span>OLD</span></div></div></div>
          <div class="job"><div class="job-icon">◈</div><div class="job-info"><div class="job-name">EPQ_social_carrossel_1080x1080</div><div class="job-meta">Concursos › Carrossel › social</div><div class="job-path"><span>01 - Apoio</span><span class="sep">›</span><span>01 - Referencia</span><span class="sep">+</span><span>02 - Briefing</span><span class="sep">›</span><span>03 - Arquivo Finalizado</span><span class="sep">›</span><span>OLD</span></div></div></div>
          <div class="job"><div class="job-icon">◈</div><div class="job-info"><div class="job-name">EPQ_social_reels_1080x1920</div><div class="job-meta">Concursos › Reels › social</div><div class="job-path"><span>01 - Apoio</span><span class="sep">›</span><span>01 - Referencia</span><span class="sep">+</span><span>02 - Briefing</span><span class="sep">›</span><span>03 - Arquivo Finalizado</span><span class="sep">›</span><span>OLD</span></div></div></div>
          <div class="job"><div class="job-icon">◈</div><div class="job-info"><div class="job-name">EPQ_ads_feed_1080x1080</div><div class="job-meta">Concursos › Feed › ads</div><div class="job-path"><span>01 - Apoio</span><span class="sep">›</span><span>01 - Referencia</span><span class="sep">+</span><span>02 - Briefing</span><span class="sep">›</span><span>03 - Arquivo Finalizado</span><span class="sep">›</span><span>OLD</span></div></div></div>
          <div class="job"><div class="job-icon">◈</div><div class="job-info"><div class="job-name">EPQ_ads_stories_1080x1920</div><div class="job-meta">Concursos › Stories › ads</div><div class="job-path"><span>01 - Apoio</span><span class="sep">›</span><span>01 - Referencia</span><span class="sep">+</span><span>02 - Briefing</span><span class="sep">›</span><span>03 - Arquivo Finalizado</span><span class="sep">›</span><span>OLD</span></div></div></div>
          <div class="job"><div class="job-icon">◈</div><div class="job-info"><div class="job-name">EPQ_banner_1920x500</div><div class="job-meta">Concursos › Banner › banner</div><div class="job-path"><span>01 - Apoio</span><span class="sep">›</span><span>01 - Referencia</span><span class="sep">+</span><span>02 - Briefing</span><span class="sep">›</span><span>03 - Arquivo Finalizado</span><span class="sep">›</span><span>OLD</span></div></div></div>
          <div class="job"><div class="job-icon">◈</div><div class="job-info"><div class="job-name">EPQ_impresso_a4_210x297mm</div><div class="job-meta">Concursos › Impresso › impresso</div><div class="job-path"><span>01 - Apoio</span><span class="sep">›</span><span>01 - Referencia</span><span class="sep">+</span><span>02 - Briefing</span><span class="sep">›</span><span>03 - Arquivo Finalizado</span><span class="sep">›</span><span>OLD</span></div></div></div>
        </div>
      </div>'''

jobs_data = [
    {'name': 'EPQ_social_stories_1080x1920', 'editoria': 'Concursos', 'formato': 'Stories', 'categoria': 'social'},
    {'name': 'EPQ_social_feed_1080x1080', 'editoria': 'Concursos', 'formato': 'Feed', 'categoria': 'social'},
    {'name': 'EPQ_social_carrossel_1080x1080', 'editoria': 'Concursos', 'formato': 'Carrossel', 'categoria': 'social'},
    {'name': 'EPQ_social_reels_1080x1920', 'editoria': 'Concursos', 'formato': 'Reels', 'categoria': 'social'},
    {'name': 'EPQ_ads_feed_1080x1080', 'editoria': 'Concursos', 'formato': 'Feed', 'categoria': 'ads'},
    {'name': 'EPQ_ads_stories_1080x1920', 'editoria': 'Concursos', 'formato': 'Stories', 'categoria': 'ads'},
    {'name': 'EPQ_banner_1920x500', 'editoria': 'Concursos', 'formato': 'Banner', 'categoria': 'banner'},
    {'name': 'EPQ_impresso_a4_210x297mm', 'editoria': 'Concursos', 'formato': 'Impresso', 'categoria': 'impresso'},
]

editorias_options = sorted(set(j['editoria'] for j in jobs_data))
formatos_options = sorted(set(j['formato'] for j in jobs_data))
categorias_options = sorted(set(j['categoria'] for j in jobs_data))

jobs_filter_html = '''
      <div id="section-jobs" class="section">
        <div class="section-title">jobs padrão</div>
        <p style="color:var(--text-secondary);font-size:12px;margin-bottom:10px;">Cada job usa a mesma estrutura: <strong style="color:var(--text);">01 - Apoio › 01 - Referencia + 02 - Briefing · 03 - Arquivo Finalizado › OLD</strong></p>
        
        <div class="filters-bar">
          <div class="filter-group">
            <label class="filter-label">editoria</label>
            <select class="filter-select" id="filterEditoria" onchange="applyFilters()">
              <option value="">todas</option>
''' + '\n'.join([f'              <option value="{ed}">{ed}</option>' for ed in editorias_options]) + '''
            </select>
          </div>
          
          <div class="filter-group">
            <label class="filter-label">formato</label>
            <select class="filter-select" id="filterFormato" onchange="applyFilters()">
              <option value="">todos</option>
''' + '\n'.join([f'              <option value="{fmt}">{fmt}</option>' for fmt in formatos_options]) + '''
            </select>
          </div>
          
          <div class="filter-group">
            <label class="filter-label">categoria</label>
            <select class="filter-select" id="filterCategoria" onchange="applyFilters()">
              <option value="">todas</option>
''' + '\n'.join([f'              <option value="{cat}">{cat}</option>' for cat in categorias_options]) + '''
            </select>
          </div>
          
          <div class="filter-group">
            <label class="filter-label">busca</label>
            <input type="text" class="filter-input" id="filterBusca" placeholder="nome do job..." oninput="applyFilters()">
          </div>
          
          <button class="filter-clear" onclick="clearFilters()">limpar</button>
        </div>
        
        <div id="jobsList" style="display:flex;flex-direction:column;gap:10px;margin-top:12px;">
'''

for j in jobs_data:
    jobs_filter_html += f'''          <div class="job" data-editoria="{j['editoria']}" data-formato="{j['formato']}" data-categoria="{j['categoria']}" data-name="{j['name']}">
            <div class="job-icon">◈</div>
            <div class="job-info">
              <div class="job-name">{j['name']}</div>
              <div class="job-meta">{j['editoria']} › {j['formato']} › {j['categoria']}</div>
              <div class="job-path">
                <span>01 - Apoio</span><span class="sep">›</span>
                <span>01 - Referencia</span><span class="sep">+</span>
                <span>02 - Briefing</span><span class="sep">›</span>
                <span>03 - Arquivo Finalizado</span><span class="sep">›</span>
                <span>OLD</span>
              </div>
            </div>
          </div>
'''

jobs_filter_html += '''        </div>
        <div id="jobsEmpty" style="display:none;color:var(--text-tertiary);font-size:12px;margin-top:10px;">nenhum job encontrado</div>
      </div>'''

html = html.replace(old_jobs, jobs_filter_html)

# 3. Add meses section before regras
old_regras = '''      <div id="section-regras" class="section">'''

meses_html = '''      <div id="section-meses" class="section">
        <div class="section-title">calendário de meses</div>
        <p style="color:var(--text-secondary);font-size:12px;margin-bottom:10px;">Cada job contém pastas mensais em <strong style="color:var(--text);">03 - Arquivo Finalizado</strong>. Use para organizar por data de publicação.</p>
        <div class="meses-grid">
          <div class="mes-card">
            <div class="mes-header">08 - Agosto</div>
            <div class="mes-body">8 jobs · arquivos de agosto/2026</div>
          </div>
          <div class="mes-card">
            <div class="mes-header">09 - Setembro</div>
            <div class="mes-body">8 jobs · arquivos de setembro/2026</div>
          </div>
          <div class="mes-card">
            <div class="mes-header">10 - Outubro</div>
            <div class="mes-body">8 jobs · arquivos de outubro/2026</div>
          </div>
          <div class="mes-card">
            <div class="mes-header">11 - Novembro</div>
            <div class="mes-body">8 jobs · arquivos de novembro/2026</div>
          </div>
          <div class="mes-card">
            <div class="mes-header">12 - Dezembro</div>
            <div class="mes-body">8 jobs · arquivos de dezembro/2026</div>
          </div>
        </div>
      </div>'''

html = html.replace(old_regras, meses_html + old_regras)

# 4. Add CSS for filters, editoria cards, meses grid
extra_css = '''
      .editoria-card{border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);padding:14px 16px;cursor:pointer;transition:all 0.15s ease;}
      .editoria-card:hover{border-color:var(--border-active);background:var(--surface-hover);}
      .editoria-header{display:flex;align-items:center;gap:14px;}
      .editoria-toggle{color:var(--text-secondary);font-size:11px;transition:transform 0.15s ease;margin-left:auto;}
      .editoria-card.open .editoria-toggle{transform:rotate(90deg);}
      .editoria-body{margin-top:10px;padding-top:10px;border-top:1px solid var(--border);}

      .filters-bar{display:flex;align-items:flex-end;gap:10px;flex-wrap:wrap;padding:12px 14px;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);}
      .filter-group{display:flex;flex-direction:column;gap:4px;}
      .filter-label{font-size:10px;text-transform:uppercase;letter-spacing:0.12em;color:var(--text-tertiary);font-weight:500;}
      .filter-select,.filter-input{padding:8px 10px;border-radius:var(--radius-sm);border:1px solid var(--border);background:rgba(255,255,255,0.03);color:var(--text);font-size:12px;font-family:inherit;outline:none;min-width:140px;}
      .filter-select:focus,.filter-input:focus{border-color:var(--border-active);}
      .filter-clear{padding:8px 12px;border-radius:var(--radius-sm);border:1px solid var(--border);background:var(--surface);color:var(--text-secondary);font-size:11.5px;cursor:pointer;height:fit-content;backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);}
      .filter-clear:hover{border-color:var(--border-active);color:var(--text);}

      .meses-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;}
      .mes-card{border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);padding:14px 16px;display:flex;flex-direction:column;gap:6px;transition:all 0.15s ease;}
      .mes-card:hover{border-color:var(--border-active);background:var(--surface-hover);}
      .mes-header{font-size:13px;font-weight:500;letter-spacing:0.02em;color:var(--text);}
      .mes-body{font-size:12px;color:var(--text-secondary);line-height:1.4;}
'''

html = html.replace('</style>', extra_css + '</style>')

# 5. Add JS for editoria toggle, filters
extra_js = '''
<script>
  function toggleEditoria(card){
    const body = card.querySelector('.editoria-body');
    const isHidden = body.style.display === 'none';
    body.style.display = isHidden ? 'block' : 'none';
    card.classList.toggle('open', isHidden);
  }

  function applyFilters(){
    const editoria = document.getElementById('filterEditoria').value;
    const formato = document.getElementById('filterFormato').value;
    const categoria = document.getElementById('filterCategoria').value;
    const busca = document.getElementById('filterBusca').value.toLowerCase();
    const jobs = document.querySelectorAll('#jobsList .job');
    let visible = 0;
    jobs.forEach(job => {
      const matchEd = !editoria || job.dataset.editoria === editoria;
      const matchFmt = !formato || job.dataset.formato === formato;
      const matchCat = !categoria || job.dataset.categoria === categoria;
      const matchBusca = !busca || job.dataset.name.toLowerCase().includes(busca);
      const show = matchEd && matchFmt && matchCat && matchBusca;
      job.style.display = show ? 'flex' : 'none';
      if (show) visible++;
    });
    document.getElementById('jobsEmpty').style.display = visible === 0 ? 'block' : 'none';
  }

  function clearFilters(){
    document.getElementById('filterEditoria').value = '';
    document.getElementById('filterFormato').value = '';
    document.getElementById('filterCategoria').value = '';
    document.getElementById('filterBusca').value = '';
    applyFilters();
  }
</script>
'''

html = html.replace('</body>', extra_js + '</body>')

# Update sidebar
old_nav = '''      <div class="nav-item" data-target="section-drive">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 19a2 2 0 0 1-2 2H4 2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
        <span>drive</span>
      </div>'''

new_nav = '''      <div class="nav-item" data-target="section-meses">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>
        <span>meses</span>
      </div>
      <div class="nav-item" data-target="section-drive">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 19a2 2 0 0 1-2 2H4 2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
        <span>drive</span>
      </div>'''

html = html.replace(old_nav, new_nav)

with open('/Users/mac/HermesWorkspace/epq-temp/painel-estrutura/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Painel atualizado com filtros, meses e editorias expansíveis.')
