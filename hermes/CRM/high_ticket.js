/**
 * HIGH TICKET — extension fields and scoring
 * Adiciona: micropolo, subtierHT, high_ticket_score, motivo_high_ticket,
 * estado, cidade, bairro, segmentoHT, nivel_decisao, porte_empresa, sinais_intencao
 * Compatível com CONTACTS existentes (campos novas são opcionais).
 */
const HT = (() => {
  // Carrega configuração estática (humana) do High Ticket
  const CFG_PATH = 'high_ticket_config.json';
  let cfg = null;
  try {
    cfg = JSON.parse(localStorage.getItem('ht_config_v1') || 'null');
    if (!cfg) {
      // fallback: tenta carregar via fetch apenas para inicialização opcional; não bloqueia
      console.warn('[HT] configuração não encontrada em localStorage; servidor precisa servir high_ticket_config.json');
    }
  } catch (e) {
    cfg = null;
  }

  // ===== mapeamento de cargo → nível de decisão =====
  const CARGO_NIVEL = {
    'ceo': { nivel: 'C-Level', decisao: 5, label: 'CEO / Fundador' },
    'founder': { nivel: 'C-Level', decisao: 5, label: 'Founder' },
    'co-founder': { nivel: 'C-Level', decisao: 5, label: 'Co-Founder' },
    'socio': { nivel: 'Sócio', decisao: 5, label: 'Sócio' },
    'partner': { nivel: 'Partner', decisao: 5, label: 'Partner' },
    'managing partner': { nivel: 'Partner', decisao: 5, label: 'Managing Partner' },
    'diretor': { nivel: 'Diretor', decisao: 4, label: 'Diretor' },
    'diretora': { nivel: 'Diretor', decisao: 4, label: 'Diretora' },
    'head': { nivel: 'Head', decisao: 4, label: 'Head' },
    'vp': { nivel: 'VP', decisao: 4, label: 'VP' },
    'c-level': { nivel: 'C-Level', decisao: 5, label: 'C-Level' },
    'cmo': { nivel: 'C-Level', decisao: 4, label: 'CMO' },
    'cco': { nivel: 'C-Level', decisao: 4, label: 'CCO' },
    'cro': { nivel: 'C-Level', decisao: 4, label: 'CRO' },
    'coo': { nivel: 'C-Level', decisao: 4, label: 'COO' },
    'cto': { nivel: 'C-Level', decisao: 4, label: 'CTO' },
    'cio': { nivel: 'C-Level', decisao: 4, label: 'CIO' },
    'cfo': { nivel: 'C-Level', decisao: 4, label: 'CFO' },
    'diretor comercial': { nivel: 'Diretor', decisao: 4, label: 'Diretor Comercial' },
    'diretor de marketing': { nivel: 'Diretor', decisao: 4, label: 'Diretor de Marketing' },
    'head de marketing': { nivel: 'Head', decisao: 3, label: 'Head de Marketing' },
    'head de growth': { nivel: 'Head', decidão: 3, label: 'Head de Growth' },
    'head de vendas': { nivel: 'Head', decisao: 3, label: 'Head de Vendas' },
    'head de produto': { nivel: 'Head', decisao: 3, label: 'Head de Produto' },
    'head de digital': { nivel: 'Head', decisao: 3, label: 'Head de Digital' },
    'head de tecnologia': { nivel: 'Head', decisao: 3, label: 'Head de Tecnologia' },
    'gerente geral': { nivel: 'Gerente', decisao: 3, label: 'Gerente Geral' },
    'gerente comercial': { nivel: 'Gerente', decisao: 3, label: 'Gerente Comercial' },
    'gerente de marketing': { nivel: 'Gerente', decisao: 3, label: 'Gerente de Marketing' },
    'gerente de growth': { nivel: 'Gerente', decisao: 3, label: 'Gerente de Growth' },
    'business development': { nivel: 'Gestão', decisao: 3, label: 'Business Development' },
    'investidor': { nivel: 'Investidor', decisao: 4, label: 'Investidor' },
    'private equity': { nivel: 'Investidor', decisao: 4, label: 'Private Equity' },
    'venture capital': { nivel: 'Investidor', decisao: 4, label: 'Venture Capital' },
    'family office': { nivel: 'Investidor', decisao: 4, label: 'Family Office' }
  };

  // ===== mapeamento de cargo → score (0–20) =====
  function cargoScore(cargo) {
    if (!cargo) return 0;
    const c = String(cargo).toLowerCase().trim();
    // founder / socio / partner / CEO
    if (/founder|co-?founder|sócio|partner|managing partner|ceo|presidente/.test(c)) return 20;
    if (/c-?level|cmo|cco|cro|coo|cto|cio|cfo|director|directora|head of|head de|v.?p\.?|vice-.?president/.test(c)) return 16;
    if (/gerente geral|gerente comercial|gerente de marketing|gerente de growth|business development|gerente de vendas/.test(c)) return 12;
    if (/head|gerente|coordenador|supervisor|gestor/.test(c)) return 8;
    return 4;
  }

  // ===== segmento → score (0–15) =====
  const SEGMENTO_PESO = {
    'fintech': 15, 'private-equity': 15, 'venture-capital': 15, 'investimentos': 14,
    'bancos': 14, 'seguros': 13, 'saude-premium': 13, 'medicina': 12,
    'estetica-premium': 12, 'odontologia-premium': 12, 'advocacia-empresarial': 13,
    'consultoria': 12, 'contabilidade-empresarial': 10, 'imobiliario': 12,
    'real-estate': 12, 'tecnologia': 13, 'saas': 14, 'ecommerce': 12,
    'marketing': 11, 'publicidade': 10, 'educacao-premium': 10,
    'energia': 12, 'logistica': 11, 'agronegocio': 12, 'industria': 11,
    'arquitectura': 10, 'engenharia': 10, 'construcao': 10, 'eventos-corporativos': 9,
    'servicos-b2b': 10, 'vendas-consultivas': 12, 'alto-lvt': 12,
    'luxo': 11, 'servicos-premium': 11, 'ri': 11, 'ri-tech': 13
  };
  function segmentoScore(segmento) {
    if (!segmento) return 0;
    const s = String(segmento).toLowerCase().trim();
    // verifica substring
    for (const [key, val] of Object.entries(SEGMENTO_PESO)) {
      if (s.includes(key)) return val;
    }
    return 5;
  }

  // ===== micropolo → score (0–15) =====
  function micropoloScore(codigoSubTier) {
    if (!codigoSubTier) return 0;
    const pt = cfg?.micropolo_prioridade;
    if (!pt) return 10;
    for (const nivel of pt.niveis) {
      if (nivel.micropolos.includes(codigoSubTier)) {
        if (nivel.label === 'MUITO ALTA') return 15;
        if (nivel.label === 'ALTA') return 12;
        return 8;
      }
    }
    return 5;
  }

  // ===== porte empresa → score (0–10) =====
  function porteScore(porte) {
    if (!porte) return 5;
    const p = String(porte).toLowerCase().trim();
    if (/grande|grande porte|multinacional|holding|farm.?office|fund/.test(p)) return 10;
    if (/medio|mediano|pme|sme/.test(p)) return 7;
    if (/pequeno|pj|empresa/.test(p)) return 4;
    return 5;
  }

  // ===== sinais de intenção → score (0–10) =====
  function intencaoScore(sinais) {
    if (!sinais) return 0;
    const txt = String(sinais).toLowerCase();
    let s = 0;
    if (/contrata|contratar|hiring|open.*position|vaga|recruiting/.test(txt)) s += 4;
    if (/investimento|invest|investment|capex|orcamento|budget/.test(txt)) s += 3;
    if (/crescimento|growth|escala|scale|expansao|expansion/.test(txt)) s += 2;
    if (/nova|novo|nova sede|abrir|abertura|launch|lançamento/.test(txt)) s += 1;
    return Math.min(10, s);
  }

  // ===== calcula High Ticket Score =====
  function calcularScore(c) {
    const cargo = cargoScore(c.cargo || c.subtipo || '');
    const seg = segmentoScore(c.segmentoHT || c.segmento || c.subtipo || '');
    const microp = micropoloScore(c.subtierHT || c.subtier || c.listaV2 || '');
    const porte = porteScore(c.porte_empresa || '');
    const intencao = intencaoScore(c.sinais_intencao || c.observacoes || '');
    // potencial econômico: combina cargo+segmento+porte como proxy
    const potencial = Math.min(30, Math.round((cargo * 0.5 + seg * 0.5 + porte * 0.3)));
    const total = Math.min(100, potencial + cargo + seg + microp + porte + intencao);
    return {
      total,
      detalhes: {
        potencial_economico: potencial,
        cargo_poder_decisao: cargo,
        segmento: seg,
        localizacao_micropolo: microp,
        porte_empresa: porte,
        sinais_intencao: intencao
      }
    };
  }

  // ===== classifica score =====
  function classificarScore(score) {
    if (score >= 90) return { classe: 'HT-A', label: 'PRIORIDADE MÁXIMA', min: 90, max: 100, cor: '#33c17a' };
    if (score >= 75) return { classe: 'HT-B', label: 'ALTA PRIORIDADE', min: 75, max: 89, cor: '#4f9dff' };
    if (score >= 60) return { classe: 'HT-C', label: 'POTENCIAL', min: 60, max: 74, cor: '#e8b339' };
    if (score >= 40) return { classe: 'HT-D', label: 'OBSERVAÇÃO', min: 40, max: 59, cor: '#9599a8' };
    return { classe: 'FORA', label: 'FORA DO HIGH TICKET', min: 0, max: 39, cor: '#5c6070' };
  }

  // ===== verifica se é high ticket =====
  function isHighTicket(c) {
    if (!c) return false;
    const lista = c.listaV2 || '';
    return lista === '10 - High_Ticket' || lista.includes('High_Ticket');
  }

  // ==== helpers de exibição ====
  function subTierLabel(cod) {
    if (!cod) return '';
    const st = cfg?.sub_tiers;
    if (!st) return cod;
    const found = st.find(s => s.codigo === cod);
    return found ? `${found.codigo} — ${found.micropolo}` : cod;
  }

  function micropoloInfo(cod) {
    if (!cod || !cfg) return null;
    const st = cfg.sub_tiers;
    return st.find(s => s.codigo === cod) || null;
  }

  function micropoloPortePorEstado(estado) {
    if (!cfg) return {};
    const porEstado = {};
    for (const s of cfg.sub_tiers) {
      const sigla = s.estado;
      if (!porEstado[sigla]) porEstado[sigla] = [];
      porEstado[sigla].push(s.codigo);
    }
    return porEstado;
  }

  return {
    cfg,
    CARGO_NIVEL,
    cargoScore,
    segmentoScore,
    micropoloScore,
    porteScore,
    intencaoScore,
    calcularScore,
    classificarScore,
    isHighTicket,
    subTierLabel,
    micropoloInfo,
    micropoloPortePorEstado
  };
})();
