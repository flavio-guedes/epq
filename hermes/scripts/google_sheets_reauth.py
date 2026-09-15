#!/usr/bin/env python3
"""Reautoriza o acesso do Google Sheets (CRM EPQ).

Fluxo de 1 clique:
  1. Lê o client secret em ~/.hermes/google_client_secret.json
  2. Abre/gera URL de consentimento (run_local_server)
  3. Salva token renovado em ~/.hermes/google_token.json
Uso:  python google_sheets_reauth.py   (depois rode sync_epq_sheet.py)

Scopes requeridos: spreadsheets (token dedicado, não afeta gmail/calendar do hermes).
Caso o token antigo esteja revogado, este fluxo cria um novo.
"""
import os, sys, json, time, socket

BASE = os.path.expanduser("~/.hermes")
CLIENT = os.path.join(BASE, "google_client_secret.json")
TOKEN = os.path.join(BASE, "google_sheets_token.json")
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]


def main():
    if not os.path.exists(CLIENT):
        sys.exit(f"Faltando client secret: {CLIENT}")
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.oauth2.credentials import Credentials
    except ImportError:
        sys.exit("pip install google-auth-oauthlib google-api-python-client no venv google_workspace_venv")

    # permite reutilizar um token ainda válido (não força nova tela desnecessária)
    if os.path.exists(TOKEN):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)
            if creds and creds.valid:
                print("Token já válido em", TOKEN)
                return
        except Exception:
            creds = None
    else:
        creds = None

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT, SCOPES, redirect_uri="http://localhost")

    if sys.stdin.isatty() and not os.environ.get("DISPLAY") and not os.environ.get("SSH_CONNECTION"):
        # sessão headless: imprime URL para colar o código
        auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
        print("\n== AUTORIZAÇÃO GOOGLE (CRM EPQ) ==")
        print("1. Abra a URL abaixo no navegador do Flávio:")
        print("   ", auth_url)
        print("2. Aprove o acesso e copie o código/autorize.\n")
        code = input("Código de autorização: ").strip()
        creds = flow.fetch_token(code=code)
    else:
        creds = flow.run_local_server(port=0, prompt="consent", authorization_prompt_message="Autorize o acesso ao Google Sheets (CRM EPQ)")

    with open(TOKEN, "w", encoding="utf-8") as f:
        f.write(creds.to_json())
    print("OK token gravado:", TOKEN)
    print("Validado para scopes:", creds.scopes)


def wait_for_url():
    """printa a porta se precisar (apenas para diagnóstico)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        print("porta pick:", s.getsockname()[1])


if __name__ == "__main__":
    main()