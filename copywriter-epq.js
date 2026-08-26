/*
  EPQ — Copywriter Estratégico
  Briefing completo por pauta, alinhado ao painel de conteúdo.
*/
const EPQ_COPYWRITER = (() => {
  const POSITIONING = {
    dna: 'Você não precisa estudar MAIS. Precisa estudar MELHOR.',
    territorio: 'Erro Comum de Quem Estuda para Concurso',
    pilares: ['Estude Melhor', 'Erros Comuns', 'Mito x Verdade', 'Prova Social', 'Editais e Oportunidades', 'Autoridade e Método', 'Bastidores e Humanização', 'Comunidade'],
    voz: {
      tom: 'direta, inteligente, provocativa, prática, humana, estratégica, fácil de entender',
      evitar: ['linguagem corporativa', 'frases motivacionais vazias', 'excesso de emojis', 'exageros', 'promessas irreais', 'clickbait sem entrega', 'textos genéricos de “coach”']
    }
  };

  const FUNIL = {
    topo: { estagio: 'Topo', objetivo: 'Atração', comportamento: 'Descoberta do problema e identificação' },
    meio: { estagio: 'Meio', objetivo: 'Consideração', comportamento: 'Aprofundamento da dor e busca de solução' },
    fundo: { estagio: 'Fundo', objetivo: 'Conversão', comportamento: 'Decisão e ação' }
  };

  const FORMATO_CANVAS = {
    'Post': { formato: 'Post fixo', melhorUso: 'Educação leve, regras práticas, prompts de engajamento' },
    'Story': { formato: 'Story interativo', melhorUso: 'Enquetes, quizzes, respostas rápidas, CTA direto' },
    'Carrossel': { formato: 'Carrossel educativo', melhorUso: 'Passo a passo, framework, lista prática' },
    'Reel': { formato: 'Reel rápido', melhorUso: 'Hooks visuais, padrão, transformação, bastidores' },
    'Vídeo': { formato: 'Vídeo longo/médio', melhorUso: 'Método, explicação, autoridade, storytelling' },
    'Campanha': { formato: 'Campanha multiplataforma', melhorUso: 'Narrativa cruzada EPQ + Ronan' },
    'Prova Social': { formato: 'Prova social', melhorUso: 'Depoimento real, números, transformação' }
  };

  const TERRITORIOS = {
    'Estude Melhor': { insight: 'O problema não é falta de tempo, é falta de sistema.', dor: 'Estuda muito e não vê resultado.', desejo: 'Passar estudando menos, com método.' },
    'Erros Comuns': { insight: 'O erro repetido não é falta de esforço, é falta de correção.', dor: 'Repete o mesmo erro em toda prova.', desejo: 'Parar de errar o que já estudou.' },
    'Mito x Verdade': { insight: 'Mitos sobre estudo vendem esperança, não resultados.', dor: 'Acredita em técnicas que não funcionam.', desejo: 'Usar método com base real.' },
    'Prova Social': { insight: 'Resultado real conversa mais que promessa bonita.', dor: 'Dificuldade de acreditar em métodos genéricos.', desejo: 'Ver alguém “igual” passando.' },
    'Editais e Oportunidades': { insight: 'Prazo não espera ninguém. Quem organiza primeiro, ganha.', dor: 'Perde prazos por desorganização.', desejo: 'Ficar por dentro sem perder tempo.' },
    'Autoridade e Método': { insight: 'Experiência na correção vale mais que teoria de motivação.', dor: 'Falta de clareza sobre o que realmente cai.', desejo: 'Aprender com quem já viu milhares de provas.' },
    'Bastidores e Humanização': { insight: 'A confiança começa quando o professor mostra como pensa.', dor: 'Falta de conexão com a marca/método.', desejo: 'Ver que existe alguém real por trás do conteúdo.' },
    'Comunidade': { insight: 'Estudar junto reduz a desistência.', dor: 'Estuda sozinho e desanima.', desejo: 'Fazer parte de algo maior.' }
  };

  function detectarFunil(objetivo, tipo, pilar) {
    const o = (objetivo || '').toLowerCase();
    const t = (tipo || '').toLowerCase();
    const p = pilar || '';

    if (/conversão|comercial|edital|oportunidade|prazo|prazo/.test(o)) return 'fundo';
    if (/educação|engajamento|alcance|autoridade|relacionamento/.test(o)) {
      if (t === 'campanha' || t === 'prova social') return 'fundo';
      if (p.includes('Erros Comuns') || p.includes('Mito x Verdade')) return 'meio';
      return 'meio';
    }
    return 'meio';
  }

  function gerarObjetivoEstrategico(pauta) {
    const mapa = {
      'Educação': 'Ensinar um comportamento de estudo acionável e lembrar o aluno do método EPQ.',
      'Alcance': 'Amplificar alcance com um insight claro e facilmente compartilhável.',
      'Autoridade': 'Posicionar o professor como referência prática e diferenciada.',
      'Engajamento': 'Estimular comentários, saves e compartilhamentos com interação simples.',
      'Conversão': 'Conduzir o público para o próximo passo com CTA claro e coerente.',
      'Relacionamento': 'Aproximar a marca do público por meio de humanização e confiança.'
    };
    return mapa[(pauta.Objetivo || '').trim()] || 'Gerar conteúdo relevante e estrategicamente alinhado ao EPQ.';
  }

  function gerarDorDesejo(pauta) {
    const ref = TERRITORIOS[pauta.Pilar] || TERRITORIOS['Estude Melhor'];
    return { dor: ref.dor, desejo: ref.desejo, insight: ref.insight };
  }

  function gerarAngulo(pauta) {
    const tema = (pauta['Tema / Campanha'] || '').trim();
    const formato = pauta.Formato || '';
    const base = tema.toLowerCase();
    let angulo = 'use a regra contrária ao erro comum';

    if (base.includes('edital') || base.includes('pmrj') || base.includes('ses') || base.includes('guarda') || base.includes('oportunidade')) {
      angulo = 'prazo como gatilho de decisão';
    } else if (formato === 'Carrossel' || base.includes('passo') || base.includes('como') || base.includes('rotina') || base.includes('planejar')) {
      angulo = 'passo a passo executável sem dramatização';
    } else if (formato === 'Reel' || formato === 'Vídeo') {
      angulo = 'opinião direta + exemplo visual';
    } else if (formato === 'Prova Social' || base.includes('depoimento') || base.includes('aprovado')) {
      angulo = 'transformação real antes da explicação';
    } else if (base.includes('mito') || base.includes('verdade')) {
      angulo = 'mito que parece verdade para quem está desesperado';
    } else if (base.includes('erro') || base.includes('repetir') || base.includes('corrigir')) {
      angulo = 'erro invisível que todo repetidor de questão comete';
    } else if (base.includes('motivação') || base.includes('consistência') || base.includes('desistir')) {
      angulo = 'o que sustenta a longo prazo não é motivação, é sistema';
    } else if (base.includes('bastidor') || base.includes('sala') || base.includes('live') || base.includes('humano')) {
      angulo = 'preparo real, sem filtro';
    }

    return angulo;
  }

  function gerarConceito(pauta) {
    const angulo = gerarAngulo(pauta);
    const formato = pauta.Formato || 'conteúdo';
    const perfil = pauta.Perfil || 'EPQ';
    const tema = pauta['Tema / Campanha'] || '';
    return `Em ${formato}, o conceito gira em torno de: ${angulo}. ${perfil} entrega clareza prática sobre "${tema}", evitando motiv Easy e reforçando o posicionamento EPQ: estudar melhor, não estudar mais.`;
  }

  function limparTexto(texto) {
    return (texto || '').replace(/\s+/g, ' ').trim();
  }

  function gerarHeadlines(pauta) {
    const tema = limparTexto(pauta['Tema / Campanha']);
    const headlineOriginal = limparTexto(pauta.Headline);
    const formato = pauta.Formato || '';
    const pilar = pauta.Pilar || '';

    const porFormato = {
      'Carrossel': ['O que ninguém diz sobre repetir questões.', 'Se você só faz questão, está perdendo isso.', 'A diferença está na correção, não na quantidade.'],
      'Reel': ['Repetir questão não é estudar.', 'O erro invisível no estudo por questões.', 'Você está estudando mais ou apenas repetindo?'],
      'Vídeo': ['Antes de aumentar a carga, ajuste o método.', 'O padrão que vejo toda semana na correção.', 'Estudar mais não resolve repetir o mesmo erro.'],
      'Post': ['Um ajuste simples no método.', 'Estude melhor em vez de estudar mais.', 'Pare de repetir erros sem perceber.'],
      'Story': ['Responda rápido: você só faz questões?', 'Você está em qual erro?', 'Monte sua semana de estudos agora.'],
      'Campanha': ['EPQ: método. Ronan: explicação. Você: resultado.', 'Não é sorte. É padrão que você pode repetir.', 'Estude melhor em vez de estudar mais.'],
      'Prova Social': ['Do método para a aprovação.', 'Resultados reais em editais de segurança.', 'Ele mudou de estratégia e passou.']
    };

    const alternativas = porFormato[formato] || porFormato['Post'];
    const principal = headlineOriginal || alternativas[0];
    return { principal, alternativas };
  }

  function gerarCopyCarrossel(pauta) {
    const tema = limparTexto(pauta['Tema / Campanha']);
    const headline = limparTexto(pauta.Headline) || 'Estude melhor';
    const cta = limparTexto(pauta.CTA) || 'Aplique isso hoje.';

    return {
      slide01: `Hook direto: "${headline}"`,
      slide02: `Desenvolvimento: explique por que o erro acontece sem drama, com linguagem simples.`,
      slide03: `Desenvolvimento: mostre um exemplo real no estudo por questões ou na revisão.`,
      slide04: 'Virada: o insight que muda a forma de estudar.',
      slide05: `CTA: ${cta || 'Salve para revisar depois.'}`
    };
  }

  function gerarCopyCriativo(pauta) {
    const formato = pauta.Formato || '';
    if (formato.toLowerCase().includes('carrossel')) return gerarCopyCarrossel(pauta);
    return { texto: limparTexto(pauta.Headline) || 'Texto do criativo.' };
  }

  function gerarDirecaoCriativa(pauta) {
    const perfil = pauta.Perfil || 'EPQ';
    const formato = pauta.Formato || '';
    const tema = limparTexto(pauta['Tema / Campanha']);
    const cores = perfil === 'EPQ' ? 'azul EPQ + cinza claro' : 'preto Ronan + azul de destaque';
    const atmosfera = formato === 'Vídeo' || formato === 'Reel' ? 'dinâmica, natural, próxima' : 'limpa, organizada, analítica';

    return `Composição: hierarquia clara com headline acima, texto legível em 3–4 linhas e elemento visual de apoio sem poluir.\nDestaque visual: cor de destaque no dado principal ou insight.\nImagem sugerida: ${perfil === 'EPQ' ? 'estudante em contexto real de estudo' : 'professor em sala/aula'}.\nAtmosfera: ${atmosfera}.\nRelação texto/imagem: texto explica, imagem exemplifica.`;
  }

  function gerarLegenda(pauta) {
    const tema = limparTexto(pauta['Tema / Campanha']);
    const headline = limparTexto(pauta.Headline);
    const cta = limparTexto(pauta.CTA);
    const legendaOriginal = limparTexto(pauta.Legenda);

    const hook = headline || `A maioria estuda para concurso no modo errado.`;
    let corpo = legendaOriginal || `Em "${tema}" o detalhe que separa quem avança de quem estagna não é repetir mais questões: é corrigir o erro no momento certo.`;

    if (cta) {
      corpo += `\n\n${cta}`;
    }
    return `${hook}\n\n${corpo}`;
  }

  function gerarTags(pauta) {
    const tags = limparTexto(pauta['Tags / Hashtags']);
    const tema = limparTexto(pauta['Tema / Campanha']);
    const palavras = tema
      .toLowerCase()
      .split(/[\s,-]+/)
      .filter(Boolean)
      .slice(0, 8);

    const hashtags = tags ? tags.split(' ').filter(Boolean) : ['#EPQ', '#Estudo', '#Concursos'];
    return {
      hashtags: hashtags.join(' '),
      palavrasChave: [...new Set([...palavras, 'estudo', 'concurso', 'método'])].slice(0, 8).join(', '),
      relacionados: [...new Set([...palavras, 'questões', 'revisão', 'edital', 'aprovado'])].slice(0, 8).join(', ')
    };
  }

  function gerarVariacoes(pauta) {
    const tema = limparTexto(pauta['Tema / Campanha']);
    return {
      headlines: [
        `Se você só faz questões, está perdendo isso.`,
        `O ajuste que muda qualquer rotina de estudos.`,
        `Estudar mais não resolve repetir o mesmo erro.`
      ],
      hooks: [
        `A maioria repete questões sem corrigir o padrão do erro.`,
        `Você já percebeu que sempre erra o mesmo ponto?`
      ],
      ctas: [
        limparTexto(pauta.CTA) || 'Salve para aplicar hoje.',
        'Qual o seu maior erro de estudo? Comenta.'
      ],
      conceitoAlternativo: `Versão reversa: mostrar o erro primeiro, depois a correção simples, ideal para Reel/Story quando a pauta permitir humor/surpresa.`
    };
  }

  function gerarBriefing(pauta) {
    if (!pauta || !pauta.ID) {
      return { erro: 'Pauta inválida para briefing.' };
    }

    const tema = limparTexto(pauta['Tema / Campanha']);
    const objetivoEstrategico = gerarObjetivoEstrategico(pauta);
    const publico = 'Estudantes de concursos em preparação ativa, com foco em segurança pública, PMERJ, SES, Guarda Municipal e escolas militares.';
    const funil = detectarFunil(pauta.Objetivo, pauta['Tipo de distribuição'], pauta.Pilar);
    const funilInfo = FUNIL[funil] || FUNIL.meio;
    const dorDesejo = gerarDorDesejo(pauta);
    const angulo = gerarAngulo(pauta);
    const conceito = gerarConceito(pauta);
    const headlines = gerarHeadlines(pauta);
    const copy = gerarCopyCriativo(pauta);
    const direcao = gerarDirecaoCriativa(pauta);
    const legenda = gerarLegenda(pauta);
    const tags = gerarTags(pauta);
    const variacoes = gerarVariacoes(pauta);
    const formatoInfo = FORMATO_CANVAS[pauta.Formato] || FORMATO_CANVAS['Post'];

    return {
      id: pauta.ID,
      pauta,
      briefing: {
        '01. CONCEITO': {
          objetivo: objetivoEstrategico,
          publico,
          funil: `${funilInfo.estagio} — ${funilInfo.objetivo}`,
          dorDesejo: `${dorDesejo.dor}\nDesejo: ${dorDesejo.desejo}`,
          insight: dorDesejo.insight,
          angulo,
          conceitoCriativo: conceito
        },
        '02. HEADLINE': {
          principal: headlines.principal,
          alternativas: headlines.alternativas
        },
        '03. COPY DO CRIATIVO': copy,
        '04. DIREÇÃO CRIATIVA': {
          direcao,
          formato: formatoInfo.formato,
          melhorUso: formatoInfo.melhorUso
        },
        '05. LEGENDA': legenda,
        '06. TAGS': tags,
        '07. VARIAÇÕES': variacoes,
        dna: POSITIONING.dna,
        territorio: POSITIONING.territorio,
        tomDeVoz: POSITIONING.voz.tom,
        evitar: POSITIONING.voz.evitar.join(', ')
      }
    };
  }

  return { gerarBriefing, POSITIONING, FUNIL };
})();
