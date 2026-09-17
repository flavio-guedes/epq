# Bolsão EPQ 2026

## Finalidade

Esta pasta contém a Landing Page do **Bolsão EPQ 2026**, evento de prova de bolsas de estudo do EPQ para concursos de segurança pública.

- **Evento:** Bolsão EPQ 2026 — prova de bolsas
- **Data:** 03/10/2026
- **Local:** Nilópolis – RJ
- **Arquivo principal:** `bolsao.html`

## Funcionamento

A LP é um HTML estático, autocontido, com imagem de fundo embutida e formulário de inscrição.

- O **formulário** captura turma de interesse, nome, e-mail e WhatsApp.
- As inscrições são armazenadas **localmente** via `localStorage` no navegador de quem preenche.
- O painel `?admin=1` mostra os leads capturados no navegador atual e permite **exportação em CSV**.
- Quando configurado, o formulário também envia uma cópia para um **endpoint remoto** via `fetch(POST)` — por padrão um **Google Apps Script** publicado como Aplicativo da Web, conforme documentado em `COMO-INTEGRAR.md`.
- Se `FORM_ENDPOINT` estiver vazia, o formulário mantém apenas o comportamento local.

## URLs

- **URL raiz:** `https://flavio-guedes.github.io/epq/`
  - Redireciona para `bolsao.html` via `index.html`.
- **URL direta:** `https://flavio-guedes.github.io/epq/bolsao.html`

## Importação

O script `importar-leads.py` importa leads a partir de um CSV para a planilha local `Inscricoes-Bolsao-EPQ-2026.xlsx`.

Uso:

```bash
python3 importar-leads.py caminho/do/arquivo.csv
```

O CSV esperado contém: `nome,email,whatsapp,turma,data_envio`.

O script identifica duplicidade por e-mail, não importa e-mails já existentes e preenche Origem e Status do Contato automaticamente.

## Integração

A integração remota do formulário depende de um **Google Apps Script** documentado em:

`COMO-INTEGRAR.md`

Quando a URL `/exec` estiver disponível, basta colá-la na constante `FORM_ENDPOINT` de `bolsao.html`.
