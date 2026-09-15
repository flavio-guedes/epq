#!/usr/bin/env python3
"""Gera o dataset enriquecido dos leads EPQ (dados da aba Leads da planilha).

Saídas:
  ../data/leads_epq_2026-09-15.json          — dados completos + análise
  ../data/leads_epq_followup_plan.md         — plano operacional legível
  ../data/leads_epq_dispatch_queue.json      — fila de disparo WhatsApp (P0/P1)
"""
import json, re, os, datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

# (id, data, nome, whatsapp, origem, turma, etapa, responsavel, ultima, objeção/obs)
ROWS = [
 (1,"2026-09-10","Flávio Luiz dos Santos","(21) 99971-9474","Meta Ads","GCM Maricá combo","Qualificado","Andressa","2026-09-10",
  "Lead quente GCM combo. Pediu horário e valor. Recebeu tabela combo R$1.945,50 à vista / 5x R$389,50 Pix. Confirmou nome completo para aulão 12/09. Objeção: não pode ir ao aulão presencial porque precisa levar filho ao concurso ESPCEX na Tijuca no mesmo dia. Team ofereceu aula experimental online ou outro dia. Tom de objeção real mas negociável."),
 (2,"2026-09-11","Ramon Cerqueira","(21) 96660-4178","Meta Ads","GCM Maricá","Negociação","Andressa","2026-09-11",
  "Lead quente GCM Maricá. Recebeu oferta turma noite (19h-22h, 2a-6a, 5 meses) + convite aula experimental. Valor: R$300/mês Pix ou R$330 cartão. Lead: 'vou resolver uma situação referente ao trabalho' e 'o valor tem que ser pago assim que faz a matrícula?'. Confirmou 'GCM de Maricá, que vai abrir agora'. Pediu prazo: 'Resolvendo já entro em contato'. LEAD QUENTE - esperando resolução do trabalho para fechar."),
 (3,"2026-09-09","Brenda","(21) 96997-7512","Meta Ads","INSS","Proposta Enviada","Andressa","2026-09-09",
  "Perguntou localização da unidade e valor da turma INSS. Recebeu endereço + tabela completa de valores. Parou após receber os valores - sem confirmar visita ou aula experimental. Único lead de concurso não policial/militar."),
 (4,"2026-09-09","Guilherme","(21) 97431-6907","Meta Ads","GCM Maricá / São Gonçalo","Proposta Enviada","Andressa","2026-09-09",
  "Perguntou dias e preços do combo GCM. Recebeu tabela completa (R$1.945,50 à vista ≈ R$332/mês ou 5x R$389,50 Pix). Parou sem confirmar presença no aulão de 12/09."),
 (5,"2026-09-09","Lead PRF (sem nome)","(21) 98055-5629","Meta Ads","PRF Agente Administrativo","Proposta Enviada","Clara","2026-09-09",
  "Perguntou inscrição, requisitos, edital e valores do concurso PRF. Recebeu mensagem genérica de boas-vindas - SEM responder às 4 perguntas reais. Conversa parou aqui. URGENTE: responder às 4 perguntas concretas (inscrição, requisitos, edital vigente, valores) + oferecer aula experimental."),
 (6,"2026-09-09","Andressa (sem nome) - PMERJ","(21) 98294-6742","Meta Ads","PMERJ (digitado PMERG)","Contato Feito","Andressa","2026-09-09",
  "Equipe respondeu com erro de digitação 'PMERG' em vez de 'PMERJ'. Lead disse 'Sim' mas sem informar nome. Parou - parece que nem percebeu a conversa estava ativa. Retomar com nome correto PMERJ, sem erro de digitação. Perguntar turno preferido."),
 (7,"2026-09-09","Douglas","(21) 99043-9709 (1)","Meta Ads","GCM Maricá","Proposta Enviada","Andressa","2026-09-10",
  "Perguntou 'Esse concurso é real mesmo?'. Equipe confirmou. Continuou em 10/09 sem resposta do lead. Dúvida de legitimidade do concurso."),
 (8,"2026-09-09","Marcelo","(21) 99228-3360 (1)","Meta Ads","GCM Queimados","Proposta Enviada","Clara","2026-09-09",
  "Perguntou preparatório GCM Queimados. Recebeu detalhes das turmas de manhã, noite e sábado. Parou sem confirmar qual turno prefere."),
 (9,"2026-09-09","Andressa (sem nome) - GCM noturno","(21) 99812-7074","Meta Ads","GCM Maricá noturno","Proposta Enviada","Andressa","2026-09-09",
  "Confirmou GCM noturno. Recebeu detalhes da turma combo (19h-22h, 2a-6a, 5 meses) + convite para aulão de 12/09. Parou sem confirmar presença no aulão."),
 (10,"2026-09-10","Elen PMERJ","(21) 99043-9709 (2)","Meta Ads","PMERJ noturno semanal","Proposta Enviada","Andressa","2026-09-10",
  "Perguntou informações sobre PMERJ noturno semanal. Recebeu valores (5x R$300 Pix / R$330 cartão + material R$50 + camisa R$75). Oferecido aulão de 12/09. Lead disse 'Entendi' e afirmou ser de Nilópolis. Parou após receber valores. Lead em período de repouso médico."),
 (11,"2026-09-10","Mateus PMERJ","n/a","Meta Ads","PMERJ / PC / PRF / PF / Secretarias","Contato Feito","Clara","2026-09-10",
  "Pediu informações de vários concursos militares. Recebeu oferta GCM + convite para aulão de 12/09. Lead não confirmou. Enviou imagem do aulão e convidou para garantir vaga."),
 (12,"2026-09-11","Raquel PMERJ","(21) 98762-5333","Meta Ads","PMERJ","Proposta Enviada","Andressa","2026-09-11",
  "Perguntou informações. Equipe identificou interesse em PMERJ e ofereceu GCM Maricá e São Gonçalo. A conversa parou aqui - sem oferta de valores ou aula experimental para PMERJ, apenas oferta GCM. Raquel nunca foi atendida com a oferta real do concurso que ela quer (PMERJ). URGENTE: oferecer valores e aula experimental da turma PMERJ (não GCM)."),
 (13,"2026-09-09","Bergdias GCM - Gutemberg","n/a","Meta Ads","GCM Maricá","Proposta Enviada","Andressa","2026-09-12",
  "Em 12/09 às 9:18 enviou nome e concurso. Equipe listou turmas (manhã/noite/sábado) e ofereceu aula experimental. Ainda aguardando disponibilidade. Turno GCM Maricá definido."),
 (14,"2026-09-12","Karen Ribeiro GCM","n/a","Meta Ads","GCM Maricá","Proposta Enviada","Clara","2026-09-12",
  "Em 12/09 às 9:14 enviou nome 'Karen', turno 'Noite' e frequência 'Semanal'. Equipe perguntou disponibilidade de horário. Ainda sem resposta sobre horário concreto. Turno noite, semanal."),
 (15,"2026-09-12","Andreia Moreira CNU","n/a","Meta Ads","CNU Queimados Assistente Administrativo","Contato Feito","Andressa","2026-09-14",
  "Perguntou em 12/09 às 12:33 sobre 'turma pro concurso de Queimados Assistente Administrativo'. Equipe só respondeu no dia 14/09 às 8:58 (~44h depois) com mensagem genérica sobre viabilidade. Ponto de atenção: resposta tardia + genérica, sem data estimada de abertura."),
 (16,"2026-09-09","Walber Nunes","(21) 96768-8448","Meta Ads","PMERJ","Contato Feito","Andressa","2026-09-09",
  "Perguntou 'Só tem em Nilópolis?' - pergunta direta que decide se ele continua ou desiste. Equipe NÃO respondeu essa pergunta. Conversa parou aqui."),
 (17,"2026-09-09","Lead noturno (sem nome)","(21) 98563-3062","Meta Ads","PMERJ","Contato Feito","Clara","2026-09-09",
  "Perguntou 'boa noite' e 'pmerj'. Equipe ofereceu turno. Lead não respondeu sobre qual turno prefere. Conversa parou."),
 (18,"2026-09-11","Andressa (sem nome) - PMERJ 1","(21) 98254-5234","Meta Ads","PMERJ","Contato Feito","Andressa","2026-09-11",
  "Equipe pediu nome. Sem resposta do lead."),
 (19,"2026-09-11","Andressa (sem nome) - GCM","(21) 98839-3147","Meta Ads","GCM Maricá / São Gonçalo","Contato Feito","Andressa","2026-09-11",
  "Equipe pediu nome e área. Sem resposta."),
 (20,"2026-09-09","Gustavo","(21) 96429-4767","Meta Ads","PMERJ","Novo Lead","Ronan","2026-09-09",
  "Perguntou informações sobre o concurso. Equipe respondeu com erro de digitação 'PMERG' em vez de PMERJ. Sem follow-up do lead."),
 (21,"2026-09-09","Andressa (sem nome) - GCM 1628","(21) 96526-1628","Meta Ads","GCM Maricá","Novo Lead","Ronan","2026-09-09",
  "Clicou no anúncio GCM Maricá. Equipe apresentou e pediu nome. Sem resposta do lead."),
 (22,"2026-09-09","Andressa (sem nome) - PMERJ 9476","(21) 96532-9476","Meta Ads","PMERJ","Novo Lead","Ronan","2026-09-09",
  "Clicou no anúncio PMERJ. Equipe pediu nome e concurso. Sem resposta."),
 (23,"2026-09-09","Andressa (sem nome) - PMERJ 4076","(21) 97025-4076","Meta Ads","PMERJ","Novo Lead","Ronan","2026-09-09",
  "Equipe pediu nome. Sem resposta do lead."),
 (24,"2026-09-09","Andressa (sem nome) - PMERJ 9106","(21) 97030-9106","Meta Ads","PMERJ","Novo Lead","Ronan","2026-09-09",
  "Clicou no anúncio. Equipe pediu nome. Sem resposta."),
 (25,"2026-09-09","Andressa (sem nome) - GCM 4965","(21) 97735-4965","Meta Ads","GCM Maricá","Novo Lead","Ronan","2026-09-09",
  "Equipe pediu nome. Sem resposta."),
 (26,"2026-09-09","Andressa (sem nome) - PMERJ 4969","(21) 98297-4969","Meta Ads","PMERJ","Novo Lead","Ronan","2026-09-09",
  "Mandou mensagem às 23h54. Equipe só respondeu às 10h28 do dia seguinte (~10h30 de espera). Pediu nome. Sem resposta. Atraso de ~10h30 em retomar."),
 (27,"2026-09-09","Andressa (sem nome) - PMERJ 7968","(21) 98377-7968","Meta Ads","PMERJ","Novo Lead","Ronan","2026-09-09",
  "Equipe pediu nome. Sem resposta."),
 (28,"2026-09-09","Andressa (sem nome) - PMERJ 7500","(21) 98699-7500","Meta Ads","PMERJ","Novo Lead","Clara","2026-09-09",
  "Equipe pediu nome. Sem resposta."),
 (29,"2026-09-09","Andressa (sem nome) - sem info","(21) 99042-1362","Meta Ads","Não informado","Novo Lead","Ronan","2026-09-09",
  "Equipe pediu nome e concurso. Sem resposta."),
 (30,"2026-09-09","Andressa (sem nome) - GCM 1964","(21) 99605-1964","Meta Ads","GCM Maricá","Novo Lead","Clara","2026-09-09",
  "Equipe pediu nome. Sem resposta."),
 (31,"2026-09-09","Andressa (sem nome) - sem info 0254","(21) 99711-0254","Meta Ads","Não informado","Novo Lead","Ronan","2026-09-09",
  "Equipe pediu nome. Sem resposta."),
 (32,"2026-09-09","Andressa (sem nome) - GCM 1224","(21) 98802-1224","Meta Ads","GCM Maricá","Novo Lead","Clara","2026-09-09",
  "Só clicou no anúncio. Sem resposta."),
 (33,"2026-09-09","Andressa (sem nome) - PMERJ 6720","(21) 99068-6720","Meta Ads","PMERJ","Novo Lead","Ronan","2026-09-09",
  "Respondeu às 22h19. Equipe só respondeu às 9h06 do dia seguinte (~11h de espera). Pediu nome. Sem resposta. Atraso de ~11h em retomar."),
 (34,"2026-09-09","Andressa (sem nome) - PMERJ 3360","(21) 99228-3360","Meta Ads","PMERJ","Novo Lead","Clara","2026-09-09",
  "Clicou no anúncio. Sem resposta."),
 (35,"2026-09-09","Andressa (sem nome) - sem info clique","n/a","Meta Ads","PMERJ","Novo Lead","Ronan","2026-09-09",
  "Só registro de clique no anúncio. Sem interação real."),
 (36,"2026-09-10","Andressa (sem nome) - Marinha","(21) 99838-0012","Meta Ads","Marinha (não atendido)","Novo Lead","Clara","2026-09-10",
  "Perguntou sobre prova e inscrição marinha. Equipe respondeu com mensagem de voz e ofereceu aula experimental. Sem resposta do lead. Retomar com informação sobre inscrição de marinha (se houver) ou redirecionar para concurso disponível."),
 (37,"2026-09-10","Leticia Bombeiro","n/a","Meta Ads","Bombeiro (não atendido)","Novo Lead","Ronan","2026-09-10",
  "Perguntou 'tem curso de bombeiro?'. Equipe ofereceu atendimento. Lead não respondeu sobre nome/concurso. Verificar disponibilidade de curso de bombeiro ou redirecionar para preparação de concursos afins."),
 (38,"2026-09-11","Flavio GCM","(21) 97492-7884","Meta Ads","GCM Maricá / São Gonçalo","Novo Lead","Clara","2026-09-11",
  "Perguntou informações. Equipe ofereceu GCM Maricá e São Gonçalo a partir de 14/09 e 19/09. Pediu nome e área. Sem resposta."),
 (39,"2026-09-11","Andressa (sem nome) - PMERJ 9657","(21) 97927-9657","Meta Ads","PMERJ","Novo Lead","Ronan","2026-09-11",
  "Clicou no anúncio PMERJ. Equipe enviou mensagem genérica de clique. Sem resposta do lead."),
 (40,"2026-09-11","Andressa (sem nome) - GCM 9716","(21) 98537-9716","Meta Ads","GCM Maricá","Novo Lead","Clara","2026-09-11",
  "Perguntou informações. Equipe ofereceu GCM Maricá e São Gonçalo. Pediu nome e área. Sem resposta."),
 (41,"2026-09-11","Andressa (sem nome) - PMERJ 3534","(21) 98858-3534","Meta Ads","PMERJ","Novo Lead","Ronan","2026-09-11",
  "Equipe ofereceu atendimento. Pediu nome, dúvida e concurso. Sem resposta do lead."),
 (42,"2026-08-03","Lead de Mesquita - 97960-7938","(21) 97960-7938","Meta Ads","GCM São Gonçalo presencial","Novo Lead","Clara","2026-09-14",
  "Caso de atenção especial. Contato original em 03/08: perguntou por GCM São Gonçalo presencial. Recusou PMERJ como alternativa ('não quero não... assim que abrir, entro em contato'). Deixou nome e bairro (Mesquita - Centro). Voltou sozinha em 02/09 perguntando se já havia previsão de turma - e recebeu apenas mensagem padrão de boas-vindas. É a lead mais engajada entre as frias e a única que voltou por iniciativa própria. Ação: responder com previsão real de turma."),
]

