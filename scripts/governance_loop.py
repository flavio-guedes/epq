#!/usr/bin/env python3
"""EPQ Governance Loop: reconcilia cronograma, painel de conteúdo, painel de tarefas e planilha.
Uso:
  python3 governance_loop.py            # executa reconciliação e atualiza acompanhamento
  python3 governance_loop.py --export   # exporta CSV para planilha
  python3 governance_loop.py --import   # importa mudanças aprovadas do CSV
"""
import json, re, os, sys, csv, shutil, tempfile
from pathlib import Path
from datetime import datetime
from difflib import unified_diff

EPQ_ROOT = Path('/Users/mac/repo-epq')
ACOMPANHAMENTO = Path('/Users/mac/repo-epq-projetos/master-acompanhamento.html')
STATE_FILE = EPQ_ROOT / '.epq-governance-state.json'
EXPORT_DIR = EPQ_ROOT / 'outputs'
EXPORT_DIR.mkdir(exist_ok=True)

FILES = {
    'cronograma': EPQ_ROOT / 'cronograma.html',
    'conteudo': EPQ_ROOT / 'painel-conteudo.html',
    'tarefas': EPQ_ROOT / 'painel-tarefas' / 'tarefas.html',
}

HEALTH_THRESHOLDS = {
    'max_gap_days': 3,
    'drastic_removal_ratio': 0.30,
    'drastic_pilar_change_count': 3,
    'drastic_date_change_count': 5,
    'drastic_format_change_ratio': 0.25,
}

FIELDNAMES = [
    'ID', 'Data da ação', 'Semana', 'Perfil', 'Tipo de distribuição', 'Formato',
    'Tema / Campanha', 'Pilar', 'Objetivo', 'Headline', 'Texto de apoio', 'Legenda',
    'CTA', 'Tags / Hashtags', 'Roteiro', 'Ideia de arte / Thumb', 'Link para arquivo',
    'Responsável', 'Status', 'OBS', 'Avaliação e Aprendizados', 'Campanha'
]


# ========================
# READERS
# ========================

