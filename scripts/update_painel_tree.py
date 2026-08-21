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
    return sorted(results, key=lambda x: (0 if x['mimeType'] == 'application/vnd.google-apps.folder' else 1, x['name']))

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

# Replace terminal section with tree section
old_terminal = '''      <div id="section-terminal" class="section">
        <div class="section-title">terminal</div>
        <div class="terminal">
          <div class="terminal-header"><div class="terminal-dot"></div><div class="terminal-title">epq estrutura</div></div>
          <div class="terminal-body" id="terminalBody">
            <div class="terminal-line"><span class="prefix">&gt;</span><span class="resp">Sistema operacional. Navegue pelo menu lateral.</span></div>
          </div>
          <div class="terminal-composer">
            <input class="terminal-input" id="terminalInput" placeholder="comando..." autocomplete="off">
            <button class="terminal-send" id="terminalSend" aria-label="enviar">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
            </button>
          </div>
        </div>
      </div>'''

new_tree_section = '''      <div id="section-drive" class="section">
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

html = html.replace(old_terminal, new_tree_section)

# Add tree styles
tree_css = '''
      .tree-controls{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:10px;}
      .tree-btn{padding:6px 12px;border-radius:var(--radius-sm);border:1px solid var(--border);background:var(--surface);color:var(--text-secondary);font-size:11.5px;cursor:pointer;backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);}
      .tree-btn:hover{border-color:var(--border-active);color:var(--text);}
      .tree-info{font-size:11.5px;color:var(--text-tertiary);margin-left:auto;}
      .tree-container{border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);padding:12px 10px;max-height:calc(100vh - 220px);overflow-y:auto;}
      .tree-group{display:flex;flex-direction:column;gap:2px;}
      .tree-node{display:flex;flex-direction:column;}
      .tree-row{display:flex;align-items:center;gap:8px;padding:5px 8px;border-radius:var(--radius-sm);cursor:default;transition:background 0.12s ease;}
      .tree-node.has-children>.tree-row{cursor:pointer;}
      .tree-node.has-children>.tree-row:hover{background:var(--surface-hover);}
      .tree-toggle{width:14px;height:14px;display:flex;align-items:center;justify-content:center;color:var(--text-secondary);font-size:9px;transition:transform 0.15s ease;flex-shrink:0;}
      .tree-toggle.open{transform:rotate(90deg);}
      .tree-toggle-placeholder{width:14px;flex-shrink:0;}
      .tree-icon{font-size:12px;line-height:1;}
      .tree-label{font-size:12.5px;color:var(--text-secondary);flex:1;line-height:1.3;letter-spacing:0.01em;}
      .tree-link{font-size:11px;color:var(--text-tertiary);text-decoration:none;padding:2px 8px;border-radius:999px;border:1px solid var(--border);background:var(--surface);opacity:0;transition:opacity 0.12s ease;white-space:nowrap;}
      .tree-row:hover .tree-link{opacity:1;}
      .tree-link:hover{border-color:var(--border-active);color:var(--text);}
'''

# Insert tree styles before </style>
html = html.replace('</style>', tree_css + '</style>')

# Add tree script before </body>
tree_js = '''
<script>
  document.addEventListener('click', function(e){
    const toggle = e.target.closest('.tree-toggle');
    if (!toggle) return;
    e.stopPropagation();
    const targetId = toggle.getAttribute('data-target');
    const target = document.getElementById(targetId);
    if (!target) return;
    const isHidden = target.style.display === 'none';
    target.style.display = isHidden ? 'block' : 'none';
    toggle.classList.toggle('open', isHidden);
  });

  document.getElementById('treeExpandAll').addEventListener('click', function(){
    document.querySelectorAll('.tree-children').forEach(el => el.style.display = 'block');
    document.querySelectorAll('.tree-toggle').forEach(el => el.classList.add('open'));
  });

  document.getElementById('treeCollapseAll').addEventListener('click', function(){
    document.querySelectorAll('.tree-children').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.tree-toggle').forEach(el => el.classList.remove('open'));
  });
</script>
'''

html = html.replace('</body>', tree_js + '</body>')

# Update sidebar to include tree section
old_nav = '''      <div class="nav-item" data-target="section-terminal">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg>
        <span>terminal</span>
      </div>'''

new_nav = '''      <div class="nav-item" data-target="section-drive">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 19a2 2 0 0 1-2 2H4 2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
        <span>drive</span>
      </div>'''

html = html.replace(old_nav, new_nav)

with open('/Users/mac/HermesWorkspace/epq-temp/painel-estrutura/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Painel atualizado com árvore do Drive.')
