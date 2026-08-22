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
        
        html_parts.append(f'<div class="tree-node" style="padding-left:{(depth * 18)}px">')
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

# 1. Change title and brand
html = html.replace('<title>EPQ · Painel de Estrutura</title>', '<title>Drive EPQ · Painel de Estrutura</title>')
html = html.replace('class="brand">epq painel</div>', 'class="brand">drive epq</div>')
html = html.replace('<div class="status-pill">estrutura</div>', '<div class="status-pill">drive</div>')
html = html.replace('<div class="status-pill" id="clock">--:--</div>', '<div class="status-pill" id="clock">--:--</div>')

# 2. Update sidebar title
html = html.replace('<div class="sidebar-title">navegação</div>', '<div class="sidebar-title">drive epq</div>')

# 3. Add new features section
old_drive = '''      <div id="section-drive" class="section">
        <div class="section-title">drive — estrutura em árvore</div>
        <div class="tree-controls">
          <button class="tree-btn" id="treeExpandAll">expandir tudo</button>
          <button class="tree-btn" id="treeCollapseAll">recolher tudo</button>
          <span class="tree-info">clique em ▶ para expandir · pastas clicáveis abrem no Drive</span>
        </div>
        <div class="tree-container">
          ''' + tree_html + '''
        </div>
      </div>'''

new_drive = '''      <div id="section-drive" class="section">
        <div class="section-title">drive — estrutura em árvore</div>
        <div class="tree-controls">
          <button class="tree-btn" id="treeExpandAll">expandir tudo</button>
          <button class="tree-btn" id="treeCollapseAll">recolher tudo</button>
          <button class="tree-btn" id="treeCopy">copiar estrutura</button>
          <span class="tree-info">clique em ▶ para expandir · pastas clicáveis abrem no Drive</span>
        </div>
        <div class="tree-container" id="treeContainer">
          ''' + tree_html + '''
        </div>
      </div>'''

html = html.replace(old_drive, new_drive)

# 4. Add quick actions section before meses
old_meses = '''      <div id="section-meses" class="section">'''

quick_actions = '''      <div id="section-atalhos" class="section">
        <div class="section-title">atalhos rápidos</div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;">
          <div class="quick-card" onclick="window.open('https://drive.google.com/drive/folders/1z6Y3JwfKfupA95KT_Il_X8xs5vqfMNeJ','_blank')">
            <div class="quick-icon">📂</div>
            <div class="quick-title">Abrir Drive EPQ</div>
            <div class="quick-desc">Pasta principal 01 - Criação</div>
          </div>
          <div class="quick-card" onclick="document.getElementById('section-jobs').scrollIntoView({behavior:'smooth'})">
            <div class="quick-icon">◈</div>
            <div class="quick-title">Ver Jobs</div>
            <div class="quick-desc">8 jobs padrão</div>
          </div>
          <div class="quick-card" onclick="document.getElementById('section-regras').scrollIntoView({behavior:'smooth'})">
            <div class="quick-icon">⚡</div>
            <div class="quick-title">Regras</div>
            <div class="quick-desc">Padrões e governança</div>
          </div>
          <div class="quick-card" onclick="document.getElementById('section-meses').scrollIntoView({behavior:'smooth'})">
            <div class="quick-icon">📅</div>
            <div class="quick-title">Meses</div>
            <div class="quick-desc">08 a 12/2026</div>
          </div>
        </div>
      </div>'''

html = html.replace(old_meses, quick_actions + old_meses)