def read_json(path: Path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def md5(text: str) -> str:
    import hashlib
    return hashlib.md5(text.encode('utf-8')).hexdigest()[:8]


def find_raw_block(path: Path, marker='const RAW =') -> str:
    text = path.read_text(encoding='utf-8', errors='ignore')
    start = text.find(marker)
    if start == -1:
        return ''
    start = text.find('[', start)
    if start == -1:
        return ''
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        ch = text[i]
        if esc:
            esc = False
            continue
        if ch == '\\':
            esc = True
            continue
        if ch == '"' and not esc:
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0:
                end = i + 1
                return text[start:end]
    return ''


def read_canonical_items():
    raw = find_raw_block(FILES['conteudo'])
    items = []
    if raw:
        try:
            data = json.loads(raw)
            for it in data:
                items.append({
                    'id': it.get('ID', ''),
                    'date': it.get('Data da ação', ''),
                    'profile': it.get('Perfil', ''),
                    'format': it.get('Formato', ''),
                    'headline': it.get('Headline', ''),
                    'tema': it.get('Tema / Campanha', ''),
                    'pilar': it.get('Pilar', ''),
                    'status': it.get('Status', ''),
                    'campaign': it.get('Campanha', ''),
                    'responsible': it.get('Responsável', ''),
                })
        except Exception:
            pass
    return items


def read_cronograma_items():
    text = FILES['cronograma'].read_text(encoding='utf-8', errors='ignore')
    items = []
    for line in text.splitlines():
        if 'sched-headline' in line or 'sched-tema' in line:
            m = re.search(r'>([^<]+)<', line)
            if m:
                items.append({'text': m.group(1).strip()})
    return items


def read_tarefas_items():
    text = FILES['tarefas'].read_text(encoding='utf-8', errors='ignore')
    items = []
    for line in text.splitlines():
        if 'card-title' in line:
            m = re.search(r'>([^<]+)<', line)
            if m:
                items.append({'text': m.group(1).strip()})
    return items


# ========================
# CHANGES / HEALTH
# ========================

def detect_drastic_changes(old_state, new_state):
    alerts = []
    if not old_state or not new_state:
        return alerts
    canonical_old = old_state.get('canonical_items', [])
    canonical_new = new_state.get('canonical_items', [])
    if len(canonical_old) > 10:
        ratio = abs(len(canonical_new) - len(canonical_old)) / len(canonical_old)
        if ratio >= HEALTH_THRESHOLDS['drastic_removal_ratio']:
            alerts.append(f'Mudança drástica no número de conteúdos: {len(canonical_old)} -> {len(canonical_new)} ({ratio:.0%})')
    pilar_changes = 0
    date_changes = 0
    format_changes = 0
    old_by_id = {it.get('id'): it for it in canonical_old if it.get('id')}
    for it in canonical_new:
        prev = old_by_id.get(it.get('id'))
        if prev:
            if prev.get('pilar') and prev.get('pilar') != it.get('pilar'):
                pilar_changes += 1
            if prev.get('date') and prev.get('date') != it.get('date'):
                date_changes += 1
            if prev.get('format') and prev.get('format') != it.get('format'):
                format_changes += 1
    if pilar_changes >= HEALTH_THRESHOLDS['drastic_pilar_change_count']:
        alerts.append(f'Mudança drástica de pilar em {pilar_changes} conteúdos')
    if date_changes >= HEALTH_THRESHOLDS['drastic_date_change_count']:
        alerts.append(f'Mudança drástica de data em {date_changes} conteúdos')
    if len(canonical_old) > 10 and (format_changes / len(canonical_old)) >= HEALTH_THRESHOLDS['drastic_format_change_ratio']:
        alerts.append(f'Mudança drástica de formato em {format_changes} conteúdos')
    return alerts


def compute_health_score(canonical_items, tarefas_items):
    total = len(canonical_items) + len(tarefas_items)
    if total == 0:
        return 0
    base = 100
    if len(tarefas_items) < len(canonical_items) * 0.7:
        base -= 15
    if len(canonical_items) < 5:
        base -= 20
    return max(0, min(100, base))


def generate_suggestions(canonical_items, tarefas_items, alerts):
    suggestions = []
    if len(tarefas_items) < len(canonical_items) * 0.7:
        suggestions.append('Mapear tarefas operacionais para cada conteúdo planejado.')
    if any('pilar' in a.lower() for a in alerts):
        suggestions.append('Revisar pilares alterados; atualizar playbook e tags.')
    if any('data' in a.lower() for a in alerts):
        suggestions.append('Atualizar datas no cronograma e comunicar alterações.')
    if not suggestions:
        suggestions.append('Manter sincronização semanal com a planilha.')
    return suggestions


def build_action_plan(alerts, suggestions):
    plan = []
    if alerts:
        plan.append({'action': 'Revisão emergencial', 'reason': '; '.join(alerts), 'owner': 'Master', 'deadline': '24h'})
    if suggestions:
        plan.append({'action': 'Auditoria de consistência', 'reason': '; '.join(suggestions[:2]), 'owner': 'Diretor Criativo', 'deadline': '48h'})
    plan.append({'action': 'Sincronização cruzada', 'reason': 'Confirmar alinhamento com planilha fonte única', 'owner': 'Automação', 'deadline': '7d'})
    return plan


# ========================
# SPREADSHEET EXPORT / IMPORT
# ========================


def export_csv(canonical_items, path: Path):
    raw = find_raw_block(FILES['conteudo'])
    if not raw:
        return False
    try:
        data = json.loads(raw)
    except Exception:
        return False
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)
    return True


def import_csv(path: Path):
    if not path.exists():
        return False
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        return False
    raw = json.dumps(rows, ensure_ascii=False, indent=4)
    text = FILES['conteudo'].read_text(encoding='utf-8')
    marker = 'const RAW ='
    start = text.find(marker)
    if start == -1:
        return False
    start = text.find('[', start)
    if start == -1:
        return False
    depth = 0
    in_str = False
    esc = False
    end = start
    for i in range(start, len(text)):
        ch = text[i]
        if esc:
            esc = False
            continue
        if ch == '\\':
            esc = True
            continue
        if ch == '"' and not esc:
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    new_text = text[:start] + raw + text[end:]
    tmp = Path(str(FILES['conteudo']) + '.tmp')
    tmp.write_text(new_text, encoding='utf-8')
    shutil.move(str(tmp), str(FILES['conteudo']))
    return True


# ========================
# TASK SYNC PROPOSAL
# ========================

