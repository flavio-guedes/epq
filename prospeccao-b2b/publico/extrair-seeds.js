#!/usr/bin/env node
// extrair-seeds.js — extrai SEED_GRUPS, SEED_LEADS, SEED_OPORTUNIDADES como JSON
const fs = require('fs');
const path = require('path');
const vm = require('vm');

// __dirname = /Users/mac/HermesWorkspace/prospeccao-b2b/publico
// Precisamos subir 2 niveis para chegar em HermesWorkspace
const diretorioRaiz = path.resolve(__dirname, '..', '..');
const files = [
  path.join(diretorioRaiz, 'b2b-groups', 'js', 'data.js'),
  path.join(diretorioRaiz, 'b2b-groups', 'data', 'data.js'),
  path.join(diretorioRaiz, 'b2b-groups', 'js', 'seed-inline.js'),
];

let filePath = null;
for (const fp of files) {
  if (fs.existsSync(fp)) { filePath = fp; break; }
}

if (!filePath) {
  console.error('ERRO: arquivo nao encontrado');
  console.error('Procurado em:', files.map(f => f).join('\n'));
  process.exit(1);
}

const code = fs.readFileSync(filePath, 'utf-8');
console.error('Lido:', filePath);

// Executar no contexto global do node
const wrappedCode = `
  (function() {
    ${code}
    return {
      SEED_GRUPS: typeof SEED_GRUPS !== 'undefined' ? SEED_GRUPS : [],
      SEED_LEADS: typeof SEED_LEADS !== 'undefined' ? SEED_LEADS : [],
      SEED_OPORTUNIDADES: typeof SEED_OPORTUNIDADES !== 'undefined' ? SEED_OPORTUNIDADES : [],
    };
  })()
`;

try {
  const result = vm.runInThisContext(wrappedCode);
  console.log(JSON.stringify(result, null, 2));
} catch (e) {
  console.error('Erro:', e.message);
  console.error(e.stack);
  process.exit(1);
}
