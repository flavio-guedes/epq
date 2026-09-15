# Google Sheets (CRM EPQ) — acesso de escrita

## Estado (15/09/2026) — RESOLVIDO
- O arquivo original era **.xlsx** (`Planilha_Acompanhamento_Leads_EPQ.xlsx`) e a API
  Sheets bloqueava escrita: `This operation is not supported for this document. The
  document must not be an Office file.`
- Convertido para **Google Sheets nativo** → nova planilha:
  `1wD4Xi5HGq680i27WdFm1Ym4aNiTHnShJYTYrQe8g5hs` (mesmas abas/gids, dados preservados).
- Token OAuth **dedicado** `~/.hermes/google_sheets_token.json` (escopo spreadsheets),
  obtido via fluxo localhost:53197. NO MEXER em `google_token.json` (do hermes — gmail/calendar).
- Backfill de 129 células aplicado com sucesso
  (`sync_epq_sheet.py --apply`).
- ⚠ Layout da aba Leads: linha 1 cabeçalho, linha 2 vazia, lead N na linha N+2.
  `gen_sheet_updates_csv.py` já usa `linha = id + 2`.

## Reautorização (se o token dedicado expirar/revogar)
1. `cd ~/HermesWorkspace`
2. `/Users/mac/.hermes/google_workspace_venv/bin/python hermes/scripts/google_sheets_reauth.py`
   - Abre navegador (consentimento) e grava em `~/.hermes/google_sheets_token.json`.
   - Em sessão headless imprime a URL para autorizar e pede o código.
3. Rodar `sync_epq_sheet.py --apply` após.

## Scripts
- `hermes/scripts/sync_epq_sheet.py` — aplica backfill (lê aba atual via export CSV,
  merge REPLACE/APPEND/FIX local, grava via `values().batchUpdate`).
- `hermes/scripts/gen_sheet_updates_csv.py` — gera `data/leads_epq_sheet_updates.csv`
  a partir do dataset do dia.
- `hermes/scripts/google_sheets_reauth.py` — (documentado acima) fluxo de consentimento.

## Diagnóstico do problema original
- `google_token.json` (do hermes) foi revogado (`invalid_grant`) — nunca usar;
- `gcloud` (`flavioguedesmkt@gmail.com`) só tem `cloud-platform` → `403`.