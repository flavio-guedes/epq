// EPQ · CONCURSO RADAR — Motor de scoring e regras de recomendação

export const WEIGHTS = {
  proximidadeEdital: 18,
  inscricoesAbertas: 20,
  vagas: 10,
  relevanciaCargo: 12,
  historicoDemanda: 10,
  aderenciaEPQ: 12,
  concorrencia: 6,
  ticketPotencial: 6,
  recorrencia: 5,
  publico: 5,
  facilidadeTurma: 6,
  materialQuestoes: 5,
  disciplinasExistentes: 6,
  forcaMovimentacao: 9
};

export const MAX_SCORE = 100;

export function scoreConcurso(c) {
  // Heurísticas baseadas em faixas e sinais de estágio do concurso
  const s = {
    proximidadeEdital: stageProximity(c),
    inscricoesAbertas: enrollmentSignal(c),
    vagas: vacanciesScore(c),
    relevanciaCargo: relevanceScore(c),
    historicoDemanda: demandScore(c),
    aderenciaEPQ: c.aderenciaEPQ ?? 0,
    concorrencia: competitionScore(c),
    ticketPotencial: ticketScore(c),
    recorrencia: recurrenceScore(c),
    publico: audienceScore(c),
    facilidadeTurma: feasibilityScore(c),
    materialQuestoes: materialScore(c),
    disciplinasExistentes: disciplinesScore(c),
    forcaMovimentacao: momentumScore(c)
  };
  const total = Object.keys(WEIGHTS).reduce((acc, k) => acc + ((s[k] ?? 0) * (WEIGHTS[k] ?? 0)), 0) / 100;
  const clamped = Math.max(0, Math.min(MAX_SCORE, Math.round(total)));
  return { raw: s, total: clamped };
}

function stageProximity(c) {
  const map = { 'ABERTO': 100, 'IMINENTE': 85, 'EM ESTUDO': 55, 'DISTANTE': 25, 'ENCERRADO': 0 };
  return map[c.status] ?? 10;
}
function enrollmentSignal(c) {
  return c.status === 'ABERTO' ? 100 : c.status === 'IMINENTE' ? 70 : 20;
}
function vacanciesScore(c) {
  const v = Number(c.vagasEstimadas || 0);
  if (v >= 1500) return 90;
  if (v >= 800) return 75;
  if (v >= 300) return 60;
  if (v >= 100) return 45;
  return 30;
}
function relevanceScore(c) {
  const high = ['segurança pública','tribunais','educação','saúde','área militar','área administrativa'];
  return high.includes(c.area) ? 85 : 55;
}
function demandScore(c) {
  const m = String(c.historicoDemanda || '').toLowerCase();
  if (m.includes('muito alta') || m.includes('alta')) return 90;
  if (m.includes('média')) return 60;
  return 40;
}
function competitionScore(c) {
  const m = String(c.concorrenciaCursos || '').toLowerCase();
  if (m.includes('alta')) return 50;
  if (m.includes('média')) return 70;
  return 85;
}
function ticketScore(c) {
  const m = String(c.potencialTicket || '').toLowerCase();
  if (m.includes('alto')) return 85;
  if (m.includes('médio')) return 60;
  return 40;
}
function recurrenceScore(c) {
  const m = String(c.historicoDemanda || '').toLowerCase();
  if (m.includes('recorrente') || m.includes('contínua')) return 85;
  if (m.includes('alta')) return 70;
  return 45;
}
function audienceScore(c) {
  const m = String(c.publicoPotencial || '').toLowerCase();
  if (m.includes('muito alto')) return 95;
  if (m.includes('alto')) return 85;
  if (m.includes('médio')) return 65;
  return 45;
}
function feasibilityScore(c) {
  let s = 50;
  if (c.disciplinas && c.disciplinas.length) s += 15;
  if (c.existeMaterial) s += 15;
  if (c.existeTurma) s += 10;
  return Math.min(95, s);
}
function materialScore(c) {
  return c.existeMaterial ? 75 : 40;
}
function disciplinesScore(c) {
  const core = ['Português','Matemática','Direito Constitucional','Direito Administrativo','Legislação'];
  const set = new Set((c.disciplinas || []).map(x => x.toLowerCase()));
  const hit = core.filter(x => set.has(x.toLowerCase())).length;
  return 40 + hit * 12;
}
function momentumScore(c) {
  const base = Number(c.forcaMovimentacao || 0);
  const accel = c.aceleração ? 15 : 0;
  return Math.min(100, base + accel);
}

export function recommendation(c) {
  const { total } = scoreConcurso(c);
  if (c.status === 'ABERTO' && total >= 65) return 'ABRIR';
  if (c.status === 'IMINENTE' && total >= 78) return 'PRÉ-LANÇAR';
  if ((c.status === 'IMINENTE' || c.status === 'EM ESTUDO') && total >= 55) return 'CAPTAR';
  if (c.status === 'EM ESTUDO' && total >= 40) return 'MONITORAR';
  return 'NÃO ATACAR';
}

export function detectAcceleration(items) {
  const now = new Date();
  return items
    .map(c => {
      const hist = [];
      // Placeholder: in production, inject history per item
      const count = Number(c.recenciaDias || 30);
      const vel = count <= 14 ? 'alta' : count <= 35 ? 'média' : 'baixa';
      const accel = c.aceleração || vel === 'alta';
      return { ...c, accel, vel, reason: c.aceleraçãoRazao || `Movimentação recente em ${count} dias` };
    })
    .filter(c => c.accel);
}
