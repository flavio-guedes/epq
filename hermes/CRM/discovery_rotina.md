# Discovery Rotina — High Ticket Micropolos
# Executada pelo Hermes quando ativada (manual ou periódica via cron)
# Saída: novo sub-tier registrado em high_ticket_config.json (quando validado)

## Gatilhos de execução
- Manual: `hermes run discovery-ht` ou chamada direta
- Periódica: a cada 30 dias (ou quando o usuário solicitar)
- Trigger externo: когда há notícia de novo polo corporate (ex.: edifício aberto, cluster identificado)

## Fonte de dados permitidas
- LinkedIn (busca pública, sem login)
- Google Maps (placemark de edifícios corporativos)
- Notícias públicas (Jornal Valor, exame, etc.)
- Sites institucionais de empresas conhecidas
- Dados abertos (Receita Federal via abrir, se disponível)
- Wikipedia / dicionários de bairros
- Outras fontes públicas SEM login/credencial

## Processo de validação de micropolo (antes de criar sub-tier)
Para cada região candidata, responder SIM a TODOS:

1. Há pelo menos 5 grandes empresas / multinacionais / fundos / family offices com sede ou escritório relevante no bairro/eixo?
2. Há concentração de cargos C-Level / Founder / Partner / Diretor na região? (evidência pública)
3. O perfil econômico justifica prospeção B2B de alto ticket?
4. Existe massa crítica de decisores (mínimo ~20 profissionais relevantes identificáveis publicamente)?
5. O bairro/eixo não é apenas "nobre" sem concentração comercial real?

Se qualquer um for NÃO → não criar sub-tier. Registrar como "observação" em vez disso.

## Saída do processo
Quando válido, criar entrada em high_ticket_config.json:

{
  "codigo": "HT-XX-NN",
  "micropolo": "Nome do bairro/eixo",
  "cidade": "Cidade",
  "estado": "UF",
  "perfil": "...",
  "setores": ["setor1", "setor2"],
  "__descoberto_em": "YYYY-MM-DD",
  "__fonte": "descrição da fonte",
  "__validado_por": "procedimento de descoberta",
  "__observacoes": "..."
}

IMPORTANTE: nunca inventar empresas, cargos ou leads usando esta rotina.
A descoberta diz respeito ao micropolo e ao setor — os leads individuais
só são criados quando há dado público concreto (LinkedIn público, site oficial,
contato público validado). Dados fictícios para preencher painel são proibidos
exceto quando marcados explicitamente como DEMO.

## Exemplos de evidência aceitável
- Lista de 10 empresas com endereço no bairro X, extraída de Google Maps / site próprias
- Menção em matéria de jornal valorando o polo
- Lista pública de participantes de evento corporativo na região
- Perfil público de Coworking/Hub com lista de empresas residentes

## Limite de execução
- Tempo máximo: 45 minutos por rodada de descoberta
- Foco Geográfico: iniciar por SP, RJ, MG; depois expandir para os outros estados
- Não reputar micropolos já mapeados sem novo dado relevante

## Próximos micropolos prioritários para pesquisa (já mapeados, aguardando validação ou expansão)
- São Paulo: Moema, Ipiranga, Ana Rosa, Santana
- Rio: Tijuca, São Cristóvão, Niterói (Pça. Sulawesi)
- Minas: Contagem, Betim, Santa Rita do Sapucaí
- PR: Colombo, São José dos Pinhais
- RS: Cidade Alegre, Partenon
- SC: Labjor/UFSC area, Hercílio Luz
- PE: Casa Forte, Imbiribeira
- BA: Jequiá, Ondina, Barra
- CE: Meireles, Edson Queiroz
- DF: Asa Norte, Setor de Castelão
- GO: Goiânia Velho, Vila Nova
- SP exterior: Santos (corporate portuário), Guaratinguetá

## Governança
- Toda entrada tem data de descoberta e fonte
- Nada é apagado; desabilitado com "__desabilitado": true apenas se há erro grave
- Revisar entradas antigos a cada 6 meses
