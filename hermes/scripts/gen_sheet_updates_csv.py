#!/usr/bin/env python3
"""Gera o CSV de atualização da planilha EPQ (aba Leads) + doc de apoio.

Saídas:
  ../data/leads_epq_sheet_updates.csv  — backfill pronto p/ sync_epq_sheet.py ou manual
"""
import json, os, csv

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
ds = json.load(open(os.path.join(DATA, "leads_epq_2026-09-15.json"), encoding="utf-8"))
leads = ds["leads"]

# colunas da aba Leads (A=1): A ID, B Data, C Nome, D WhatsApp, E Origem,
# F Turma, G Etapa, H Responsavel, I Ultima, J Dias, K Proximo Follow-up,
# L Objecao/Observacao, M Motivo da Perda, N Status Follow-up, O Prioridade

rows = []  # (linha_sheet=A2.. , coluna, acao, valor/nota)

for l in leads:
    rid = l["id"]
    linha = rid + 2  # linha na aba: linha 1 cabeçalho + linha 2 vazia; lead id N → N+2
    p = l["analise"]["prioridade"]
    motivo = l["analise"]["motivo_parada"]
    # K — Próximo Follow-up (P0/P1 → 15/09/2026; Brenda id 3 fica definido aqui)
    if p in ("P0", "P1"):
        rows.append((linha, "K", "REPLACE", "15/09/2026"))
    elif p in ("P2", "P3"):
        rows.append((linha, "K", "REPLACE", "não agendar (frio)"))

    # O — Prioridade
    rows.append((linha, "O", "REPLACE", p))

    # L — Obs (append do contexto do follow-up)
    sufixo = f"FOLLOW-UP 15/09 ({p}): {motivo}"
    rows.append((linha, "L", "APPEND", sufixo))

# Correções específicas
fc = {(l["id"]): l for l in leads}
fix_turma = {6: "PMERJ", 20: "PMERJ"}  # 'PMERG' digitado
for rid, val in fix_turma.items():
    rows.append((rid + 1, "F", "FIX", f"PMERG→{val}"))

# Mesquita — consolidar a espera real (turma São Gonçalo abre 19/09)
rows.append((42 + 1, "L", "APPEND", "Voltou espontaneamente em 02/09 pedindo previsão — responder com turma São Gonçalo 19/09 e reservar aula experimental."))

csvo = os.path.join(DATA, "leads_epq_sheet_updates.csv")
with open(csvo, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["linha_aba", "id_lead", "coluna", "acao", "valor"])  # id_lead = id real do lead
    for linha, col, acao, valor in sorted(rows):
        # linha+1 => id do lead (linha = id+2; o CSV abaixo guarda apenas referência)
        w.writerow([linha, linha - 2, col, acao, valor])
print("CSV:", csvo, "| linhas:", len(rows))

# resumo por tipo de ação
from collections import Counter
print(Counter(a for _,_,a,_ in rows))