# FLUXO OPERACIONAL — ATENDIMENTO DE LEADS EPQ

**Versão:** 1.0  
**Data:** 04/09/2026  
**Escopo:** distribuição, triagem, handoff, SLA e painel operacional  
**Modo inicial:** observação/simulação sem alterar o fluxo atual

---

## 1. PRINCÍPIO

Não distribuir por ordem de chegada.  
Distribuir por **velocidade + contexto + qualidade + conversão**.

---

## 2. EQUIPE E JANELAS

### Andressa
- Seg a sex: 09:00–17:00
- Sáb: 09:00–13:00

### Clara
- Seg a sex: 09:00–15:00
- Ter e qui: entrada às 14:00

### Ronan
- Dono do curso
- Backup fora da janela das atendentes
- Camada de escalonamento para leads quentes, complexos ou estratégicos

---

## 3. REGRAS DE DISTRIBUIÇÃO

### Segunda a sexta
- 09:00–15:00: Andressa + Clara
- 15:00–17:00: somente Andressa
- Após 17:00: Ronan

### Terça e quinta
- 09:00–14:00: somente Andressa
- 14:00–15:00: Andressa + Clara
- 15:00–17:00: somente Andressa
- Após 17:00: Ronan

### Sábado
- 09:00–13:00: Andressa
- Após 13:00: Ronan

### Fora do horário
- Sempre Ronan

---

## 4. TRIAGEM

Todo novo lead deve ser classificado considerando:
1. horário atual
2. dia da semana
3. atendentes disponíveis
4. carga atual de leads ativos
5. temperatura
6. tempo desde a entrada
7. etapa do funil
8. complexidade
9. necessidade de intervenção do Ronan

---

## 5. ROUND ROBIN INTELIGENTE

Base: distribuição alternada entre Andressa e Clara quando as duas estiverem disponíveis.

Desvio: quando houver diferença relevante de carga, direcionar para quem tem mais capacidade disponível.

Continuidade: lead que já iniciou com uma atendente não muda de responsável automaticamente.

Limites de carga:
- 0–5: normal
- 6–10: atenção
- 11+: evitar novas distribuições, salvo lead extremamente quente

---

## 6. PRIORIDADE POR TEMPERATURA

Ordem de atendimento:
1. 🔥 quente aguardando resposta
2. 🔥 quente em negociação
3. 🟠 morno aguardando follow-up
4. 🟡 frio
5. follow-up programado

Nunca deixar lead quente atrás de leads frios.

---

## 7. SLA

- 🔥 Quente: primeira resposta em até 5 minutos
- 🟠 Morno: primeira resposta em até 15 minutos
- 🟡 Frio: primeira resposta em até 30 minutos

Se o SLA estiver próximo de estourar:
1. alertar a atendente
2. escalar para outra atendente disponível
3. se não houver atendente, escalar para Ronan

---

## 8. HANDOFF

15 minutos antes do fim do expediente de cada atendente, gerar pré-handoff com:
- nome
- telefone
- temperatura
- produto/interesse
- última mensagem
- objeção principal
- o que já foi oferecido
- próxima ação
- horário recomendado para follow-up
- status da negociação

Transferir somente os necessários. Não transferir toda a carteira.

---

## 9. ESCALONAMENTO PARA RONAN

Ronan deve receber:
- leads muito quentes
- alto potencial financeiro
- negociações travadas
- objeções difíceis
- reclamações
- solicitações fora do padrão
- leads que pedem para falar com o dono
- leads de parceiros
- alta intenção de matrícula
- situações em que intervenção pessoal aumenta conversão

---

## 10. PAINEL OPERACIONAL

O painel deve mostrar:

### Quem atende agora
- Andressa: horário, status, leads ativos, leads aguardando
- Clara: horário, status, leads ativos, leads aguardando
- Ronan: status, leads escalados

### O que precisa ser feito agora
- leads quentes aguardando resposta
- leads mornos aguardando follow-up
- leads próximos de estourar SLA
- leads que precisam de handoff
- leads aguardando Ronan

---

## 11. MÉTRICAS

Monitorar diariamente:
- leads recebidos
- leads respondidos
- tempo médio de primeira resposta
- SLA cumprido
- leads por atendente
- leads ativos
- leads sem resposta
- leads transferidos
- leads escalados para Ronan
- matrículas por atendente
- taxa de conversão por atendente
- conversão por horário
- conversão por origem
- motivos de perda

---

## 12. IMPLEMENTAÇÃO

1. manter o fluxo atual funcionando
2. implementar em modo observação/simulação
3. comparar resultado com o fluxo atual
4. somente depois ativar distribuição automática

Objetivo final:
> "Quem deve atender este lead agora, por quê e qual é a próxima ação?"
