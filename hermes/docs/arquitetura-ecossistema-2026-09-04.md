# Arquitetura do Ecossistema de Agentes e Operações — Pesquisa Estrutural
**Data da pesquisa:** 2026-09-04  
**Escopo:** Hermes / ATLAS / EPQ / Job Hunter / Prospecção / Produção / Infraestrutura  
**Status:** CONFIRMADO / HIPÓTESE / CONFLITO  

---

# 01 — EXECUTIVE SUMMARY

**CONFIRMADO**
- O usuário já opera múltiplos domínios com entregáveis reais: EPQ comercial/CRM, painéis HTML estáticos, deploy em GitHub Pages, prospecção, job hunter, propostas, conteúdo e produção.
- Já existe uma hierarquia operacional informal: usuário → ATLAS → HERMES → especialistas/skills.
- Existem automações noturnas e jobs agendados no Hermes, com pelo menos 2 jobs executando de forma recorrente.
- O ecossistema não é teórico; já possui dados, scripts, integrações e integridade comercial/operacional.

**HIPÓTESE**
- O principal gargalo hoje não é falta de agentes, mas sim falta de estado, governança, observabilidade e contratos entre camadas.
- A evolução saudável depende mais de padronização, backlog, retries e isolamento do que de mais LLM calls.
- A adoção antecipada de frameworks “pesados” tende a aumentar custo e complexidade sem resolver o problema central.

**CONFLITO**
- A camada ATLAS como interface pessoal ainda é conceitual, sem implementação operacional unificada; há risco de sobreposição com o próprio Hermes.
- Existem múltiplas skills de orquestração/supervisão disponíveis, mas não há uma regra clara de quando usar cada uma.

**Recomendação direta**
- Não reconstruir.
- Introduzir higiene operacional primeiro: inventário, estados, observabilidade, governança e contratos.
- Automatizar depois o que já tem evidência de repetição e retorno.
- Aumentar autonomia só após observabilidade + recuperação.

---

# 02 — MAPA ATUAL

## 2.1 Camada Humana
- Decisão estratégica: usuário.
- Contexto pessoal, prioridades e rotina: ATLAS (conceitual).

## 2.2 Camada Hermes
- Orquestração via Hermes Agent CLI.
- Profissional de voz e operação no terminal.
- Memória cross-session.
- Cron jobs e delegação.
- Browser automation e desktop background.

## 2.3 Camada de Skills
- Mais de 250 skills disponíveis.
- Domínios relevantes confirmados:
  - autonomous-ai-agents
  - project
  - prospecting
  - content
  - github
  - software-development
  - research
  - marketing-ops
  - communication

## 2.4 Camada de Projetos e Artefatos
CONFIRMADO:
- Repositórios ativos no workspace:
  - painel-semanal
  - pipeline-job-hunter
  - prospeccao
  - founder-radar
  - crm-acao-web
  - epq-aulao-webhook
  - crm-backend
  - hermes-guide
  - propostas
  - repo estrutura crm/drive

- Painéis e entregáveis:
  - CRM HTML estático
  - leads.html otimizado
  - command_center_full.html
  - painel-conteudo.html
  - command-center
  - forecasting
  - cronograma
  - publico
  - playbook atendimento
  - playbook marketing
  - relatórios de ads
  - forecast HTML

- Dados:
  - contatos.json
  - crm_unified.json
  - crm_final.json
  - threads exportadas
  - research_raw.json
  - search_results.json
  - JSONs de prospecção e leads

- Scripts relevantes:
  - sync_crm.py
  - enrich_crm.py
  - merge_all_sources.py
  - process_threads.py
  - exportador_contatos_curriculos.js
  - integração Google Sheets
  - painel JS/data embarcados

## 2.5 Integrações Confirmadas
- GitHub Pages como padrão de deploy.
- Google Drive/Sheets como repositório de dados e estado.
- Telegram/WhatsApp como canais de saída.
- Browser automation como via dominante de integração frágil.

---

# 03 — MAPA DE ATIVIDADES