def phone_to_e164(raw):
    if not raw or raw.strip().lower() in ("n/a", "-", ""):
        return None
    no_suffix = re.sub(r"\(\s*\d+\s*\)\s*$", "", raw.strip())
    d = re.sub(r"\D", "", no_suffix)
    if d.startswith("0") and len(d) > 11:
        d = d[1:]
    if len(d) == 10 or len(d) == 11:
        d = "55" + d
    return d

# ── Mensagens prontas (decisão comercial humana revisou os rascunhos) ──
MSG = {
 1:"Flávio, sobre o aulão de sábado: entendo perfeitamente a questão do seu filho no ESPCEX. A gente consegue fazer sua aula experimental de outro jeito — online ou em outra data. Quer que eu já agende?",
 2:"Ramon, conseguiu resolver aquela situação do trabalho? Se já estiver tudo certo, posso te orientar sobre o próximo passo da matrícula.",
 3:"Brenda, você chegou a avaliar a turma de INSS que te passei? Se quiser, te oriento sobre a aula experimental — é um bom jeito de testar antes de decidir.",
 4:"Guilherme, a turma de GCM Maricá acabou de abrir. Você recebeu a tabela do combo — prefere manhã, noite ou sábado? Se quiser, te reservo uma aula experimental.",
 5:"Voltando pras suas perguntas, direto:\n• Inscrição: ainda não abriu — o edital oficial não foi publicado, mas assim que sair a gente te orienta.\n• Requisitos e valores do preparatório: vou confirmar com a equipe e te retorno hoje, pra não te passar nada errado.\nQuer que eu já separe uma aula experimental de PRF em paralelo?",
 6:"Retomando: você tinha demonstrado interesse no PMERJ. Pra te encaixar na turma certa — noite ou sábado funcionaria pra você?",
 7:"Douglas, você perguntou se o concurso de GCM Maricá é real — é, sim, e inclusive a primeira turma já está abrindo. Pra você ver na prática como é a preparação, quer fazer uma aula experimental?",
 8:"Marcelo, as turmas de GCM Queimados são de manhã, noite e sábado. Qual encaixa melhor na sua rotina?",
 9:"A turma de GCM Maricá abriu essa semana, noturno das 19h às 22h. Consegue decidir o horário? Se preferir, agendo uma visita na unidade pra você conhecer de perto.",
 10:"Elen, você mencionou que está de repouso — sem pressa. Quando estiver melhor, a turma de PMERJ segue aberta. Quer que eu deixe uma aula experimental reservada pra próxima semana?",
 11:"Das opções que você trouxe (PMERJ, PC, PRF, PF), qual é a prioridade pra você agora? Focando nela, te passo a turma e a aula experimental certa.",
 12:"Retomando aqui — seu interesse era PMERJ, certo? A turma noturna sai por 5x de R$300 no Pix ou R$330 no cartão (material R$50 e camisa R$75 à parte). Você prefere noite ou sábado? Se quiser, já te alinho uma aula experimental de PMERJ.",
 13:"Gutemberg, você chegou a fechar o horário da aula experimental de GCM Maricá? Se me confirmar o turno, já te garanto a vaga.",
 14:"Karen, vou confirmar a turma pra você: turno noite, certo? Qual horário funciona melhor, 19h? Assim já te garanto a vaga.",
 15:"Andreia, sobre Queimados — Assistente Administrativo: a gente ainda está validando a data de abertura do edital. Assim que confirmar, te aviso em primeiro lugar. Enquanto isso, quer uma aula experimental pra já começar a preparação?",
 16:"Walber, a unidade principal é em Nilópolis mesmo. Se você mora mais longe, me diz seu bairro que eu avalio a melhor opção de turma pra você.",
 17:"Você tinha chamado sobre PMERJ. A turma que você procura é pra noite ou sábado?",
 18:"Retomando aqui: você chegou a definir qual concurso quer? Se for PMERJ, te passo a turma certa. Quer uma aula experimental pra testar?",
 19:"Retomando: a turma de GCM Maricá acabou de abrir. Você chegou a definir o concurso que quer seguir? Se quiser, te explico como funciona a aula experimental.",
 20:"Retomando de onde a gente parou: você buscava informações do PMERJ. Se for fechar turma, prefere noite ou sábado? Se quiser, te explico como funciona a aula experimental.",
 21:"Você chamou sobre GCM Maricá. A turma acabou de abrir — prefere manhã, noite ou sábado? Quer uma aula experimental?",
 22:"Você tinha chamado sobre PMERJ. A turma que você procura é pra noite ou sábado?",
 23:"Retomando: você chegou a definir o concurso que quer? Se me disser, te passo a turma certa.",
 24:"Você tinha chamado sobre PMERJ. Se quiser, te passo as próximas opções de turma e uma aula experimental.",
 25:"Você chamou sobre GCM Maricá. A turma acabou de abrir — prefere manhã, noite ou sábado? Quer uma aula experimental?",
 26:"Você tinha chamado sobre PMERJ. A turma que você procura é pra noite ou sábado?",
 27:"Retomando: você chegou a definir o concurso que quer? Se me disser, te passo a turma certa.",
 28:"Retomando: você chegou a definir qual concurso quer? Se for PMERJ, te passo a turma certa. Quer uma aula experimental pra testar?",
 29:"Retomando por aqui: você chegou a definir qual concurso quer (PMERJ ou GCM)? Se me disser, te passo a turma certa.",
 30:"Você chamou sobre GCM Maricá. A turma acabou de abrir — prefere manhã, noite ou sábado? Quer uma aula experimental?",
 31:"Retomando por aqui: você chegou a definir qual concurso quer (PMERJ ou GCM)? Se me disser, te passo a turma certa.",
 32:"Você chamou sobre GCM Maricá. A turma acabou de abrir — prefere manhã, noite ou sábado? Quer uma aula experimental?",
 33:"Você tinha chamado sobre PMERJ. A turma que você procura é pra noite ou sábado?",
 34:"Retomando: você chegou a definir qual concurso quer? Se for PMERJ, te passo a turma certa. Quer uma aula experimental pra testar?",
 35:"Você chamou sobre PMERJ. Se ainda estiver avaliando, posso te passar as próximas opções de turma e uma aula experimental.",
 36:"Sobre Marinha: deixa eu confirmar com a equipe se atendemos esse concurso e te retorno. Enquanto isso, o que acha de conhecer a preparação com uma aula experimental?",
 37:"Sobre Bombeiro: vou confirmar com a equipe se atendemos e te retorno. Quer conhecer uma aula experimental de preparação enquanto isso?",
 38:"Flávio, a turma de GCM Maricá abriu (14/09) e São Gonçalo inicia dia 19/09. Qual delas você quer conhecer? Se quiser, te separo uma aula experimental.",
 39:"Você tinha chamado sobre PMERJ. A turma que você procura é pra noite ou sábado?",
 40:"Você chamou sobre GCM Maricá. A turma acabou de abrir — prefere manhã, noite ou sábado? Quer uma aula experimental?",
 41:"Retomando: você chegou a definir qual concurso quer? Se for PMERJ, te passo a turma certa. Quer uma aula experimental pra testar?",
 42:"Voltando à sua pergunta: sim, a turma de GCM de São Gonçalo está abrindo — a previsão é iniciar dia 19/09. Como você já tinha deixado o interesse salvo, quer que eu já te reserve uma aula experimental na turma presencial?",
}

