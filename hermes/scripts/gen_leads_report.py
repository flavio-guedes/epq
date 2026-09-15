#!/usr/bin/env python3
"""Gera /Users/mac/HermesWorkspace/leads_15_09.html no formato do cron epq
(panorama de leads), alimentado pelo dataset leads_epq_2026-09-15.json."""
import json, os, re

ROOT = os.path.expanduser("~/HermesWorkspace")
SRC = os.path.join(ROOT, "leads_12_09.html")
DATA = os.path.join(ROOT, "hermes/data/leads_epq_2026-09-15.json")
OUT = os.path.join(ROOT, "leads_15_09.html")

ds = json.load(open(DATA, encoding="utf-8"))
leads = ds["leads"]; c = ds["contagem"]

css = re.search(r"<style>(.*?)</style>", open(SRC, encoding="utf-8").read(), re.S).group(1)

BADGE = {
 "GCM": '<span class="badge gcm">GCM</span>',
 "GCM Maricá": '<span class="badge gcm">GCM Maricá</span>',
 "GCM Maricá combo": '<span class="badge gcm">GCM Maricá combo</span>',
 "GCM Maricá noturno": '<span class="badge gcm">GCM Maricá noturno</span>',
 "GCM Maricá / São Gonçalo": '<span class="badge gcm">GCM Maricá / São Gonçalo</span>',
 "GCM São Gonçalo presencial": '<span class="badge gcm">GCM São Gonçalo</span>',
 "GCM Queimados": '<span class="badge gcm">GCM Queimados</span>',
 "PMERJ": '<span class="badge pmerj">PMERJ</span>',
 "PMERJ noturno semanal": '<span class="badge pmerj">PMERJ noturno semanal</span>',
 "PMERJ (digitado PMERG)": '<span class="badge pmerj">PMERJ (digitado PMERG)</span>',
 "INSS": '<span class="badge inss">INSS</span>',
 "PRF Agente Administrativo": '<span class="badge pmerj">PRF</span>',
 "Marinha (não atendido)": '<span class="badge pmerj">Marinha</span>',
 "Bombeiro (não atendido)": '<span class="badge pmerj">Bombeiro</span>',
 "PMERJ / PC / PRF / PF / Secretarias": '<span class="badge pmerj">Múltiplos</span>',
 "Não informado": '<span class="badge pmerj">—</span>',
 "CNU Queimados Assistente Administrativo": '<span class="badge gcm">CNU Queimados</span>',
}

def concurso_badge(l):
    key = l["analise"]["concurso"]
    return BADGE.get(key, BADGE["Não informado"])

def tel(l):
    return l["whatsapp_raw"] if l["whatsapp_raw"] != "n/a" else "sem nº"

def table(rows, extra_col="Prioridade"):
    th = ("<thead><tr><th>Lead</th><th>Badge</th><th>Concurso</th><th>Contato</th>"
          "<th>Motivo da parada</th><th>Mensagem pronta (15/09)</th>"
          + (f"<th>{extra_col}</th>" if extra_col else "") + "</tr></thead>")
    body = []
    for l in rows:
        prio = l["analise"]["prioridade"]
        dot = "%s" % ("P0" if prio == "P0" else prio)
        contato = f"{l['ultima_interacao']} · {tel(l)} · {l['responsavel']}"
        body.append(
            "<tr>"
            f"<td class='name'>{l['nome']}</td>"
            f"<td>{concurso_badge(l)}</td>"
            f"<td>{l['analise']['concurso']}</td>"
            f"<td><span class='muted'>{contato}</span></td>"
            f"<td>{l['analise']['motivo_parada']}</td>"
            f"<td>{l['mensagem_pronta']}</td>"
            f"<td><b>{dot}</b></td>"
            "</tr>")
    return ("<div class='table-card'><div class='table-scroll'><table>" + th +
            "<tbody>" + "".join(body) + "</tbody></table></div></div>")

P0 = [l for l in leads if l["analise"]["prioridade"] == "P0"]
P1 = [l for l in leads if l["analise"]["prioridade"] == "P1"]
P2 = [l for l in leads if l["analise"]["prioridade"] in ("P2", "P3")]