| Atividade | Objetivo | Frequência | Responsável | Dependência humana | Dependência autenticação | Ferramentas | Integrações | Observabilidade | Confiabilidade | Prioridade |
|---|---|---|---|---|---|---|---|---|---|---|
| EPQ CRM / leads / follow-up | Nutrir, classificar e converter leads | diária | agente + humano | média | média | HTML, JSON, Sheets, scripts Python | WhatsApp, Drive, Telegram | 20/100 | 35/100 | P0 |
| Atendimento / conversas / forense | Transformar conversas em ação | diária | humano + agente assistivo | alta | alta | HTML, JSON | WhatsApp | 15/100 | 30/100 | P0 |
| Anúncios Meta / conteúdo / trafégo | Gerar demanda qualificada | semanal | humano + agente | média | média | HTML, markdown | Meta | 10/100 | 25/100 | P1 |
| Prospecção LinkedIn / outreach | Abrir portas comerciais | semanal | humano + agente | alta | alta | browser automation, HTML | LinkedIn | 10/100 | 25/100 | P1 |
| Job Hunter | Acompanhar vagas e candidaturas | diária | agente | baixa | baixa | JSON, scripts | Telegram | 20/100 | 40/100 | P1 |
| Founder Radar | Identificar parceiros/oportunidades | diária | agente | baixa | baixa | Python, JSON | web, local | 15/100 | 35/100 | P2 |
| Pesquisa de mercado / B2B | Mapear mercados e referências | eventual | humano + agente | baixa | baixa | markdown, web | web | 10/100 | 30/100 | P2 |
| Produção / design / propostas / landing | Criar materiais comerciais | eventual | humano + agente | baixa | baixa | HTML/CSS, imagens, JS | GitHub Pages, Drive | 10/100 | 40/100 | P1 |
| Treinamento noturno | Aperfeiçoar agentes e relatar | noturna | agente | baixa | baixa | skills, sessions | Hermes internals | 15/100 | 30/100 | P2 |
| Deploy / publicação | Levar painel ou página ao ar | eventual | humano + agente | baixa | baixa | git, GitHub CLI, Pages | GitHub | 15/100 | 45/100 | P1 |
| Organização de pastas / docs | Estruturar pastas, base e governança | eventual | humano + agente | baixa | baixa | Drive, filesystem | Google Drive | 10/100 | 30/100 | P2 |

---

# 04 — MAPA DE GARGALOS

| Gargalo | Impacto | Causa raiz confirmada | Classificação |
|---|---|---|---|
| Sem estado confiável de tarefa | alto | ausência de camada transacional/pipeline | CONFIRMADO |
| Dependência excessiva de browser automation | alto | ausência de APIs/MCP/webhooks como primeira via | CONFIRMADO |
| Dados espalhados entre JSONs e painéis | alto | ausência de fonte única e contratos de dados | CONFIRMADO |
| Falta de observabilidade | alto | logs isolados, sem tracing, sem métricas | CONFIRMADO |
| Automações sem retry/timeout formal | médio | execução por prompt/shell sem guardrails | CONFIRMADO |
| Falta de governança/approval gates | médio | autonomia sem política explícita | CONFIRMADO |
| ATLAS conceitual, não operacional | médio | camada de contexto sem implementação | CONFIRMADO |
| Skills duplicadas/overlapping | médio | catálogo grande sem profiler por projeto | CONFIRMADO |
| Falta de versionamento de skills | médio | skills vivem sem estado/changelog | CONFIRMADO |
| Falta de backlog estruturado | médio | tarefas ficam em prompts e memória volátil | CONFIRMADO |
| Integração WhatsApp sem API | médio | automação frágil e bloqueante | CONFIRMADO |
| Falta de staging/rollback deploy | baixo | deploy direto em produção | CONFIRMADO |
| Ausência de testes automatizados | baixo | sem pipeline de regression/evals | CONFIRMADO |

---

# 05 — FRAMEWORK MATRIX

Avaliação focada em: **menor complexidade operacional para o nível atual de autonomia.**

