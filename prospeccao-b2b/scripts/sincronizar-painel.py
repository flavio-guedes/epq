#!/usr/bin/env python3
"""
Sincroniza o painel centralizado.

Lê os JSONs originais e gera:
  - fila-centralizada.json (view consolidada para o painel)
  - estado/painel-ultimo.json (snapshot de auditoria)

NÃO modifica os arquivos originais.
"""
import json
import os
import re
import sys
from datetime import datetime

BASE = '/Users/mac/HermesWorkspace/prospeccao-b2b'
PAINEL_HTML = f'{BASE}/painel-centralizado.html'
FILA_CONSOLIDADA = f'{BASE}/fila-centralizada.json'
LEADS_B2B = f'{BASE}/leads/leads_mei_lier_I.json'
FULL_EPQ = f'{BASE}/leads_epq_2026-09-15.json'


def load_json(path):
    if not os.path.exists(path):
        print(f"⚠ Arquivo não encontrado: {path}")
        return None
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def salvar_json(path, data):
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def montar_b2b(leads_raw):
    """Converte leads_mei_lier_I.json em estrutura operacional B2B."""
    grupos = {
        '1-respondeu-oportunidade': {'titulo': '1. Respondeu / Oportunidade', 'count': 0, 'leads': []},
        '2-quente': {'titulo': '2. Quente', 'count': 0, 'leads': []},
        '3-morno': {'titulo': '3. Morno', 'count': 0, 'leads': []},
        '4-frio': {'titulo': '4. Frio', 'count': 0, 'leads': []},
        '5-sem-contexto-validar': {'titulo': '5. Sem contexto / Precisa validar', 'count': 0, 'leads': []},
    }

    for l in leads_raw:
        temp = str(l.get('temperatura', '')).upper()
        # Mapeamento para grupos
        if temp == 'QUENTE':
            gkey = '2-quente'
        elif temp == 'MORNO':
            gkey = '3-morno'
        elif temp == 'FRIO':
            gkey = '4-frio'
        else:
            gkey = '5-sem-contexto-validar'

        lead = {
            'id': str(l.get('id', '')),
            'nome': l.get('empresa', l.get('nome', 'Sem nome')),
            'whatsapp': l.get('whatsapp', l.get('whatsapp_raw', 'n/a')),
            'e164': l.get('e164'),
            'temperatura': temp,
            'segmento': l.get('segmento', l.get('turma', '—')),
            'responsavel': l.get('responsavel', ''),
            'ultimo_status': l.get('estagio_funil', l.get('status', '')),
            'mensagem_status': l.get('mensagem_status', ''),
            'ultima_interacao': l.get('ultima_interacao', l.get('data_entrada', '')),
            'proxima_acao': l.get('proxima_acao', ''),
            'observacao': l.get('observacoes', l.get('observacao', ''))
        }

        # Re-classificação: se sem WA (e164 vazio), vai para validar independente do status da mensagem
        if not lead['e164']:
            gkey = '5-sem-contexto-validar'

        grupos[gkey]['leads'].append(lead)
        grupos[gkey]['count'] += 1

    # Ordena dentro de cada grupo por ultima_interacao (mais recente primeiro)
    for g in grupos.values():
        g['leads'].sort(key=lambda x: x.get('ultima_interacao', ''), reverse=True)

    return grupos


def montar_epq(leads_raw):
    """Converte leads_epq_2026-09-15.json em estrutura operacional EPQ."""
    grupos = {
        '1-respondeu-oportunidade': {'titulo': '1. Respondeu / Oportunidade', 'count': 0, 'leads': []},
        '2-quente': {'titulo': '2. Quente', 'count': 0, 'leads': []},
        '3-morno': {'titulo': '3. Morno', 'count': 0, 'leads': []},
        '4-frio': {'titulo': '4. Frio', 'count': 0, 'leads': []},
        '5-sem-contexto-validar': {'titulo': '5. Sem contexto / Precisa validar', 'count': 0, 'leads': []},
    }

    for l in leads_raw.get('leads', []):
        analise = l.get('analise', {})
        temp = str(analise.get('intencao', '')).upper()
        e164 = l.get('e164')

        lead = {
            'id': l.get('id', ''),
            'nome': l.get('nome', ''),
            'whatsapp': l.get('whatsapp_raw', 'n/a'),
            'e164': e164,
            'temperatura': temp,
            'prioridade': analise.get('prioridade', ''),
            'responsavel': l.get('responsavel', ''),
            'concurso': l.get('turma', '—'),
            'ultima_interacao': l.get('ultima_interacao', ''),
            'observacao': l.get('observacao', ''),
            'etapa': l.get('etapa', ''),
            'envio_status': l.get('envio', {}).get('status', '')
        }

        # Classificação
        if temp == 'QUENTE':
            gkey = '2-quente'
        elif temp == 'MORNO':
            gkey = '3-morno'
        elif temp == 'FRIO':
            gkey = '4-frio'
        else:
            gkey = '5-sem-contexto-validar'

        # Re-classificação: sem WA e sem interação real → validar
        if not e164 and not l.get('ultima_interacao'):
            gkey = '5-sem-contexto-validar'

        grupos[gkey]['leads'].append(lead)
        grupos[gkey]['count'] += 1

    for g in grupos.values():
        g['leads'].sort(key=lambda x: x.get('ultima_interacao', ''), reverse=True)

    return grupos


