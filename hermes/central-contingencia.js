// ══════════════════════════════════════════
// CONTINGÊNCIA: SATURAÇÃO + PANORAMA
// Injetado em central.html via DOMContentLoaded
// ══════════════════════════════════════════

const SATURATION = [
  { name:'Solar Pro 4 (Hermes)',    status:'working', cue:'livre',     pct:5,  note:'modelo atual do Hermes — sem sinal de limite' },
  { name:'OpenCode — big-pickle',   status:'blocked', cue:'limite',    pct:96, note:'free limit reached — Subscribe to OpenCode Go' },
  { name:'OpenCode — mimo-v2.5',    status:'blocked', cue:'limite',    pct:96, note:'free tier saturado — alternar não resolve se todos no limite' },
  { name:'OpenCode — outros free',  status:'blocked', cue:'limite',    pct:96, note:'mesmo comportamento esperado nos demais modelos gratuitos' },
  { name:'Ollama (local)',          status:'available', cue:'pronto',   pct:0,  note:'disponível localmente como fallback — sem custo externo' },
];

const PANORAMA = [
  { label:'Hermes',                status:'working', detail:'assumiu retomada há poucos instantes — orquestração ativa' },
  { label:'OpenCode / Codex',     status:'blocked',  detail:'4 processos presos — limite de modelo gratuito — não produtivos' },
  { label:'Agentes Hermes',        status:'working',  detail:'12 especialistas mapeados — vários disponíveis para redistribuição' },
  { label:'Mercúrio',              status:'waiting',  detail:'lote OUTREACH_BATCH_001 aguardando resposta — backend ativo porta 4321' },
  { label:'EPQ Leads 15/09',       status:'working',  detail:'42 leads classificados — relatório publicado — envio ao grupo pendente (canal não registrado)' },
  { label:'Auto-recovery Hermes',  status:'blocked',  detail:'briefing existente no workspace — não implementado antes da interrupção do OpenCode' },
  { label:'GitHub Pages',          status:'working',  detail:'deploy funcional — última publicação confirmada' },
  { label:'Desktop App Hermes',    status:'blocked',  detail:'build falhou por OOM na máquina — pendente de reconfiguração' },
];

// ── CSS ──
const BLOCO_CSS = `
.panorama-row { display:flex; align-items:center; gap:10px; padding:9px 0; border-bottom:1px solid var(--border-l); }
.panorama-row:last-child { border-bottom:none; }
.perc-val { font-family:var(--mono); font-size:15px; font-weight:700; min-width:42px; }
.mini-bar { width:100%; max-width:200px; height:5px; background:var(--bg); border-radius:3px; margin-top:4px; }
.mini-bar-track { width:100%; height:100%; border-radius:3px; overflow:hidden; }
.mini-bar-fill { height:100%; background:var(--accent); border-radius:3px; }
`;

let blocoCSSInjetado = false;
function injetarCSS() {
  if (blocoCSSInjetado) return;
  blocoCSSInjetado = true;
  const s = document.createElement('style');
  s.textContent = BLOCO_CSS;
  document.head.appendChild(s);
}

// ── view sidebar toggle (botão lateral) ──
function injetarBotaoSidebar() {
  const sidebar = document.querySelector('.app.sidebar .sidebar-section:last-of-type');
  if (!sidebar) return;
  const lastActionItem = sidebar.querySelector('.sidebar-item:last-of-type');
  if (!lastActionItem) return;
  const already = sidebar.querySelector('[onclick*="contingencia"]');
  if (already) return;
  const b = document.createElement('div');
  b.className = 'sidebar-item';
  b.setAttribute('onclick', "showView('contingencia')");
  b.title = 'Radar de saturação e panorama da operação';
  b.innerHTML = '<span class="si-icon">⚡</span><span class="si-text">Contingência</span>';
  lastActionItem.after(b);
}

// ── view — o card que fica no overview após health-ov ──
function montarViewContingencia() {
  const main = document.querySelector('main.main');
  if (!main) return;
  if (document.getElementById('view-contingencia')) return;
  const view = document.createElement('div');
  view.id = 'view-contingencia';
  view.className = 'view';
  view.innerHTML = `
    <div class="view-inner">
      <div class="page-header">
        <div class="page-title">Contingência</div>
        <div class="page-sub">Radar de saturação dos modelos + panorama da operação</div>
      </div>
      <div class="two-col">
        <div>
          <div style="font-size:13px;color:var(--ink-3);margin-bottom:14px">O quão cheio está cada recurso disponível. Marginal acima de 80% = risco iminente de interrupção.</div>
          <div id="saturacao-list"></div>
        </div>
        <div>
          <div style="font-size:13px;color:var(--ink-3);margin-bottom:14px">Onde cada peça está agora e o que define se pode ou não continuar.</div>
          <div id="panorama-list"></div>
        </div>
      </div>
    </div>`;
  const healthPanel = document.querySelector('#health-ov')?.closest('.panel');
  if (healthPanel) healthPanel.after(view);
  else {
    const ov = document.getElementById('view-overview');
    if (ov) {
      const firstCol = ov.querySelector('.two-col > div:first-child');
      if (firstCol && firstCol.contains(document.getElementById('health-ov'))) {
        const panels = firstCol.querySelectorAll('.panel');
        if (panels.length) panels[panels.length - 1].after(view);
        else firstCol.appendChild(view);
      }
    }
  }
}

// ── saturação ──
function renderSaturacao() {
  const el = document.getElementById('saturacao-list');
  if (!el) return;
  el.innerHTML = SATURATION.map(s => {
    const c = s.pct >= 80 ? 'c-red' : s.pct >= 50 ? 'c-amber' : s.pct >= 20 ? 'c-violet' : 'c-green';
    const chip = s.status === 'blocked' ? 'chip s-blocked' : s.status === 'waiting' ? 'chip s-waiting' : s.status === 'available' ? 'chip s-available' : 'chip s-working';
    return `
      <div class="panorama-row">
        <div style="flex:0 0 190px;font-weight:600;font-size:14px;color:var(--ink-1)">${s.name}</div>
        <div style="flex:1;display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
          <span class="perc-val ${c}">${s.pct}%</span>
          <span class="${chip}" style="font-size:11px">${s.cue}</span>
          <span style="font-size:12px;color:var(--ink-3);flex:1">${s.note}</span>
        </div>
        <div class="mini-bar"><div class="mini-bar-track"><div class="mini-bar-fill ${c}" style="width:${s.pct}%"></div></div></div>
      </div>`;
  }).join('');
}

// ── panorama ──
function renderPanorama() {
  const el = document.getElementById('panorama-list');
  if (!el) return;
  el.innerHTML = PANORAMA.map(p => {
    const chip = p.status === 'blocked' ? 'chip s-blocked' : p.status === 'waiting' ? 'chip s-waiting' : p.status === 'working' ? 'chip s-working' : 'chip s-review';
    return `
      <div class="panorama-row">
        <div style="flex:0 0 150px;font-weight:600;font-size:14px;color:var(--ink-1)">${p.label}</div>
        <div style="flex:1;display:flex;align-items:center;gap:8px;">
          <span class="${chip}" style="font-size:11px">${p.status}</span>
          <span style="font-size:12.5px;color:var(--ink-2)">${p.detail}</span>
        </div>
      </div>`;
  }).join('');
}

// ── inicialização ──
let bootRode = false;
function boot() {
  if (bootRode) return;
  bootRode = true;
  injetarCSS();
  montarViewContingencia();
  injetarBotaoSidebar();
  renderSaturacao();
  renderPanorama();
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
else boot();