| Tecnologia | Problema resolvido | Benefício | Complexidade | Custo | Lock-in | Maturidade | Nota |
|---|---|---|---:|---:|---:|---:|:---:|
| Cron + scripts + skills atuais | automação repetitiva simples | baixo custo, direto | baixa | baixo | baixo | alta | 7/10 |
| LangGraph | workflows multi-step, estado, ciclos | controle de fluxo e retries | média | médio | médio | média | 7/10 |
| Temporal | workflows long-running, confiabilidade | recuperação, durabilidade | alta | alto | baixo | alta | 6/10 |
| n8n | automação visual, integrações prontas | velocidade operacional | média | médio | baixo | alta | 6/10 |
| OpenAI Agents SDK | orquestração de agentes/tools | simplicidade relativa | média | médio | alto | média | 5/10 |
| CrewAI | times de agentes prontos | rápido para MVPs | média | médio | alto | média | 4/10 |
| Mastra | agentes/workflows JavaScript | ecosystem JS | média | médio | médio | média | 4/10 |
| Google ADK | integração Google/agentes | sinergia Google | média | médio | alto | baixa | 4/10 |
| LangChain | abstração de LLM/tools | ecossistema amplo | média-alta | alto | alto | alta | 5/10 |
| LlamaIndex Workflows | RAG + fluxos | conhecimento + execução | média | médio | médio | média | 5/10 |
| DSPy | prompts como programas | otimização de prompts | média-alta | médio | médio | média | 4/10 |
| Microsoft Agent Framework | enterprise governance | segurança/custódia | alta | alto | alto | média | 3/10 |
| MCP como camada padrão | descoberta/contrato de tools | reduz acoplamento | média | baixo | baixo | média-alta | 7/10 |

**Decisão provisória**
- Fase inicial: manter scripts + skills + camada de estado leve.
- Fase 2: introduzir LangGraph ou workflow determinístico pontual onde houver repetição e risco.
- n8n/Temporal só se houver volume ou duração crítica comprovada.

---

# 06 — TOOL / INTEGRATION MATRIX

| Integração | API/MCP | Webhook | OAuth | Browser | Risco bloqueio | Manutenção | Custo | Estabilidade | Prioridade |
|---|---|---|---|---|---|---|---|---|---|
| GitHub Pages | sim | não | não | não | baixo | baixa | baixo | alta | P0 |
| GitHub CLI / Git | sim | não | token | não | baixo | baixa | baixo | alta | P0 |
| Google Sheets | sim | não | OAuth | não | baixo | média | baixo | alta | P0 |
| Google Drive | sim | não | OAuth | não | baixo | média | baixo | alta | P0 |
| Telegram | sim | sim | não | não | baixo | baixa | baixo | alta | P0 |
| WhatsApp | API Business | sim | sim | alto | alto | alta | médio | média | P1 |
| Meta Ads | sim | sim | OAuth | sim | médio | alta | alto | média | P1 |
| LinkedIn | não | não | OAuth | sim | alto | alta | médio | baixa | P2 |
| E-mail | IMAP/SMTP | não | senha/app | não | médio | média | baixo | média | P1 |
| Navegador geral | não | não | não | sim | alto | alta | variável | baixa | P2 |

**Regra**
- Preferir API/MCP/webhook sempre que tecnicamente viável.
- Browser automation deve ser fallback, não primeira via.

---

# 07 — AGENT ARCHITECTURE

## 7.1 Arquitetura recomendada
```
Usuário
  ↓
ATLAS (contexto, prioridades, políticas)
  ↓
HERMES (orquestração, backlog, approval, routing)
  ↓
┌─────────────────────────────────────────────┐
│ Camada de Workflows + Agents Especializados │
│  • Workflow Engine  • Router  • Skills      │
│  • Observability  • Governance              │
└─────────────────────────────────────────────┘
  ↓
Tools / Integrations / Data
```

## 7.2 Princípios
- **Router-first:** Hermes roteia para workflow quando possível; agente só quando há ambiguidade.
- **Skill-first:** capacidades reutilizáveis antes de prompts ad-hoc.
- **State-first:** sem estado não existe coordenação confiável.
- **Governance-first:** sem approval/policy não existe autonomia segura.
- **Observability-first:** sem tracing/metrícula não existe melhoria contínua.