# prioridade P0/P1/P2/P3 e intenção
PRIO = {
 1:"P0",2:"P0",3:"P1",4:"P1",5:"P0",6:"P0",7:"P1",8:"P1",9:"P1",10:"P1",11:"P1",12:"P0",13:"P1",14:"P1",15:"P0",
 16:"P0",17:"P1",18:"P1",19:"P1",20:"P0",21:"P2",22:"P2",23:"P2",24:"P2",25:"P2",26:"P2",27:"P2",28:"P2",29:"P2",
 30:"P2",31:"P2",32:"P2",33:"P2",34:"P2",35:"P3",36:"P2",37:"P2",38:"P1",39:"P2",40:"P2",41:"P2",42:"P0",
}
INTENCAO = {1:"quente",2:"quente",3:"morno",4:"morno",5:"morno",6:"morno",7:"morno",8:"morno",9:"morno",10:"morno",11:"morno",12:"quente",
 13:"morno",14:"morno",15:"morno",16:"morno",17:"morno",18:"frio",19:"frio",20:"frio",21:"frio",22:"frio",23:"frio",24:"frio",25:"frio",
 26:"frio",27:"frio",28:"frio",29:"frio",30:"frio",31:"frio",32:"frio",33:"frio",34:"frio",35:"frio",36:"frio",37:"frio",38:"frio",
 39:"frio",40:"frio",41:"frio",42:"quente"}