TAIL_JS = """
gsap.registerPlugin(ScrollTrigger);
gsap.utils.toArray('.reveal').forEach(el=>{gsap.fromTo(el,{opacity:0,y:28},{opacity:1,y:0,duration:.7,ease:'power2.out',scrollTrigger:{trigger:el,start:'top 85%'}})});
document.querySelectorAll('.fbar-fill').forEach(el=>{gsap.to(el,{scaleX:1,duration:1,ease:'power3.out',scrollTrigger:{trigger:el,start:'top 90%'}})});
document.querySelectorAll('.kpi .n').forEach(el=>{const t=+el.dataset.count; const o={v:0}; gsap.to(o,{v:t,duration:1.2,ease:'power2.out',onUpdate:()=>el.textContent=Math.round(o.v)});});
"""

html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Panorama de Leads — CRM EPQ · 15/09/2026</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/ScrollTrigger.min.js"></script>
<style>
{css}
</style>
</head>
<body>

<header class="hero" id="topo">
  <div style="height:180px;background:linear-gradient(120deg,#0d1834,#2f6bff 55%,#5c9bff);opacity:.92;"></div>
</header>

<section class="intro">
  <div class="intro-inner">
    <div class="eyebrow"><span class="pulse"></span>CRM EPQ · loop de recuperação · 15 de Setembro de 2026</div>
    <h1>Prioridade de follow-up<br><em>cada lead tem a próxima ação definida.</em></h1>
    <p class="lead">Análise dos {c['total']} leads da planilha (aba Leads) com priorização P0–P3, causa da parada, mensagem pronta e responsável. Aulão 12/09 encerrado — novo gatilho é a abertura das turmas GCM Maricá (14/09) e GCM São Gonçalo (19/09). Nenhum dado inventado: tudo extraído do CRM.</p>
    <div class="hero-cta">
      <a class="btn btn-primary" href="#p0">Fila P0 (responder direto) ↓</a>
      <a class="btn btn-ghost" href="#p1">Fila P1 (recebeu proposta)</a>
    </div>
    <div class="kpi-row">
      <div class="kpi"><div class="n" data-count="{c['total']}">0</div><div class="l">leads na base</div></div>
      <div class="kpi green"><div class="n green" data-count="{c['por_prioridade']['P0']}">0</div><div class="l">P0 · é preciso responder</div></div>
      <div class="kpi amber"><div class="n amber" data-count="{c['por_prioridade']['P1']}">0</div><div class="l">P1 · recebeu proposta e parou</div></div>
      <div class="kpi red"><div class="n red" data-count="{c['por_prioridade']['P2']+c['por_prioridade']['P3']}">0</div><div class="l">P2/P3 · novos e frios</div></div>
    </div>
  </div>
</section>

<nav class="navbar">
  <div class="navbar-inner">
    <span class="brand">EPQ <b>·</b> RECUPERAÇÃO 15/09</span>
    <a href="#p0" class="active">P0 · Responder</a>
    <a href="#p1">P1 · Proposta</a>
    <a href="#p2">P2/P3 · Novos/frios</a>
    <a href="#atend">Falhas de atendimento</a>
    <a href="#especial">Caso especial</a>
  </div>
</nav>