## 7.3 Padrões preferidos
- Specialist agents para domínios delimitados.
- Planner/executor para tarefas com passos repetitivos.
- Human-in-the-loop por policy, não por falta de infra.

---

# 08 — OPERATING MODEL

## 8.1 Responsabilidades

| Camada | Responsabilidade |
|---|---|
| Usuário | decisão estratégica, investimento, risco maior |
| ATLAS | contexto pessoal, prioridades, agenda, políticas |
| Hermes | orquestração, backlog, status, relatórios, routing |
| Workflows | processos repetitivos determinísticos |
| Agentes | execução especializada com ambiguidade |
| Skills | capacidades reutilizáveis |
| Tools | acesso a sistemas externos |
| Data | estado, histórico, conhecimento |
| Observability | tracing, custo, sucesso, falhas |
| Governance | aprovação, risco, audit log |

## 8.2 Operação diária
- Backlog único.
- Tarefa em um destes estados:
  - Inbox
  - Triaged
  - Ready
  - Running
  - Waiting
  - Blocked
  - Review
  - Done
  - Failed
  - Archived
- Relatório matinal e noturno.

---

# 09 — NIGHT SHIFT ARCHITECTURE

## 9.1 Conceito Night Shift
Depois de /PROJETEM, Hermes deve:
1. capturar backlog
2. triar elegibilidade
3. planejar ordem
4. delegar especialistas
5. executar com timeout e retry
6. validar saída
7. documentar aprendizados
8. atualizar painéis/estado
9. parar diante de bloqueios
10. reportar pela manhã

## 9.2 Regras
- Nenhuma ação reversível sem confirmação quando risco ≥ médio.
- Nenhuma publicação/envio irreversível sem aprovação.
- Nenhuma execução aberta sem timeout.
- Nenhum loop sem saída.
- Nenhuma ação artificial só para gerar atividade.

---

# 10 — GOVERNANCE MODEL

| Ação | Pode executar sozinho | Log + alerta | Precisa aprovação | Não pode |
|---|---|---|---|---|
| Enviar mensagem | mensagens operacionais low-risk | mensagens comerciais | mensagens sensíveis/irreversíveis | spam |
| Publicar | branches/previews | deploy Pages simples | deploy produção/campanha | mudança sem review |
| Excluir/alterar código | não | não | sempre | — |
| Alterar CRM | não | sim | sempre | exclusão massiva sem conferência |
| Alterar campanhas | não | sim | sim | pausar/cancelar sem motivo |
| Candidatar-se | não | não | sempre | — |
| Gastar dinheiro | não | não | sempre | — |
| Acessar dados sensíveis | não | sim | sim | vazamento/export irrestrito |
| Autenticar serviços | não | não | sempre | compartilhar credenciais |
| Tarefa externa irreversível | não | não | sempre | — |

---

# 11 — OBSERVABILITY MODEL

## 11.1 Camada mínima
- Log por execução: tarefa, agente, início, fim, duração, tokens, status, erro, retries.
- Métrica: taxa de sucesso, custo por domínio, bloqueios, espera.
- Tracing mínimo: handoff, tool use, falha.

## 11.2 Agent Operations Center conceitual
- O que está rodando?
- O que falhou?
- Quanto custou?
- Quais tarefas estão bloqueadas?
- Quais workflows geram valor?
- O que deve ser automatizado?

## 11.3 Maturidade atual
- Observabilidade atual: baixa.
- Diagnóstico atual: reativo e manual.
- Próximo passo: logs estruturados + dashboard mínimo.

---

# 12 — COST MODEL

## 12.1 Diretriz
- **Fast:** tarefas simples, baixa ambiguidade, saída estruturada.
- **Smart:** tarefas médias, domínio conhecido.
- **Premium:** decisões sensíveis, ambiguidade alta, risco alto.

## 12.2 Controles
- limite por domínio/tarefa
- timeout por execução
- retry com backoff limitado
- cache quando a consulta for repetitiva
- medir custo por: projeto, workflow, agente, integração

---

# 13 — AUTONOMY MODEL

