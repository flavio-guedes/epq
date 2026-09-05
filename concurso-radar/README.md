# EPQ · Concurso Radar

Sistema de inteligência de mercado para identificar oportunidades de concursos públicos e recomendar ações comerciais e pedagógicas para o EPQ.

Tagline: **"O próximo concurso começa antes do edital."**

---

## 1. Estrutura do projeto

```
epq-concurso-radar/
├── index.html          # Dashboard principal
├── radar-data.js       # Dados estruturados de concursos, histórico e alertas
├── radar-scoring.js    # Motor de scoring e regras de recomendação
└── README.md           # Esta documentação
```

### Arquivos

- **index.html**: painel único, responsivo, com KPIs, ação agora, alertas, pipeline, ranking, motor de turmas, matriz, histórico e modal de ficha.
- **radar-data.js**: dados de exemplo, constantes de classificação, status, scores e configuração.
- **radar-scoring.js**: heurísticas de scoring, detecção de aceleração e função de recomendação.

---

## 2. Como usar

1. Abra `index.html` no navegador.
2. O dashboard usa dados de exemplo embutidos em `radar-data.js`.
3. Para produção:
   - substitua `concursos`, `historico` e `alertas` por dados reais
   - injete URLs, fontes e evidências em cada registro
   - ative automação via script/Cron job consumindo fontes oficiais/especializadas

---

## 3. Status e classificação

Status possíveis:
- `ABERTO`
- `IMINENTE`
- `EM ESTUDO`
- `DISTANTE`
- `ENCERRADO`

Pipeline visual:
`MOVIMENTAÇÃO → AUTORIZADO → BANCA → EDITAL → INSCRIÇÕES → PROVA → ENCERRADO`

---

## 4. Scoring

Score EPQ = 0 a 100.

Componentes principais (radar-scoring.js):
- proximidade do edital
- inscrições abertas
- vagas estimadas
- relevância do cargo
- histórico de demanda
- aderência EPQ
- concorrência de cursos
- potencial de ticket
- recorrência
- público potencial
- facilidade de criar turma
- material disponível
- disciplinas existentes
- força da movimentação

Bandas:
- 80–100: 🔥 PRIORIDADE MÁXIMA
- 60–79: 🟢 OPORTUNIDADE
- 40–59: 🟡 MONITORAR
- 0–39: ⚪ BAIXA PRIORIDADE

---

## 5. Recomendações

Regras em `radar-scoring.js`:
- `ABRIR`: status aberto e score >= 65
- `PRÉ-LANÇAR`: iminente e score >= 78
- `CAPTAR LEADS`: iminente/em estudo e score >= 55
- `MONITORAR`: em estudo e score >= 40
- `NÃO ATACAR`: demais casos

---

## 6. Alertas

Tipos padrão:
- 🚨 NOVO CONCURSO RELEVANTE
- 🔥 EDITAL PUBLICADO
- 🟠 BANCA DEFINIDA
- 🚀 CONCURSO ACELERANDO
- ⏰ INSCRIÇÕES ABERTAS
- ⚠️ PRAZO DE INSCRIÇÃO PRÓXIMO DO FIM
- 🎯 OPORTUNIDADE DE NOVA TURMA
- 📉 OPORTUNIDADE PERDIDA

---

## 7. Confiabilidade

Todo registro crítico deve exibir:
- Fonte
- Data da verificação
- Nível de confiança: `CONFIRMADO / INDÍCIO / PREVISÃO / RUMOR`

Nunca transformar rumor em confirmação.

---

## 8. Integrações futuras (preparadas)

- CRM EPQ (leads, atendimento, matrículas)
- WhatsApp, Meta Ads, Instagram
- Google Trends
- Vendas, turmas e faturamento
- Histórico comercial

Para ativar:
- alimentar `radar-data.js` via API/ETL
- conectar pipeline de atualização automática
- usar o ranking diário para campanhas

---

## 9. Privacidade e governança

- Não simular dados sensíveis reais em produção.
- Validar fontes oficiais antes de publicar alertas.
- Registrar acertos/erros para aprendizado contínuo.
