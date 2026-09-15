#!/usr/bin/env python3
"""Sincroniza o backfill do CRM EPQ de volta à aba Leads.

Fonte: data/leads_epq_sheet_updates.csv (gerado por gen_sheet_updates_csv.py).

Como a aba atual é lida via export CSV anônimo (docs.google.com .../export?format=csv),
todo o merge (REPLACE/APPEND/FIX) é feito localmente e gravado num único
batchUpdate da API v4:
  - REPLACE: escreve o valor na célula
  - APPEND : concatena o sufixo ao valor lido do CSV
  - FIX    : substitui 'de→para' no valor lido do CSV

Uso:  python sync_epq_sheet.py [--apply]
Sem --apply roda o dry-run e valida o token.
"""
import os, sys, csv, argparse, json, io

BASE = os.path.expanduser("~/.hermes")
SHEET_ID = "1wD4Xi5HGq680i27WdFm1Ym4aNiTHnShJYTYrQe8g5hs"
SHEET_ABA = "Leads"
GID_LEADS = 800179006
COR = "A:O"

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "leads_epq_sheet_updates.csv")
TOKEN = os.path.join(BASE, "google_sheets_token.json")


def get_service():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    if not os.path.exists(TOKEN):
        sys.exit("Token ausente. Rode: python hermes/scripts/google_sheets_reauth.py")
    creds = Credentials.from_authorized_user_file(TOKEN, scopes=[
        "https://www.googleapis.com/auth/spreadsheets"])
    if not creds.valid and not creds.expired:
        sys.exit("Token sem refresh válido. Rode google_sheets_reauth.py (1 clique).")
    try:
        if creds.expired:
            creds.refresh(Request())
    except Exception as e:
        sys.exit(f"Refresh do Google falhou ({e}). Consentimento necessário:\n"
                 "  python hermes/scripts/google_sheets_reauth.py   (1 clique)\n"
                 "  Depois: python hermes/scripts/sync_epq_sheet.py --apply")
    return build("sheets", "v4", credentials=creds)


def load_plan():
    rows = []
    with open(CSV_PATH, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "linha": int(r["linha_aba"]), "id": int(r["id_lead"]),
                "col": r["coluna"], "acao": r["acao"], "valor": r["valor"],
            })
    return rows


def fetch_aba_csv(url, token):
    import urllib.request
    req = urllib.request.Request(url)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read().decode("utf-8")
    return csv.reader(io.StringIO(raw))


def current_values():
    """Retorna {linha: {col: valor}} a partir do export CSV anônimo da aba Leads."""
    import urllib.parse
    url = (f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export"
           f"?format=csv&gid={GID_LEADS}")
    try:
        rows = list(fetch_aba_csv(url, None))
    except Exception:
        # fallback autenticado
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        creds = Credentials.from_authorized_user_file(TOKEN)
        if creds.expired:
            creds.refresh(Request())
        rows = list(fetch_aba_csv(url, creds.token))
    out = {}
    for i, row in enumerate(rows):
        linha = i + 1
        out[linha] = {chr(ord("A") + c): v for c, v in enumerate(row[:15])}
    return out


def dry_run(plan, cur):
    print(f"Plano ({len(plan)} operações) para {SHEET_ABA}!{COR} de {CSV_PATH}")
    c = {}
    for o in plan:
        c[o["acao"]] = c.get(o["acao"], 0) + 1
    print("  por ação:", json.dumps(c))
    print("  colunas:", sorted({o['col'] for o in plan}))
    if cur:
        print(f"  aba lida: {len(cur)} linhas (export CSV)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    plan = load_plan()

    try:
        svc = get_service()
    except ImportError as e:
        sys.exit(f"pip install google-api-python-client google-auth no venv google_workspace_venv: {e}")

    cur = current_values() if args.apply else {}
    dry_run(plan, cur)
    if not args.apply:
        print("DRY-RUN: use --apply para escrever na planilha.")
        return

    ops = []
    for o in plan:
        rng = f"{SHEET_ABA}!{o['col']}{o['linha']}"
        if o["acao"] == "REPLACE":
            valor = o["valor"]
        else:
            cur_val = (cur.get(o["linha"], {}).get(o["col"]) or "").strip()
            if o["acao"] == "FIX":
                de, para = o["valor"].split("→", 1)
                valor = cur_val.replace(de, para) if de in cur_val else cur_val
            else:  # APPEND
                valor = (cur_val + " | " + o['valor']) if cur_val else o["valor"]
        ops.append({"range": rng, "values": [[valor]]})

    for i in range(0, len(ops), 100):
        chunk = ops[i:i + 100]
        svc.spreadsheets().values().batchUpdate(
            spreadsheetId=SHEET_ID,
            body={"valueInputOption": "USER_ENTERED", "data": chunk},
        ).execute()
    print(f"OK sincronizado {len(ops)} células na aba {SHEET_ABA}.")


if __name__ == "__main__":
    main()