| Nível | Descrição | Exemplo atual |
|---|---|---|
| 0 | Manual | decisão estratégica |
| 1 | Assistido | proposta com rascunho |
| 2 | Automação determinística | sync/merge de JSONs |
| 3 | Agente supervisionado | job hunter, founder radar |
| 4 | Agente autônomo com guardrails | follow-up com limite baixo |
| 5 | Operação autônoma | não aplicável hoje |

**Regra**
- Subir de nível só após: observabilidade, governança, recuperação.

---

# 14 — ROADMAP EVOLUTIVO

## Fase 0 — Higiene
- Inventário completo
- Responsabilidades explícitas
- Skills curadas
- Padrões de dados e nomenclatura
- Documentação mínima viável

## Fase 1 — Observabilidade
- Logs estruturados
- Métricas mínimas
- Status de jobs
- Dashboard operacional simples

## Fase 2 — Workflows
- Converter repetições comprovadas em workflows
- Formalizar retry/timeout
- Introduzir router first

## Fase 3 — Integrações
- Migrar browser-dependente para API/MCP
- Isolar credenciais
- Webhooks onde viável

## Fase 4 — Memória/Estado
- Estado transacional confiável
- Fonte única por domínio
- Versionamento mínimo

## Fase 5 — Autonomia
- Automação noturna controlada
- Aprovação por policy
- Next Best Action

## Fase 6 — Otimização
- Evals
- Custo por domínio
- Performance
- Melhoria contínua

## Fase 7 — Escala
- Apenas após necessidade real
- Mais agentes somente após contratos, estado e observabilidade

---

# 15 — BACKLOG

1. Inventariar skills, jobs, scripts, painéis, dados e integrações em fonte única.
2. Definir estados padrão para tarefas.
3. Implementar logging estruturado.
4. Mapear browser automations passíveis de API.
5. Formalizar matriz de governança.
6. Separar workflows determinísticos de agentes.
7. Criar um ATLAS mínimo operacional: agenda + prioridades.
8. Padronizar deploy e rollback.
9. Criar pipeline de avaliação mínima.
10. Implementar camada de custo por domínio.

---

# APÊNDICE — Notas de evidência local

- Cron jobs encontrados: 8.
- Jobs recorrentes relevantes: checkpoint 18h, treinamento noturno, founder radar diário, atualizações job hunter.
- Workspace contém repositórios ativos confirmados e artefatos de produção.
- Catálogo de skills contém 252 skills, com sobreposição em orquestração.
- Evidência de deploy contínuo via GitHub Pages.
- Sem estado centralizado formal para backlog de tarefas.

---

*Documento gerado para revisão. Nenhuma alteração operacional foi aplicada.*

---

# 05 — FRAMEWORK MATRIX

Avaliação focada em: **menor complexidade operacional para o nível atual de autonomia.**

| Tecnologia | Problema resolvido | Benefício | Complexidade | Custo | Lock-in | Maturidade | Nota |
|---|---|---:|---:|---:|---:|:---:|:---:|
| Cron + scripts + skills atuais | automação repetitiva simples | baixo custo, direto | baixa | baixo | baixo | alta | 7/10 |
| LangGraph | workflows multi-step, estado, ciclos | controle de fluxo e retries | média | médio | médio | média | 7/10 |
| Temporal | workflows long-running, confiabilidade | recuperação, durabilidade | alta | alto | baixo | alta | 6/10 |
| n8n | automação visual, integrações prontas | velocidade operacional | média | médio | baixo | alta | 6/10 |
| OpenAI Agents SDK | orquestração de agentes/tools | simplicidade relativa | média | médio | alto | média | 5/10 |
| CrewAI | times de agentes prontos | rápido para MVPs | média | médio | alto | média | 4/10 |
| Mastra | agentes/workflows JavaScript | ecosystem JS | média | médio | médio | média | 4/10 |
| Google ADK | integração Google/agentes | sinergia Google | média | médio | alto | baixa | 4/10 |
| LangChain | abstração de LLM/tools | ecossistema amplo | média-alta | alto | alto | alta | 5/10 |
| LlamaIndex Workflows | RAG + fluxos | conhecimento + execução | média | médio | médio | média | 5/10 |
| DSPy | prompts como programas | otimização de prompts | média-alta | médio | médio | média | 4/10 |
| Microsoft Agent Framework | enterprise governance | segurança/custódia | alta | alto | alto | média | 3/10 |
| MCP como camada padrão | descoberta/contrato de tools | reduz acoplamento | média | baixo | baixo | média-alta | 7/10 |

