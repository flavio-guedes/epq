# Operação EPQ — Log 15/09/2026

## Resumo
Ciclo de recuperação de leads concluído: 42 leads analisados, mensagens prontas para
todos, fila de disparo 18 itens (P0/P1), relatório diário gerado e painel central
atualizado. Escrita na planilha permanece **bloqueada** (token revogado).

## Números
- 42 leads · P0=9 · P1=13 · P2=19 · P3=1
- quente=4 · morno=14 · frio=24
- Responsáveis: Andressa=14, Clara=13, Ronan=15
- Sem telefone: 6 (ids 11,13,14,15,35,37) → fora da fila
- Fila P0/P1 com nº: 18 itens (P0=8, P1=10)
- P0: 1,2,5,6,12,15,16,20,42 · P1: 3,4,7,8,9,10,11,13,14,17,18,19,38

## Artefatos produzidos
| Arquivo | Estado |
|---|---|
| `hermes/data/leads_epq_2026-09-15.json` (42 leads) | ok |
| `hermes/data/leads_epq_followup_plan.md` (21.821 b) | ok |
| `hermes/data/leads_epq_dispatch_queue.json` (18 itens) | ok |
| `hermes/data/leads_epq_sheet_updates.csv` (129 células) | ok |
| `leads_15_09.html` (37.291 b) | ok |
| `hermes/central.html` (painel + EPQ_LEADS + automação + bloqueador) | ok — node --check OK (2 scripts) |

## Fila WhatsApp (18)
IDs por ordem de prioridade: 1,2,5,6,12,16,20,42 (P0) e 3,4,7,8,9,10,17,18,19 (P1).
ids 15 (P0) e 11,13,14 (P1) sem telefone. 7 e 10 → mesmo número (5521990439709).

## Decisões
- **Não** enviar mensagens de madrugada. Disparo manual na janela 08:00–20:00 BRT:
  `python hermes/scripts/dispara_followups.py --go` (ou `--only P0` / `--id N`).
- **Escrita na planilha** exige reconsentimento (token revogado). Fluxo:
  1. `python hermes/scripts/google_sheets_reauth.py` (1 clique)
  2. `python hermes/scripts/sync_epq_sheet.py --apply`

## Correções aplicadas
- Normalizador de telefone: remove apenas sufixo `(N)`; JIDs validados 55-13d
  (`jids inválidos: []`).
- `central.html`: EPQ_LEADS reinserida limpa após splice quebrado (42 únicos);
  nota da automação corrigida.

## Atualização 09:30 — ZERADO
- Planilha **convertida** p/ Google Sheets nativo: `1wD4Xi5HGq680i27WdFm1Ym4aNiTHnShJYTYrQe8g5hs`
  (mesmas abas/gids, dados preservados). `.xlsx` original bloqueava escrita pela API.
- Token **dedicado** `~/.hermes/google_sheets_token.json` obtido via OAuth (porta 53197,
  sem PKCE — verifiers anteriores davam invalid_grant). `google_token.json` do hermes intacto.
- Backfill **aplicado**: 129 células (K=Próximo Follow-up P0/P1→15/09 e P2/P3→'não agendar',
  O=Prioridade, L=FOLLOW-UP 15/09, F=PMERG→PMERJ). Verificado 0 inconsistências:
  9 P0 · 13 P1 · 19 P2 · 1 P3, 22 P0/P1 com follow-up na L.
- ⚠ Correção de offset: na aba Leads, lead N fica na **linha N+2** (linha 2 vazia).
  `gen_sheet_updates_csv.py` usa `id+2`; `sync_epq_sheet.py` aponta p/ nova planilha.

## Pendências
- [x] Reautorizar Google (token dedicado ok).
- [x] Aplicar backfill após reauth (sync --apply, 129 células).
- [ ] Disparar follow-ups na janela 08:00–20:00 (`dispara_followups.py --go`).