MOTIVO = {
 1:"Objeção real (filho no ESPCEX no dia do aulão) — negociável; precisa de alternativa à aula presencial.",
 2:"Aguardando resolução de situação no trabalho antes de fechar; pediu prazo e retornar espontaneamente.",
 3:"Recebeu valores e parou — possível objeção de preço não declarada; reengajar com aula experimental.",
 4:"Recebeu tabela combo e parou — não confirmou aulão; reengajar com tour da turma aberta.",
 5:"Perguntas concretas (inscrição, requisitos, edital, valores) nunca respondidas — atendimento falhou.",
 6:"Erro de digitação 'PMERG' + lead não percebeu conversa ativa; retomar com PMERJ e perguntar turno.",
 7:"Dúvida de legitimidade do concurso; precisa de reforço de credibilidade + prova prática.",
 8:"Recebeu turmas e parou sem escolher turno; fechar a escolha de turno.",
 9:"Confirmou GCM noturno mas não confirmou aulão; aulão passou — usar turma aberta como gatilho.",
 10:"Recebeu valores, disse 'Entendi'; repouso médico — sem pressa, reservar aula na próxima semana.",
 11:"Sem telefone; prioridade difusa (vários concursos); definir o concurso-alvo.",
 12:"Equipe desviou conversa para GCM; nunca recebeu oferta real de PMERJ — corrigir rota.",
 13:"Sem telefone; aguardando disponibilidade da aula experimental.",
 14:"Sem telefone; aguardando horário concreto (noite definido, horário não).",
 15:"Sem telefone; resposta tardia + genérica da equipe; sem data de abertura.",
 16:"Pergunta direta (unidade Nilópolis) sem resposta — decidir continuidade.",
 17:"Equipe perguntou turno e lead não respondeu; retomar turno.",
 18:"Equipe pediu nome; sem resposta.",
 19:"Equipe pediu nome/área; sem resposta.",
 20:"Erro de digitação 'PMERG'; sem follow-up posterior.",
 21:"Só clique + pedido de nome; sem resposta.",
 22:"Clique PMERJ; sem resposta.",
 23:"Pedido de nome; sem resposta.",
 24:"Clique PMERJ; sem resposta.",
 25:"Pedido de nome; sem resposta.",
 26:"Resposta da equipe ~10h30 após lead; sem resposta seguinte.",
 27:"Pedido de nome; sem resposta.",
 28:"Pedido de nome; sem resposta.",
 29:"Pedido de nome/concurso; sem resposta.",
 30:"Pedido de nome; sem resposta.",
 31:"Pedido de nome/concurso; sem resposta.",
 32:"Só clique; sem resposta.",
 33:"Resposta da equipe ~11h após lead; sem resposta seguinte.",
 34:"Só clique; sem resposta.",
 35:"Sem interação real (só registro de clique); sem telefone.",
 36:"Concurso Marinha não atendido; equipe respondeu com áudio; sem resposta do lead.",
 37:"Curso Bombeiro não confirmado; sem telefone.",
 38:"Equipe ofereceu turmas a partir de 14/09 e 19/09; pediu nome; sem resposta.",
 39:"Mensagem genérica de clique PMERJ; sem resposta.",
 40:"Pedido de nome/área; sem resposta.",
 41:"Pedido de nome/dúvida/concurso; sem resposta.",
 42:"Voltou espontaneamente perguntando previsão da turma; recebeu resposta genérica; turma São Gonçalo abre 19/09.",
}