def propose_tasks(canonical_items):
    proposed = []
    for it in canonical_items:
        proposed.append({
            'id': it.get('id'),
            'title': it.get('headline') or it.get('tema') or 'Conteúdo sem título',
            'status': 'Aberto',
            'priority': 'Alta',
            'tags': [it.get('pilar'), it.get('format'), it.get('campaign')],
            'source': 'governance-loop',
        })
    return proposed


# ========================
# ACOMPANHAMENTO UPDATE
# ========================

def update_acompanhamento(health_score, alerts, suggestions, action_plan):
    if not ACOMPANHAMENTO.exists():
        return False
    ts = datetime.now().strftime('%d/%m/%Y %H:%M')
    status_class = 'ok' if health_score >= 80 else 'warn' if health_score >= 60 else 'error'
    status_label = 'SAUDÁVEL' if health_score >= 80 else 'ATENÇÃO' if health_score >= 60 else 'CRÍTICO'
    alerts_html = '\n'.join(f'<li>{a}</li>' for a in alerts[:8]) or '<li>Nenhuma alteração drástica recente.</li>'
    suggestions_html = '\n'.join(f'<li>{s}</li>' for s in suggestions[:8]) or '<li>Sem sugestões no momento.</li>'
    plan_html = '\n'.join(
        f'<li><strong>{p["action"]}</strong> — {p["reason"]} (responsável: {p["owner"]}, prazo: {p["deadline"]})</li>'
        for p in action_plan[:8]
    )
    block = f'''
    <div class="status {status_class}">LOOP DE GOVERNANÇA — {status_label}</div>
    <h3>🔄 Loop de Governança EPQ</h3>
    <p><strong>Saúde da gestão:</strong> {health_score}% · <strong>Atualizado:</strong> {ts}</p>
    <div class="updates">
      <div class="evolution-title">Alertas de mudança drástica</div>
      <ul>{alerts_html}</ul>
    </div>
    <div class="next">
      <div class="next-title">Sugestões para manter a saúde</div>
      <ul>{suggestions_html}</ul>
    </div>
    <div class="evolution">
      <div class="evolution-title">Plano de ação</div>
      <ul>{plan_html}</ul>
    </div>
    '''
    html = ACOMPANHAMENTO.read_text(encoding='utf-8')
    marker = '<!-- EPQ-GOVERNANCE-LOOP -->'
    if marker in html:
        start = html.index(marker)
        end = html.find('</div>', start + len(marker)) + len('</div>')
        html = html[:start] + marker + block + html[end:]
    else:
        insert_before = '</body>'
        html = html.replace(insert_before, f'  <div class="container">\n{marker}{block}\n  </div>\n{insert_before}')
    ACOMPANHAMENTO.write_text(html, encoding='utf-8')
    return True


def read_cronograma_items():
    text = FILES['cronograma'].read_text(encoding='utf-8', errors='ignore')
    items = []
    for line in text.splitlines():
        if 'sched-headline' in line or 'sched-tema' in line:
            m = re.search(r'>([^<]+)<', line)
            if m:
                items.append({'text': m.group(1).strip()})
    return items


def read_tarefas_items():
    text = FILES['tarefas'].read_text(encoding='utf-8', errors='ignore')
    items = []
    for line in text.splitlines():
        if 'card-title' in line:
            m = re.search(r'>([^<]+)<', line)
            if m:
                items.append({'text': m.group(1).strip()})
    return items


# ========================
# CHANGES / HEALTH
# ========================