# 5. Add CSS for copy button, quick cards, search highlight
extra_css = '''
      .tree-btn.copy{padding:6px 12px;border-radius:var(--radius-sm);border:1px solid var(--border);background:var(--surface);color:var(--text-secondary);font-size:11.5px;cursor:pointer;backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);}
      .tree-btn.copy:hover{border-color:var(--border-active);color:var(--text);}
      .tree-btn.copied{border-color:rgba(120,180,255,0.35);color:rgba(180,210,255,0.95);box-shadow:0 0 18px rgba(120,180,255,0.12);}
      
      .quick-card{border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);padding:14px 16px;display:flex;flex-direction:column;gap:6px;cursor:pointer;transition:all 0.15s ease;}
      .quick-card:hover{border-color:var(--border-active);background:var(--surface-hover);transform:translateY(-1px);}
      .quick-icon{font-size:20px;line-height:1;}
      .quick-title{font-size:13px;font-weight:500;letter-spacing:0.02em;color:var(--text);}
      .quick-desc{font-size:11.5px;color:var(--text-secondary);line-height:1.4;}
      
      .highlight{background:rgba(120,180,255,0.2);border-radius:2px;padding:1px 2px;}
      
      @media(max-width:640px){
        .filters-bar{flex-direction:column;align-items:stretch;}
        .filter-select,.filter-input{min-width:auto;width:100%;}
        .meses-grid{grid-template-columns:1fr;}
      }
'''

html = html.replace('</style>', extra_css + '</style>')

# 6. Update JS with copy functionality and better UX
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

  // Copy structure tree as text
  document.getElementById('treeCopy').addEventListener('click', function(){
    const treeText = document.getElementById('treeContainer').innerText;
    navigator.clipboard.writeText(treeText).then(() => {
      const btn = document.getElementById('treeCopy');
      btn.textContent = 'copiado!';
      btn.classList.add('copied');
      setTimeout(() => {
        btn.textContent = 'copiar estrutura';
        btn.classList.remove('copied');
      }, 2000);
    });
  });

  // Search in tree
  function searchTree(query){
    if (!query) {
      document.querySelectorAll('.tree-node').forEach(n => n.style.display = '');
      return;
    }
    const lower = query.toLowerCase();
    document.querySelectorAll('.tree-node').forEach(node => {
      const label = node.querySelector('.tree-label');
      if (label && label.textContent.toLowerCase().includes(lower)) {
        node.style.display = '';
        // Expand parents
        let parent = node.parentElement;
        while (parent) {
          if (parent.classList.contains('tree-children')) {
            parent.style.display = 'block';
            const toggle = document.querySelector(`[data-target="${parent.id}"]`);
            if (toggle) toggle.classList.add('open');
          }
          parent = parent.parentElement;
        }
      } else if (!node.querySelector('.tree-toggle')) {
        node.style.display = 'none';
      }
    });
  }
</script>
'''

html = html.replace('</body>', extra_js + '</body>')

# 7. Add search input in tree controls
html = html.replace(
    '<span class="tree-info">clique em ▶ para expandir · pastas clicáveis abrem no Drive</span>',
    '<input type="text" class="tree-search" id="treeSearch" placeholder="buscar na árvore..." oninput="searchTree(this.value)"><span class="tree-info">clique em ▶ para expandir · pastas clicáveis abrem no Drive</span>'
)

# 8. Add CSS for search input
search_css = '''
      .tree-search{padding:6px 10px;border-radius:var(--radius-sm);border:1px solid var(--border);background:rgba(255,255,255,0.03);color:var(--text);font-size:11.5px;font-family:inherit;outline:none;width:180px;}
      .tree-search:focus{border-color:var(--border-active);}
'''
html = html.replace('</style>', search_css + '</style>')

# Update sidebar navigation
html = html.replace(
    '<div class="sidebar-title">drive epq</div>',
    '<div class="sidebar-title">navegação</div>\n      <div class="sidebar-title" style="margin-top:8px;">atalhos</div>'
)

# Add navigation items
old_nav_end = '''      <div class="nav-item" data-target="section-drive">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 19a2 2 0 0 1-2 2H4 2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
        <span>drive</span>
      </div>'''

new_nav = '''      <div class="nav-item" data-target="section-atalhos">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
        <span>atalhos</span>
      </div>
      <div class="nav-item" data-target="section-drive">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 19a2 2 0 0 1-2 2H4 2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
        <span>drive</span>
      </div>'''

html = html.replace(old_nav_end, new_nav)

with open('/Users/mac/HermesWorkspace/epq-temp/painel-estrutura/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Painel Drive EPQ atualizado e evoluído.')
