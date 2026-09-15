# Sales Enablement Agent

Agente especialista de vendas integrado ao ecossistema Hermes/ATLAS.

## Estrutura
- `agent/`: identidade, regras e workflows.
- `intelligence/`: lead scoring, deal health, next best action.
- `playbooks/`: ICPs, personas, objeções, mensagens.
- `crm/`: integração leve com CRM existente via estado local.
- `followups/`: follow-up engine.
- `analytics/`: pipeline, conversão e WHAT TO DO NOW.
- `memory/`, `logs/`: memória e auditoria.
- `tests/`: testes obrigatórios.

## Execução
```bash
python -m pytest sales_enablement_agent/tests -v
```

## Integração
Usa `sales_enablement_agent.crm.adapter.CRMAdapter` para ler/escrever leads e follow-ups sem duplicar o CRM existente. Para integração total com `crm-state`, estenda `CRMAdapter` para consumir `state.json` via API/arquivo.