def detect_drastic_changes(old_state, new_state):
    alerts = []
    if not old_state or not new_state:
        return alerts
    canonical_old = old_state.get('canonical_items', [])
    canonical_new = new_state.get('canonical_items', [])
    if len(canonical_old) > 10:
        ratio = abs(len(canonical_new) - len(canonical_old)) / len(canonical_old)
        if ratio >= HEALTH_THRESHOLDS['drastic_removal_ratio']:
            alerts.append(f'Mudança drástica no número de conteúdos: {len(canonical_old)} -> {len(canonical_new)} ({ratio:.0%})')
    pilar_changes = 0
    date_changes = 0
    format_changes = 0
    old_by_id = {it.get('id'): it for it in canonical_old if it.get('id')}
    for it in canonical_new:
        prev = old_by_id.get(it.get('id'))
        if prev:
            if prev.get('pilar') and prev.get('pilar') != it.get('pilar'):
                pilar_changes += 1
            if prev.get('date') and prev.get('date') != it.get('date'):
                date_changes += 1
            if prev.get('format') and prev.get('format') != it.get('format'):
                format_changes += 1
    if pilar_changes >= HEALTH_THRESHOLDS['drastic_pilar_change_count']:
        alerts.append(f'Mudança drástica de pilar em {pilar_changes} conteúdos')
    if date_changes >= HEALTH_THRESHOLDS['drastic_date_change_count']:
        alerts.append(f'Mudança drástica de data em {date_changes} conteúdos')
    if len(canonical_old) > 10 and (format_changes / len(canonical_old)) >= HEALTH_THRESHOLDS['drastic_format_change_ratio']:
        alerts.append(f'Mudança drástica de formato em {format_changes} conteúdos')
    return alerts


def compute_health_score(canonical_items, tarefas_items):
    total = len(canonical_items) + len(tarefas_items)
    if total == 0:
        return 0
    base = 100
    if len(tarefas_items) < len(canonical_items) * 0.7:
        base -= 15
    if len(canonical_items) < 5:
        base -= 20
    return max(0, min(100, base))


def generate_suggestions(canonical_items, tarefas_items, alerts):
    suggestions = []
    if len(tarefas_items) < len(canonical_items) * 0.7:
        suggestions.append('Mapear tarefas operacionais para cada conteúdo planejado.')
    if any('pilar' in a.lower() for a in alerts):
        suggestions.append('Revisar pilares alterados; atualizar playbook e tags.')
    if any('data' in a.lower() for a in alerts):
        suggestions.append('Atualizar datas no cronograma e comunicar alterações.')
    if not suggestions:
        suggestions.append('Manter sincronização semanal com a planilha.')
    return suggestions


def build_action_plan(alerts, suggestions):
    plan = []
    if alerts:
        plan.append({'action': 'Revisão emergencial', 'reason': '; '.join(alerts), 'owner': 'Master', 'deadline': '24h'})
    if suggestions:
        plan.append({'action': 'Auditoria de consistência', 'reason': '; '.join(suggestions[:2]), 'owner': 'Diretor Criativo', 'deadline': '48h'})
    plan.append({'action': 'Sincronização cruzada', 'reason': 'Confirmar alinhamento com planilha fonte única', 'owner': 'Automação', 'deadline': '7d'})
    return plan


# ========================
# SPREADSHEET EXPORT / IMPORT
# ========================

FIELDNAMES = [
    'ID', 'Data da ação', 'Semana', 'Perfil', 'Tipo de distribuição', 'Formato',
    'Tema / Campanha', 'Pilar', 'Objetivo', 'Headline', 'Texto de apoio', 'Legenda',
    'CTA', 'Tags / Hashtags', 'Roteiro', 'Ideia de arte / Thumb', 'Link para arquivo',
    'Responsável', 'Status', 'OBS', 'Avaliação e Aprendizados', 'Campanha'
]


def export_csv(canonical_items, path: Path):
    raw = find_raw_block(FILES['conteudo'])
    if not raw:
        return False
    try:
        data = json.loads(raw)
    except Exception:
        return False
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)
    return True


def import_csv(path: Path):
    if not path.exists():
        return False
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        return False
    raw = json.dumps(rows, ensure_ascii=False, indent=4)
    text = FILES['conteudo'].read_text(encoding='utf-8')
    marker = 'const RAW ='
    start = text.find(marker)
    if start == -1:
        return False
    start = text.find('[', start)
    if start == -1:
        return False
    depth = 0
    in_str = False
    esc = False
    end = start
    for i in range(start, len(text)):
        ch = text[i]
        if esc:
            esc = False
            continue
        if ch == '\\':
            esc = True
            continue
        if ch == '"' and not esc:
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    new_text = text[:start] + raw + text[end:]
    tmp = Path(str(FILES['conteudo']) + '.tmp')
    tmp.write_text(new_text, encoding='utf-8')
    shutil.move(str(tmp), str(FILES['conteudo']))
    return True


# ========================
# ACOMPANHAMENTO UPDATE
# ========================

