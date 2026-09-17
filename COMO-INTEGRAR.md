# COMO INTEGRAR O FORMULÁRIO AO GOOGLE SHEETS

Este guia ensina como conectar o formulário de `bolsao.html` a uma planilha do Google Sheets, de modo que as inscrições cheguem centralizadas no Drive, sem depender apenas do `localStorage` do navegador.

O mecanismo é um **Google Apps Script** publicado como **Aplicativo da Web**, que recebe os envios em `POST` e os insere numa aba da planilha.

---

## 1. Criar a planilha Google

1. Acesse o Google Drive.
2. Crie uma nova **Planilha** na pasta correspondente ao Bolsão EPQ 2026.
3. Dê um nome fácil de identificar, por exemplo: `Bolsão EPQ 2026 — Inscrições`.

---

## 2. Estrutura da aba

Na aba principal (renomeie para `Inscricoes`, por exemplo), crie exatamente estas colunas, na ordem indicada:

1. Data/Hora
2. Nome
3. E-mail
4. WhatsApp
5. Turma de Interesse
6. Origem
7. Status do Contato
8. Compareceu na Prova
9. Nota
10. % Bolsa
11. Observações

O script insere cada linha seguindo esta ordem. Se a aba tiver outro nome, eu aviso onde ajustar no código.

---

## 3. Criar o Apps Script

1. Na planilha aberta, vá em **Extensões** > **Apps Script**.
2. Apague o código padrão, se houver.
3. Cole o conteúdo do arquivo `apps-script-formulario.gs` que está nesta pasta.
4. Salve o projeto (ícone de disquete ou `Cmd + S`).

---

## 4. Configuração

No arquivo `apps-script-formulario.gs`, localize esta linha:

```js
var SPREADSHEET_ID = "";
```

- Se a planilha que você criou for a **mesma do script**, pode deixar vazio: o script usará a planilha ativa automaticamente.
- Se preferir explicitar, substitua `""` pelo **ID da planilha** (na URL do Google Sheets, o ID vem depois de `/d/` e antes de `/edit`).

Exemplo:

```js
var SPREADSHEET_ID = "1AbCdefGHIjklMnOpQrStUvwXyz123456";
```

Se usar outro nome para a aba de inscrições, ajuste também:

```js
var SHEET_NAME = "Inscricoes";
```

---

## 5. Publicar como Aplicativo da Web

1. No editor do Apps Script, clique em **Implantar** (ícone de seta para cima, ou menu “Implantar”).
2. Escolha **Nova implantação**.
3. No seletor “Selecionar tipo”, escolha **Aplicativo da Web**.
4. Preencha:
   - **Descrição da implantação:** `Bolsão EPQ 2026`
   - **Execute como:** `Proprietário`
   - **Quem tem acesso:** `Qualquer pessoa`
5. Clique em **Implantar**.

---

## 6. Copiar a URL

Após a implantação, uma caixa de diálogo mostrará a URL do Aplicativo da Web.

A URL será algo como:

```
https://script.google.com/macros/s/AbcDefGhiJKLmnopQrsTuvWxYz/exec
```

Copie essa URL. Ela termina em `/exec`.

---

## 7. Configurar a LP

No arquivo `bolsao.html`, localize a constante:

```js
var FORM_ENDPOINT = "";
```

Substitua `""` pela URL copiada, por exemplo:

```js
var FORM_ENDPOINT = "https://script.google.com/macros/s/AbcDefGhiJKLmnopQrsTuvWxYz/exec";
```

Se preferir, também é possível colocar a URL diretamente ao lado do comentário que já foi inserido mais acima no mesmo trecho do formulário:

```html
<!-- Integração Google Apps Script: ver COMO-INTEGRAR.md -->
```

Depois de configurado, cada novo envio do formulário será guardado 국소mente no navegador **e** enviado para a planilha Google.

---

## 8. Testar a integração

1. Abra a LP `bolsao.html` em um navegador.
2. Preencha o formulário com dados de teste.
3. Confirme a inscrição.
4. Abra a planilha Google e verifique se a linha chegou na aba `Inscricoes`.

A linha deve ter:

- Data/Hora = data/hora do envio
- Nome, E-mail, WhatsApp, Turma de Interesse = preenchidos pelo formulário
- Origem = `LP Bolsão`
- Status do Contato = `Novo`
- Compareceu na Prova, Nota, % Bolsa, Observações = vazios

Se a linha não aparecer, verifique:

- se a implantação está **Ativa**
- se o **Execute como** está como **Proprietário**
- se o **Quem tem acesso** está como **Qualquer pessoa**
- se `FORM_ENDPOINT` está exatamente igual à URL do `/exec`
- se os dados enviados passaram pela validação mínima do script

---

## Observações importantes

- Não coloque tokens, senhas, chaves de API ou credenciais no código do Apps Script.
- O único dado sensível necessário é o ID da planilha, e ele não é secreto.
- A planilha local `Inscricoes-Bolsao-EPQ-2026.xlsx` continua útil para manipulação offline e para o script `importar-leads.py`, mas os dados do formulário chegam primeiro à planilha Google.