def main():
    b2b_raw = load_json(LEADS_B2B)
    epq_raw = load_json(FULL_EPQ)

    if not b2b_raw:
        print("❌ leads_mei_lier_I.json não encontrado")
        return 1
    if not epq_raw:
        print("❌ leads_epq_2026-09-15.json não encontrado")
        return 1

    b2b_grupos = montar_b2b(b2b_raw)
    epq_grupos = montar_epq(epq_raw)

    b2b_total = sum(g['count'] for g in b2b_grupos.values())
    epq_total = sum(g['count'] for g in epq_grupos.values())

    fila = {
        'meta': {
            'projeto': 'PROSPECCAO CENTRALIZADA — B2B Flávio + EPQ',
            'ultima_atualizacao': datetime.now().isoformat(),
            'fontes': {
                'b2b': LEADS_B2B,
                'epq_completo': FULL_EPQ,
            },
            'historico_envio': f'{BASE}/estado/historico_envio.json',
            'observacao': 'Arquivo unificado para operação. Dados originais preservados.'
        },
        'b2b_flavio': {
            'projeto': 'PROSPECCAO B2B FLAVIO — captacao de clientes para gestao de marketing, trafego e CRM',
            'endpoint_bridge': 'http://localhost:3000/send',
            'endpoint_preview': 'localhost:3000/send (Baileys bridge local)',
            'lista_ativa': {
                'id': '01-ZN-MEIER-I',
                'nome': '01 - Zona Norte / Méier I (LISTA ATIVA — DEFINIDA PARA FRENTE)',
                'regiao': 'Zona Norte',
                'bairro': 'Méier',
                'cidade': 'Rio de Janeiro',
                'estado': 'READY',
                'leads_total': b2b_total,
                'arquivo_leads': LEADS_B2B,
                'proxima_acao': 'VALIDAR pendentes → preparar mensagens → ENVIAR 1 a 1, 10min de intervalo',
                'proxima_lista': '02 - Zona Norte / Cachambi I'
            },
            'grupos_operacionais': b2b_grupos
        },
        'epq': {
            'projeto': 'EPQ — Preparatórios Militares (GCM/PMERJ/PRF): aulas experimentais e captação de alunos',
            'fonte': 'Google Sheets — aba Leads',
            'total_leads': epq_total,
            'grupos_operacionais': epq_grupos
        }
    }

    # Salva fila consolidada
    salvar_json(FILA_CONSOLIDADA, fila)
    print(f"✅ fila-centralizada.json atualizado: {FILA_CONSOLIDADA}")
    print(f"   B2B: {b2b_total} leads · EPQ: {epq_total} leads")

    # Snapshot de auditoria
    snapshot_path = f'{BASE}/estado/painel-ultimo.json'
    snapshot = {
        'data': datetime.now().isoformat(),
        'fila_caminho': FILA_CONSOLIDADA,
        'b2b_total': b2b_total,
        'epq_total': epq_total,
        'b2b_grupos': {k: {'titulo': v['titulo'], 'count': v['count']} for k, v in b2b_grupos.items()},
        'epq_grupos': {k: {'titulo': v['titulo'], 'count': v['count']} for k, v in epq_grupos.items()},
    }
    salvar_json(snapshot_path, snapshot)
    print(f"📸 Snapshot: {snapshot_path}")

    return 0


if __name__ == '__main__':
    exit(main())