def build():
    leads = []
    for (rid, data, nome, raw, origem, turma, etapa, resp, ultima, obs) in ROWS:
        e164 = phone_to_e164(raw)
        jid = e164 + "@s.whatsapp.net" if e164 else None
        leads.append({
            "id": rid,
            "data_entrada": data,
            "nome": nome,
            "whatsapp_raw": raw,
            "e164": e164,
            "jid": jid,
            "origem": origem,
            "turma": turma,
            "etapa": etapa,
            "responsavel": resp,
            "ultima_interacao": ultima,
            "observacao": obs,
            "analise": {
                "prioridade": PRIO[rid],
                "intencao": INTENCAO[rid],
                "concurso": turma.split(" (")[0],
                "motivo_parada": MOTIVO[rid],
            },
            "mensagem_pronta": MSG[rid],
            "envio": {
                "previsto": "2026-09-15",
                "status": "sem_numero" if not e164 else "pronto",
            },
        })
    return leads

def main():
    leads = build()
    ds = {
        "gerado_em": "2026-09-15T00:30:00-03:00",
        "fonte": "Google Sheets — aba Leads (1wD4Xi5HGq680i27WdFm1Ym4aNiTHnShJYTYrQe8g5hs)",
        "responsaveis": {"Andressa": 24, "Clara": 11, "Ronan": 7}.__class__ and None,
        "contagem": {
            "total": len(leads),
            "por_prioridade": {p: sum(1 for l in leads if l["analise"]["prioridade"] == p) for p in ("P0","P1","P2","P3")},
            "por_intencao": {i: sum(1 for l in leads if l["analise"]["intencao"] == i) for i in ("quente","morno","frio")},
            "por_responsavel": {r: sum(1 for l in leads if l["responsavel"] == r) for r in ("Andressa","Clara","Ronan")},
            "sem_telefone": sum(1 for l in leads if not l["e164"]),
            "com_mensagem_pronta": sum(1 for l in leads if l["mensagem_pronta"]),
        },
        "notas_contexto": [
            "Aulão de 12/09 já realizado — nenhuma nova mensagem deve convidar para ele.",
            "GCM Maricá: primeira turma abriu em 14/09. GCM São Gonçalo: previsão de início 19/09.",
            "Valores documentados no CRM: combo GCM R$1.945,50 à vista (~R$332/mês) ou 5x R$389,50 Pix; GCM Maricá R$300/mês Pix / R$330 cartão; PMERJ noturno semanal 5x R$300 Pix / R$330 cartão + material R$50 + camisa R$75.",
            "Acesso de gravação à planilha (API) está BLOQUEADO: token OAuth revogado/expirado — exigirá reautorização (1 clique no navegador).",
            "Regras da operação: responder pergunta objetiva antes de vender; não repetir o que o lead já informou.",
        ],
        "leads": leads,
    }
    path = os.path.join(DATA_DIR, "leads_epq_2026-09-15.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(ds, f, ensure_ascii=False, indent=2)
    print("JSON:", path, "|", len(leads), "leads")

    # ── plano MD ──
    P2_ORDER = {"quente": 0, "morno": 1, "frio": 2}
    P0 = [l for l in leads if l["analise"]["prioridade"] == "P0"]
    P1 = [l for l in leads if l["analise"]["prioridade"] == "P1"]
    P2 = [l for l in leads if l["analise"]["prioridade"] in ("P2", "P3")]
    for grp in (P0, P1, P2):
        grp.sort(key=lambda l: (P2_ORDER[l["analise"]["intencao"]], l["id"]))

    def block(title, fmodel, items):
        s = [f"## {title}", ""]
        for l in items:
            s.append(f"### {l['id']}. {l['nome']}  ")
            s.append(f"- **Concurso:** {l['analise']['concurso']} · **Etapa:** {l['etapa']} · **Resp.:** {l['responsavel']}")
            s.append(f"- **Intenção:** {l['analise']['intencao']} · **Prioridade:** {l['analise']['prioridade']}")
            s.append(f"- **Telefone:** {l['whatsapp_raw'] or 'n/a'} · **Última interação:** {l['ultima_interacao']}")
            s.append(f"- **Motivo da parada:** {l['analise']['motivo_parada']}")
            s.append(f"- **Próxima ação:** {l['mensagem_pronta']}")
            s.append("")
        return "\n".join(s).rstrip() + "\n"

    md = []
    md.append("# Loop de Recuperação de Leads EPQ — 15/09/2026\n")
    md.append("Operação executada por Hermes (camada de suporte comercial). Responsáveis humanos continuam como titulares do lead. Seguir o plano para disparo (fila P0/P1) e atualização da planilha.\n")
    c = ds["contagem"]
    md.append(f"**Resumo:** {c['total']} leads · P0={c['por_prioridade']['P0']} · P1={c['por_prioridade']['P1']} · P2={c['por_prioridade']['P2']} · P3={c['por_prioridade']['P3']} | quentes={c['por_intencao']['quente']} · mornos={c['por_intencao']['morno']} · frios={c['por_intencao']['frio']} | sem telefone={c['sem_telefone']}\n")
    md.append("## Contexto\n")
    for n in ds["notas_contexto"]:
        md.append(f"- {n}")
    md.append("")
    md.append(block("PRIORIDADE 0 — Responder pergunta direta / lead quente (disparo 15/09)", None, P0))
    md.append(block("PRIORIDADE 1 — Recebeu proposta e parou (disparo 15/09)", None, P1))
    md.append(block("PRIORIDADE 2 — Novos/frios — 1º contato de recuperação (sequência curta)", None, P2))
    md.append("""## Regras p/ o responsável
- Se o lead responder com objeção de preço/desconto → encaminhar para o responsável humano (nunca conceder desconto automaticamente).
- Se o lead pedir atendimento humano ou estiver pronto para matrícula → handoff com registro no CRM.
- Não repetir pergunta já respondida. Não mencionar o aulão de 12/09 (já ocorreu).""")

    plan_path = os.path.join(DATA_DIR, "leads_epq_followup_plan.md")
    with open(plan_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print("MD  :", plan_path)

    # ── fila de disparo ──
    queue = {
        "gerado_em": ds["gerado_em"],
        "canal": "whatsapp (Baileys via hermes send)",
        "janela_envio": "08:00–20:00 BRT (fora da janela requer --force)",
        "itens": [],
    }
    for l in leads:
        if l["envio"]["status"] == "pronto" and l["analise"]["prioridade"] in ("P0", "P1"):
            queue["itens"].append({
                "id": l["id"],
                "nome": l["nome"],
                "jid": l["jid"],
                "prioridade": l["analise"]["prioridade"],
                "intencao": l["analise"]["intencao"],
                "responsavel": l["responsavel"],
                "mensagem": l["mensagem_pronta"],
            })
    queue["itens"].sort(key=lambda x: (0 if x["prioridade"] == "P0" else 1, x["id"]))
    qpath = os.path.join(DATA_DIR, "leads_epq_dispatch_queue.json")
    with open(qpath, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)
    print("FILA:", qpath, "|", len(queue["itens"]), "itens P0/P1")

main()