def update_acompanhamento(health_score, alerts, suggestions, action_plan):
    if not ACOMPANHAMENTO.exists():
        return False
    ts = datetime.now().strftime('%d/%m/%Y %H:%M')
    status_class = 'ok' if health_score >= 80 else 'warn' if health_score >= 60 else 'error'
    status_label = 'SAUDÁVEL' if health_score >= 80 else 'ATENÇÃO' if health_score >= 60 else 'CRÍTICO'
    alerts_html = '\n'.join(f'<li>{a}</li>' for a in alerts[:8]) or '<li>Nenhuma alteração drástica recente.</li>'
    suggestions_html = '\n'.join(f'<li>{s}</li>' for s in suggestions[:8]) or '<li>Sem sugestões no momento.</li>'
    plan_html = '\n'.join(
        f'<li><strong>{p["action"]}</strong> — {p["reason"]} (responsável: {p["owner"]}, prazo: {p["deadline"]})</li>'
        for p in action_plan[:8]
    )
    block = f'''
    <div class="status {status_class}">LOOP DE GOVERNANÇA — {status_label}</div>
    <h3>🔄 Loop de Governança EPQ</h3>
    <p><strong>Saúde da gestão:</strong> {health_score}% · <strong>Atualizado:</strong> {ts}</p>
    <div class="updates">
      <div class="evolution-title">Alertas de mudança drástica</div>
      <ul>{alerts_html}</ul>
    </div>
    <div class="next">
      <div class="next-title">Sugestões para manter a saúde</div>
      <ul>{suggestions_html}</ul>
    </div>
    <div class="evolution">
      <div class="evolution-title">Plano de ação</div>
      <ul>{plan_html}</ul>
    </div>
    '''
    html = ACOMPANHAMENTO.read_text(encoding='utf-8')
    marker = '<!-- EPQ-GOVERNANCE-LOOP -->'
    if marker in html:
        start = html.index(marker)
        end = html.find('</div>', start + len(marker)) + len('</div>')
        html = html[:start] + marker + block + html[end:]
    else:
        insert_before = '</body>'
        html = html.replace(insert_before, f'  <div class="container">\n{marker}{block}\n  </div>\n{insert_before}')
    ACOMPANHAMENTO.write_text(html, encoding='utf-8')
    return True


# ========================
# TASK SYNC PROPOSAL
# ========================

def propose_tasks(canonical_items):
    proposed = []
    for it in canonical_items:
        proposed.append({
            'id': it.get('id'),
            'title': it.get('headline') or it.get('tema') or 'Conteúdo sem título',
            'status': 'Aberto',
            'priority': 'Alta',
            'tags': [it.get('pilar'), it.get('format'), it.get('campaign')],
            'source': 'governance-loop',
        })
    return proposed


# ========================
# MAIN
# ========================

def main():
    old_state = {}
    if STATE_FILE.exists():
        try:
            old_state = read_json(STATE_FILE)
        except Exception:
            old_state = {}
    canonical_items = read_canonical_items()
    cronograma_items = read_cronograma_items()
    tarefas_items = read_tarefas_items()
    new_state = {
        'ts': datetime.now().isoformat(),
        'canonical_count': len(canonical_items),
        'canonical_ids': [it.get('id') for it in canonical_items if it.get('id')],
        'canonical_hashes': [md5(json.dumps(it, ensure_ascii=False)) for it in canonical_items],
        'tarefas_count': len(tarefas_items),
        'cronograma_count': len(cronograma_items),
    }
    alerts = detect_drastic_changes(old_state, new_state)
    health_score = compute_health_score(canonical_items, tarefas_items)
    suggestions = generate_suggestions(canonical_items, tarefas_items, alerts)
    action_plan = build_action_plan(alerts, suggestions)
    updated_ac = update_acompanhamento(health_score, alerts, suggestions, action_plan)
    csv_path = EXPORT_DIR / 'cronograma_export.csv'
    exported = export_csv(canonical_items, csv_path)
    task_proposal = propose_tasks(canonical_items)
    STATE_FILE.write_text(json.dumps(new_state, ensure_ascii=False, indent=2), encoding='utf-8')
    result = {
        'health_score': health_score,
        'alerts': alerts,
        'suggestions': suggestions,
        'action_plan': action_plan,
        'updated_acompanhamento': updated_ac,
        'exported_csv': str(csv_path),
        'csv_exported': exported,
        'task_proposal_count': len(task_proposal),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