<div class="wrap">

  <section id="p0">
    <div class="section-head reveal">
      <h2>Prioridade 0 — pergunta direta sem resposta / lead quente</h2>
      <span class="count">{len(P0)} leads · disparo previsto 15/09</span>
    </div>
    <div class="group reveal">
      <div class="group-title"><span class="dot red"></span><h3>Fila P0</h3><span>a próxima ação é responder uma pergunta concreta ou retomar lead quente</span></div>
      {table(P0)}
    </div>
  </section>

  <section id="p1">
    <div class="section-head reveal">
      <h2>Prioridade 1 — recebeu proposta e parou</h2>
      <span class="count">{len(P1)} leads · disparo previsto 15/09</span>
    </div>
    <div class="group reveal">
      <div class="group-title"><span class="dot amber"></span><h3>Fila P1</h3><span>viram preço/detalhes · reengajar com aula experimental ou fechar turno</span></div>
      {table(P1)}
    </div>
  </section>

  <section id="p2">
    <div class="section-head reveal">
      <h2>Prioridade 2/3 — novos e frios</h2>
      <span class="count">{len(P2)} leads · 1º contato de recuperação (sequência curta)</span>
    </div>
    <div class="group reveal">
      <div class="group-title"><span class="dot grey"></span><h3>Fila P2/P3</h3><span>só clicaram ou nunca responderam · priorizar quentes/mornos deste grupo</span></div>
      {table(P2)}
    </div>
  </section>

  <section id="atend">
    <div class="section-head reveal">
      <h2>Falhas de atendimento a corrigir hoje</h2>
      <span class="count">erros da própria equipe que estagnaram leads</span>
    </div>
    <div class="tag-grid">
      <div class="tag-card problem-card reveal"><div class="title">❌ Pergunta direta nunca respondida</div><div class="desc"><b>Lead PRF (98055-5629)</b> — inscrição, requisitos, edital, valores seguem sem resposta. <b>Walber Nunes</b> — "Só tem em Nilópolis?" sem resposta.</div></div>
      <div class="tag-card problem-card reveal"><div class="title">⚠️ Oferta fora da intenção do lead</div><div class="desc"><b>Raquel PMERJ</b> pediu PMERJ e recebeu oferta de GCM. Correção: oferecer turma PMERJ real (5x R$300 Pix / R$330 cartão).</div></div>
      <div class="tag-card problem-card reveal"><div class="title">✍️ Erro de digitação "PMERG"</div><div class="desc"><b>Gustavo (Ronan)</b> e <b>Andressa 98294-6742</b> receberam a mensagem com "PMERG". Retomar com PMERJ correto.</div></div>
      <div class="tag-card problem-card reveal"><div class="title">⏳ Resposta tardia + genérica</div><div class="desc"><b>Andreia CNU</b> esperou ~44h e recebeu resposta genérica sem data de abertura do edital de Queimados.</div></div>
      <div class="tag-card problem-card reveal"><div class="title">🕐 Retomada em +10h</div><div class="desc">Leads <b>98297-4969</b> e <b>99068-6720</b> responderam de madrugada e só foram tratados no dia seguinte.</div></div>
      <div class="tag-card problem-card reveal"><div class="title">📌 Curso não confirmado</div><div class="desc"><b>Leticia Bombeiro</b> e lead <b>Marinha</b> perguntaram por concursos que a EPQ ainda não confirmou atendimento — validar e retornar.</div></div>
    </div>
  </section>

  <section id="especial">
    <div class="section-head reveal">
      <h2>Caso especial — lead de Mesquita (GCM São Gonçalo)</h2>
      <span class="count">a mais engajada entre as frias</span>
    </div>
    <div class="tag-grid">
      <div class="tag-card special reveal"><div class="title">⭐ Voltou por iniciativa própria</div><div class="desc">Contato em 03/08 pedindo GCM São Gonçalo presencial; recusou PMERJ. Deixou nome e bairro (Mesquita). Voltou sozinha em 02/09 perguntando previsão de turma — recebeu só a mensagem padrão.<br><br>
      <b>Correção:</b> responder com a previsão real — turma de GCM São Gonçalo inicia <b>19/09</b> — e reservar aula experimental. Mensagem já pronta no dataset.</div></div>
      <div class="tag-card special reveal"><div class="title">🔵 Contexto de turmas</div><div class="desc">GCM Maricá abriu 14/09 · GCM São Gonçalo inicia 19/09 · combo GCM R$1.945,50 à vista (~R$332/mês) · 5x R$389,50 Pix · GCM Maricá noturno 19h–22h 2ª–6ª (5 meses, R$300/mês Pix / R$330 cartão).</div></div>
    </div>
  </section>

</div>

<footer>Gerado por Hermes · dataset hermes/data/leads_epq_2026-09-15.json · 15/09/2026 · gravação na planilha depende de reautorização do Google (token revogado)</footer>

<script>
TAIL_JS
</script>
</body>
</html>
"""

open(OUT, "w", encoding="utf-8").write(html)
print("OK:", OUT, "|", os.path.getsize(OUT), "bytes")