**Decisão provisória**
- Fase inicial: manter scripts + skills + camada de estado leve.
- Fase 2: introduzir LangGraph ou workflow determinístico pontual onde houver repetição e risco.
- n8n/Temporal só se houver volume ou duração crítica comprovada.

---

# 06 — TOOL / INTEGRATION MATRIX

| Integração | API/MCP | Webhook | OAuth | Browser | Risco bloqueio | Manutenção | Custo | Estabilidade | Prioridade |
|---|---|---|---|---|---|---|---:|---:|---:|
| GitHub Pages | sim | não | não | não | baixo | baixa | baixo | alta | P0 |
| GitHub CLI / Git | sim | não | token | não | baixo | baixa | baixo | alta | P0 |
| Google Sheets | sim | não | OAuth | não | baixo | média | baixo | alta | P0 |
| Google Drive | sim | não | OAuth | não | baixo | média | baixo | alta | P0 |
| Telegram | sim | sim | não | não | baixo | baixa | baixo | alta | P0 |
| WhatsApp | API Business | sim | sim | alto | alto | alta | médio | média | P1 |
| Meta Ads | sim | sim | OAuth | sim | médio | alta | alto | média | P1 |
| LinkedIn | não | não | OAuth | sim | alto | alta | médio | baixa | P2 |
| E-mail | IMAP/SMTP | não | senha/app | não | médio | média | baixo | média | P1 |
| Navegador geral | não | não | não | sim | alto | alta | variável | baixa | P2 |

**Regra**
- Preferir API/MCP/webhook sempre que tecnicamente viável.
- Browser automation deve ser fallback, não primeira via.

---

# 07 — AGENT ARCHITECTURE

## 7.1 Arquitetura recomendada
```
Usuário
  ↓
ATLAS (contexto, prioridades, políticas)
  ↓
HERMES (orquestração, backlog, approval, routing)
  ↓
┌─────────────────────────────────────────────────┐
│ Workflows + Agents Especializados               │
│  • Router   • Planner/Executor   • Specialist   │
│  • Skills   • Tools   • State   • Governance    │
└─────────────────────────────────────────────────┘
  ↓
Tools / Integrations / Data
```

## 7.2 Princípios
- **Router-first:** Hermes roteia para workflow quando possível; agente só quando há ambiguidade.
- **Skill-first:** capacidades reutilizáveis antes de prompts ad-hoc.
- **State-first:** sem estado não existe coordenação confiável.
- **Governance-first:** sem approval/policy não existe autonomia segura.
- **Observability-first:** sem tracing/metrícula não existe melhoria contínua.

## 7.3 Padrões preferidos
- Specialist agents para domínios delimitados.
- Planner/executor para tarefas com passos repetitivos.
- Human-in-the-loop por policy, não por falta de infra.

## 7.4 Padrões descartados para esta fase
- Multi-agent swarm sem router: adiciona custo e ruído.
- Agente-orquestrador generalista para tudo: concentra risco.
- Framework completo antes de fluxos repetitivos identificados.

---

# 08 — OPERATING MODEL

## 8.1 Responsabilidades

| Camada | Responsabilidade |
|---|---|
| Usuário | decisão estratégica, investimento, risco maior |
| ATLAS | contexto pessoal, prioridades, agenda, políticas |
| Hermes | orquestração, backlog, status, relatórios, routing |
| Workflows | processos repetitivos determinísticos |
| Agentes | execução especializada com ambiguidade |
| Skills | capacidades reutilizáveis |
| Tools | acesso a sistemas externos |
| Data | estado, histórico, conhecimento |
| Observability | tracing, custo, sucesso, falhas |
| Governance | aprovação, risco, audit log |

