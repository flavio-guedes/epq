import re, json, sys

def array_end(s, start):
    depth = 0; i = start; quote = None; esc = False
    while i < len(s):
        c = s[i]
        if quote:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == quote: quote = None
        elif c in "\"'":
            quote = c
        elif c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1

SEED = r'''/* == Hermes | ciclo 1: semear os 7 em conversa na coluna "01 · Enviado" do kanban CRM == */
function seedCycle1SentLeads() {
  let added = 0;
  CONTACTS.forEach(c => {
    if ((c.status || '') !== 'Em conversa') return;
    if (c.email && !crmMap[c.email]) {
      crmMap[c.email] = { stage: '01 - Respondeu', portfolio: crmDefaultPortfolio(c) };
      added++;
    }
  });
  if (added) { try { saveCrm(); } catch (e) { } }
}
seedCycle1SentLeads();

'''

def parse(arr_txt):
    return json.loads(arr_txt)

def apply(arq):
    s = open(arq, encoding='utf-8').read()

    # 1) rótulo da coluna 01 (única ocorrência)
    old_label = '"01 - Respondeu":"💬 01 · Respondeu"'
    new_label = '"01 - Respondeu":"📤 01 · Enviado · Aguardando resposta"'
    assert s.count(old_label) == 1, (arq, 'label', s.count(old_label))
    s = s.replace(old_label, new_label)

    # 2) seed só se ainda não existir (idempotente)
    if 'function seedCycle1SentLeads()' not in s:
        anchor = 'renderCrmPanel();'
        assert s.count(anchor) >= 1, (arq, 'anchor')
        # insere antes da ÚLTIMA chamada (que inicializa o painel)
        s = s.rsplit(anchor, 1)
        s = s[0] + SEED + anchor + s[1]

    open(arq, 'w', encoding='utf-8').write(sqf)
    return len(s)

for arq in sys.argv[1:]:
    n = apply(arq)
    s = open(arq, encoding='utf-8').read()

    # valida CONTACTS
    m = re.search(r'const\s+CONTACTS\s*=\s*\[', s)
    e = array_end(s, m.end() - 1)
    arr = json.loads(s[m.end():e])
    emc = [c for c in arr if (c.get('status') or '') == 'Em conversa']
    ids = sorted(c['id'] for c in emc)

    print(arq, '| len', n, '| CONTACTS', len(arr), '| em conversa', len(emc), ids)
    print('  seed defs:', s.count('function seedCycle1SentLeads()'),
          '| chamada:', s.count('seedCycle1SentLeads();'),
          '| label📤:', s.count('"📤 01 · Enviado'),
          '| renderCrmPanel calls:', s.count('renderCrmPanel();'))
