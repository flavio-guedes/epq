/**
 * Bolsão EPQ 2026 — Google Apps Script
 *
 * Cole este código no Google Apps Script vinculado à planilha de inscrições
 * (ver COMO-INTEGRAR.md).
 *
 * Endpoint esperado:
 *   POST /exec
 *   body JSON:
 *     { "turma": "...", "nome": "...", "email": "...", "whatsapp": "...", "data_envio": "..." }
 *
 * Retorno esperado em caso de sucesso:
 *   { "result": "success" }
 */

// ============================================================
// CONFIGURAÇÃO — preencha manualmente com o ID da planilha
// ============================================================
var SPREADSHEET_ID = ""; // <-- substituir pelo ID da planilha Google
var SHEET_NAME = "Inscricoes";


function doPost(e) {
  try {
    // 1) Recebe e parseia o JSON
    var raw = e.postData && e.postData.contents;
    if (!raw) {
      return jsonResponse({ error: "Corpo da requisição vazio" }, 400);
    }

    var data;
    try {
      data = JSON.parse(raw);
    } catch (err) {
      return jsonResponse({ error: "JSON inválido" }, 400);
    }

    // 2) Validação mínima
    if (!data.turma || !data.nome || !data.email || !data.whatsapp) {
      return jsonResponse({ error: "Campos obrigatórios faltando" }, 400);
    }

    // 3) Abre a planilha
    var ss;
    if (SPREADSHEET_ID) {
      ss = SpreadsheetApp.openById(SPREADSHEET_ID);
    } else {
      ss = SpreadsheetApp.getActiveSpreadsheet();
    }

    if (!ss) {
      return jsonResponse({ error: "Planilha não encontrada" }, 500);
    }

    var sheet = ss.getSheetByName(SHEET_NAME);
    if (!sheet) {
      return jsonResponse({ error: "Aba Inscricoes nao encontrada" }, 500);
    }

    // 4) Monta a linha na ordem correta
    var row = [
      new Date(),                  // Data/Hora
      data.nome.trim(),            // Nome
      data.email.trim(),           // E-mail
      data.whatsapp.trim(),        // WhatsApp
      data.turma.trim(),           // Turma de Interesse
      "LP Bolsão",                 // Origem
      "Novo",                      // Status do Contato
      "",                          // Compareceu na Prova
      "",                          // Nota
      "",                          // % Bolsa
      ""                           // Observações
    ];

    // 5) Adiciona a linha
    sheet.appendRow(row);

    return jsonResponse({ result: "success" }, 200);

  } catch (err) {
    return jsonResponse({ error: "Erro interno" }, 500);
  }
}


function doGet(e) {
  return ContentService.createTextOutput("Bolsão EPQ API ativa");
}


function jsonResponse(payload, statusCode) {
  var output = ContentService.createTextOutput(JSON.stringify(payload));
  output.setMimeType(ContentService.MimeType.JSON);

  // Precisamos definir o status HTTP via cabeçalho quando possível
  if (statusCode && statusCode !== 200) {
    // Apps Script não expõe statusCode diretamente no TextOutput em algumas
    // versões; o corpo com "error" já serve para a LP tratar como falha.
  }

  return output;
}