## 8.2 Operação diária
- Backlog único.
- Tarefa em um destes estados:
  - Inbox
  - Triaged
  - Ready
  - Running
  - Waiting
  - Blocked
  - Review
  - Done
  - Failed
  - Archived
- Relatório matinal e noturno.

---

# 09 — NIGHT SHIFT ARCHITECTURE

## 9.1 Conceito Night Shift
Depois de /PROJETEM, Hermes deve:
1. capturar backlog
2. triar elegibilidade
3. planejar ordem
4. delegar especialistas
5. executar com timeout e retry
6. validar saída
7. documentar aprendizados
8. atualizar painéis/estado
9. parar diante de bloqueios
10. reportar pela manhã

## 9.2 Regras
- Nenhuma ação reversível sem confirmação quando risco ≥ médio.
- Nenhuma publicação/envio irreversível sem aprovação.
- Nenhuma execução aberta sem timeout.
- Nenhum loop sem saída.
- Nenhuma ação artificial só para gerar atividade.

---

# 10 — GOVERNANCE MODEL

| Ação | Pode executar sozinho | Log + alerta | Precisa aprovação | Não pode |
|---|---|---|---|---|
| Enviar mensagem | mensagens operacionais low-risk | mensagens comerciais | mensagens sensíveis/irreversíveis | spam |
| Publicar | branches/previews | deploy Pages simples | deploy produção/campanha | mudança sem review |
| Excluir/alterar código | não | não | sempre | — |
| Alterar CRM | não | sim | sempre | exclusão massiva sem conferência |
| Alterar campanhas | não | sim | sim | pausar/cancelar sem motivo |
| Candidatar-se | não | não | sempre | — |
| Gastar dinheiro | não | não | sempre | — |
| Acessar dados sensíveis | não | sim | sim | vazamento/export irrestrito |
| Autenticar serviços | não | não | sempre | compartilhar credenciais |
| Tarefa externa irreversível | não | não | sempre | — |

---

# 11 — OBSERVABILITY MODEL

## 11.1 Camada mínima
- Log por execução: tarefa, agente, início, fim, duração, tokens, status, erro, retries.
- Métrica: taxa de sucesso, custo por domínio, bloqueios, espera.
- Tracing mínimo: handoff, tool use, falha.

## 11.2 Agent Operations Center conceitual
- O que está rodando?
- O que falhou?
- Quanto custou?
- Quais tarefas estão bloqueadas?
- Quais workflows geram valor?
- O que deve ser automatizado?

## 11.3 Maturidade atual
- Observabilidade atual: baixa.
- Diagnóstico atual: reativo e manual.
- Próximo passo: logs estruturados + dashboard mínimo.

---

# 12 — COST MODEL

## 12.1 Diretriz
- **Fast:** tarefas simples, baixa ambiguidade, saída estruturada.
- **Smart:** tarefas médias, domínio conhecido.
- **Premium:** decisões sensíveis, ambiguidade alta, risco alto.

## 12.2 Controles
- limite por domínio/tarefa
- timeout por execução
- retry com backoff limitado
- cache quando a consulta for repetitiva
- medir custo por: projeto, workflow, agente, integração

---

# 13 — AUTONOMY MODEL

| Nível | Descrição | Exemplo atual |
|---|---|---|
| 0 | Manual | decisão estratégica |
| 1 | Assistido | proposta com rascunho |
| 2 | Automação determinística | sync/merge de JSONs |
| 3 | Agente supervisionado | job hunter, founder radar |
| 4 | Agente autônomo com guardrails | follow-up com limite baixo |
| 5 | Operação autônoma | não aplicável hoje |

**Regra**
- Subir de nível só após: observabilidade, governança, recuperação.

---

# 14 — ROADMAP EVOLUTIVO

## Fase 0 — Higiene
- Inventário completo
- Responsabilidades explícitas
- Skills curadas
- Padrões de dados e nomenclatura
- Documentação mínima viável

## Fase 1 — Observabilidade
- Logs estruturados
- Métricas mínimas
- Status de jobs
- Dashboard operacional simples

## Fase 2 — Workflows
- Converter repetições comprovadas em workflows
- Formalizar retry/timeout
- Introduzir router first

