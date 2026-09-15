# Sales Enablement Agent — Workflows

## Fluxos canônicos

### 1. Sales Brief
Entrada: lead_id + contexto
Saída: Sales Brief completo

1. Validar dados mínimos.
2. Carregar histórico do lead no CRM existente.
3. Calcular Sales Score.
4. Avaliar Deal Health.
5. Gerar Next Best Action.
6. Selecionar materiais comerciais relevantes.
7. Preparar mensagens por canal e estágio.
8. Gerar follow-up recomendado.
9. Registrar log estruturado.

### 2. Reunião comercial
Entrada: lead_id + agenda
Saída: Sales Meeting Brief

Antes:
- Identificação
- Contexto
- Histórico
- Dores prováveis
- Objeções prováveis
- Argumentos relevantes
- Cases relevantes
- Objetivo da reunião
- Próximo passo desejado

Depois:
- Necessidade
- Orçamento
- Timing
- Decisor
- Objeções
- Compromisso
- Próximo passo
- Probabilidade de fechamento
- Atualização do CRM

### 3. Follow-up Engine
Entrada: leads ativos
Saída: lista priorizada

1. Listar leads sem próximo passo definido.
2. Identificar leads com último contato vencido.
3. Calcular prioridade por potencial comercial.
4. Gerar WHAT TO DO NOW com 3–10 ações.

### 4. Objection Handling
Entrada: objeção + contexto do lead
Saída: classificação + resposta + próxima pergunta + próximo passo

1. Identificar padrão da objeção.
2. Classificar por tipo.
3. Selecionar resposta do playbook.
4. Personalizar pelo contexto.
5. Sugerir próxima pergunta para destravar.
6. Indicar próximo passo recomendado.

### 5. Sales Learning
Entrada: interações e resultados
Saída: Sales Learning Report

1. Consolidar mensagens, respostas, reuniões, conversões e perdas.
2. Identificar padrões por canal, horário, segmento, persona.
3. Gerar relatório com o que funciona, o que não funciona e experimentos sugeridos.

## Ordem de execução
Sempre executar:
1. ANÁLISE
2. PREPARAÇÃO
3. APROVAÇÃO QUANDO NECESSÁRIO
4. EXECUÇÃO AUTORIZADA
5. REGISTRO
