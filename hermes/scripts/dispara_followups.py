#!/usr/bin/env python3
"""Dispara a fila de follow-up EPQ via WhatsApp (hermes send → Baileys).

Uso:
  python dispara_followups.py                 # dry-run (mostra o plano, não envia)
  python dispara_followups.py --go            # envia de fato (respeita janela 08:00–20:00 BRT)
  python dispara_followups.py --go --force    # envia ignorando a janela (cuidado: fora de horário comercial)
  python dispara_followups.py --only P0 --go  # só prioridade P0
  python dispara_followups.py --id 5 --go     # só o lead 5

Janela padrão: 08:00–20:00 (America/Sao_Paulo). Fora dela exige --force.
Log de envios: hermes/data/leads_epq_dispatch_log.jsonl
"""
import argparse, json, os, subprocess, sys, datetime

DATA = os.path.expanduser("~/HermesWorkspace/hermes/data")
QUEUE = os.path.join(DATA, "leads_epq_dispatch_queue.json")
LOG = os.path.join(DATA, "leads_epq_dispatch_log.jsonl")

HERMES_BIN_CANDIDATES = [
    os.path.expanduser("~/.hermes/hermes-agent/venv/bin/hermes"),
    os.path.expanduser("~/.hermes/hermes-agent/.venv/bin/hermes"),
]
HERMES = next((b for b in HERMES_BIN_CANDIDATES if os.path.exists(b)), "hermes")

BRT = datetime.timezone(datetime.timedelta(hours=-3))

def now_brt():
    return datetime.datetime.now(BRT)

def within_window(force):
    if force:
        return True, None
    h = now_brt().hour
    if 8 <= h < 20:
        return True, None
    return False, "fora da janela 08:00–20:00 BRT (use --force se realmente for enviar)"

def run_send(jid, msg):
    return subprocess.run(
        [HERMES, "send", "--to", f"whatsapp:{jid}", msg, "--json"],
        capture_output=True, text=True, timeout=90,
    )

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--go", action="store_true", help="Executa os envios (padrão: dry-run)")
    ap.add_argument("--force", action="store_true", help="Ignora a janela de horário")
    ap.add_argument("--only", choices=["P0", "P1"], help="Filtra por prioridade")
    ap.add_argument("--id", type=int, help="Envia apenas o lead com este id")
    args = ap.parse_args()

    if not os.path.exists(QUEUE):
        sys.exit("Fila não encontrada: " + QUEUE)
    queue = json.load(open(QUEUE, encoding="utf-8"))
    itens = queue["itens"]
    if args.only:
        itens = [i for i in itens if i["prioridade"] == args.only]
    if args.id:
        itens = [i for i in itens if i["id"] == args.id]

    if not itens:
        print("Nenhum item no filtro.")
        return

    print(f"hermes: {HERMES}")
    print(f"modo: {'ENVIO REAL' if args.go else 'dry-run'} | itens: {len(itens)} | hora BRT: {now_brt().strftime('%H:%M')}")
    print("-" * 80)

    ok, why = within_window(args.force)
    if not ok:
        print(f"⚠ {why}")
        if args.go:
            print("Nenhuma mensagem foi enviada.")
            return
        print("(dry-run continua — sem envio)")

    sent = {}
    for i in itens:
        if not i.get("jid"):
            print(f"[{i['id']:>2}] {i['nome']:<32} SEM NÚMERO — pulado")
            continue
        jid = i["jid"]; p = i["prioridade"]
        print(f"[{i['id']:>2}] {i['nome']:<32} {p} {jid:<28}")
        print(f"      msg: {i['mensagem'][:80]}...")
        if not args.go or not ok:
            sent[i["id"]] = {"nome": i["nome"], "status": "dry-run"}
            continue
        proc = run_send(jid, i["mensagem"])
        entry = {
            "ts": now_brt().isoformat(),
            "id": i["id"], "nome": i["nome"], "jid": jid,
            "prioridade": p, "responsavel": i["responsavel"],
            "exit": proc.returncode, "stdout": proc.stdout.strip()[:500],
            "stderr": proc.stderr.strip()[:500],
        }
        sent[i["id"]] = entry
        flag = "OK" if proc.returncode == 0 else "FALHA"
        print(f"      → {flag} (exit {proc.returncode})")
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    resumo_ok = [v for v in sent.values() if v.get("status") == "dry-run" or v.get("exit") == 0]
    print("-" * 80)
    if args.go and ok:
        print(f"Enviados com sucesso: {sum(1 for v in sent.values() if v.get('exit')==0)} | falhas: {sum(1 for v in sent.values() if v.get('exit') not in (0,None))}")
    else:
        print("Dry-run: nenhuma mensagem foi enviada. Repita com --go para efetivar (janela 08:00-20:00 BRT).")

if __name__ == "__main__":
    main()