## Fase 3 — Integrações
- Migrar browser-dependente para API/MCP
- Isolar credenciais
- Webhooks onde viável

## Fase 4 — Memória/Estado
- Estado transacional confiável
- Fonte única por domínio
- Versionamento mínimo

## Fase 5 — Autonomia
- Automação noturna controlada
- Aprovação por policy
- Next Best Action

## Fase 6 — Otimização
- Evals
- Custo por domínio
- Performance
- Melhoria contínua

## Fase 7 — Escala
- Apenas após necessidade real
- Mais agentes somente após contratos, estado e observabilidade

---

# 15 — BACKLOG

1. Inventariar skills, jobs, scripts, painéis, dados e integrações em fonte única.
2. Definir estados padrão para tarefas.
3. Implementar logging estruturado.
4. Mapear browser automations passíveis de API.
5. Formalizar matriz de governança.
6. Separar workflows determinísticos de agentes.
7. Criar um ATLAS mínimo operacional: agenda + prioridades.
8. Padronizar deploy e rollback.
9. Criar pipeline de avaliação mínima.
10. Implementar camada de custo por domínio.

---

# APÊNDICE A — MCP RESEARCH BRIEF

**CONFIRMADO**
- O ecossistema atual depende de múltiplas integrações com fronteiras frágeis.
- Existe dependência explícita de browser automation para integrações que podem ter API/MCP/webhook.

**HIPÓTESE**
- MCP pode reduzir acoplamento entre Hermes/skills/tools sem exigir reescrita completa.
- A adoção deve ser gradual por domínio, não big-bang.

**BENEFÍCIOS**
- contrato de ferramentas padronizado
- descoberta de capacidade
- isolamento de implementação

**RISCOS**
- maturidade ainda em evolução
- overhead operacional inicial
- necessidade de servidores MCP por domínio

**CUSTO**
- baixo a médio, se adotado incrementalmente

**COMPLEXIDADE**
- média na transição; baixa depois de estabelecido

**MOMENTO IDEAL**
- após Fase 1 de observabilidade, como Fase 3-4.

---

# APÊNDICE B — MEMÓRIA E ESTADO

## Opções comparadas
- filesystem + JSONs: simples, frágil para concorrência.
- SQLite: boa para estado transacional leve.
- Redis: bom para filas/cache, não para histórico completo.
- PostgreSQL: robusto, alto custo operacional agora.
- Vector DB: útil só quando RAG/embedding for necessário.
- Document store: viável, mas sem ganho claro para o volume atual.
- Event log: importante para observabilidade.

**Decisão inicial**
- Começar por SQLite/local JSON versionado + event log estruturado.
- PostgreSQL apenas se surgir necessidade transacional real.

---

# APÊNDICE C — OBSERVABILIDADE

**Camada mínima inicial**
- logs estruturados por tarefa
- métricas simples: sucesso, duração, custo, bloqueio
- dashboard HTML leve como painel operacional

**Avaliação de ferramentas**
- Langfuse/Arize Phoenix/LangSmith: boas, mas overhead alto para fase atual.
- OpenTelemetry: indicado para Fase 1-2.

---

# APÊNDICE D — EVALUATION / QA

**Arquitetura inicial**
- teste de prompt/contrato por skill
- regression test por mudança de skill
- eval pontual em workflows repetitivos
- sem investir em framework completo agora

---

# APÊNDICE E — GOVERNANÇA

**Princípio**
- Toda saída sensível passa por policy.
- Nada de envio irreversível sem aprovação.
- Nenhuma tarefa aberta sem timeout.

---

# APÊNDICE F — DECISÃO FINAL

A recomendação não é uma tecnologia.  
É um plano de evolução por fases com gates reais.

**Foco inicial**
- Estado e observabilidade.
- Contratos de dados.
- Governança e backlog.

**Só depois**
- Workflows.
- Integrações mais limpas.
- Autonomia maior.

Isso produz a menor arquitetura capaz de sustentar a próxima fase.

---

*Documento estruturado. Nenhuma alteração operacional aplicada.*
