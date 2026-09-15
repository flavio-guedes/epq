"""
Sales Enablement Agent — Core Intelligence Engine

Papel:
- Calcular Sales Score
- Avaliar Deal Health
- Gerar Next Best Action
- Respeitar regras do agente sem inventar dados
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class SalesScoreResult:
    sales_score: int
    tier: str
    classification: str
    confidence: str
    missing_fields: List[str]
    components: Dict[str, float]


@dataclass
class DealHealthResult:
    health: str
    reason: str
    risks: List[str]
    next_step_urgency: str
    last_contact_days: Optional[int] = None


@dataclass
class NextBestActionResult:
    action: str
    reason: str
    when: str
    channel: str
    message_template: str
    priority: str


DEFAULT_WEIGHTS = {
    "icp_fit": 0.20,
    "commercial_potential": 0.20,
    "identified_need": 0.20,
    "authority_influence": 0.15,
    "timing": 0.10,
    "engagement": 0.10,
    "explicit_intent": 0.05,
}


def _safe_int(value: Any) -> int:
    try:
        return int(float(value))
    except Exception:
        return 0


def _safe_str(value: Any) -> str:
    return "" if value is None else str(value)


def _today() -> datetime:
    return datetime.utcnow()


def _days_since(date_str: Optional[str]) -> Optional[int]:
    if not date_str:
        return None
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return (_today() - dt).days
    except Exception:
        return None


def calculate_sales_score(lead: Dict[str, Any], weights: Optional[Dict[str, float]] = None) -> SalesScoreResult:
    weights = weights or DEFAULT_WEIGHTS
    components = {
        "icp_fit": float(_score_icp_fit(lead)),
        "commercial_potential": float(_score_commercial_potential(lead)),
        "identified_need": float(_score_identified_need(lead)),
        "authority_influence": float(_score_authority(lead)),
        "timing": float(_score_timing(lead)),
        "engagement": float(_score_engagement(lead)),
        "explicit_intent": float(_score_explicit_intent(lead)),
    }

    score = int(sum(weights[k] * components[k] for k in components))
    score = max(0, min(100, score))

    if score >= 90:
        classification = "PRIORIDADE MÁXIMA"
    elif score >= 75:
        classification = "ALTA PRIORIDADE"
    elif score >= 60:
        classification = "OPORTUNIDADE"
    elif score >= 40:
        classification = "NUTRIÇÃO"
    else:
        classification = "BAIXA PRIORIDADE"

    missing = [k.replace("_", " ") for k, v in lead.items() if v in (None, "", []) and k in {"company", "cargo", "telefone", "email", "linkedin", "segment", "history"}]
    confidence = "low" if len(missing) >= 4 else "medium" if missing else "high"

    return SalesScoreResult(
        sales_score=score,
        tier=classification,
        classification=classification,
        confidence=confidence,
        missing_fields=sorted(missing),
        components=components,
    )


def _score_icp_fit(lead: Dict[str, Any]) -> int:
    score = 40
    company = _safe_str(lead.get("company") or lead.get("empresa"))
    cargo = _safe_str(lead.get("cargo") or lead.get("role"))
    segment = _safe_str(lead.get("segment") or lead.get("categoria"))
    if company:
        score += 20
    if cargo:
        score += 20
    if segment and segment.lower() not in {"", "n/a", "nao informado"}:
        score += 20
    return min(100, score)


def _score_commercial_potential(lead: Dict[str, Any]) -> int:
    score = 30
    tier = _safe_str(lead.get("tier") or lead.get("Tier")).upper()
    if tier.startswith("TIER 1") or tier == "TIER1":
        score += 40
    elif tier.startswith("TIER 2") or tier == "TIER2":
        score += 25
    elif tier:
        score += 10
    score += min(40, _safe_int(lead.get("score") or lead.get("Score")))
    stage = _safe_str(lead.get("stage") or lead.get("status")).lower()
    if stage in {"opportunity", "proposal", "negotiation"}:
        score += 20
    return min(100, score)


def _score_identified_need(lead: Dict[str, Any]) -> int:
    score = 20
    history = _safe_str(lead.get("history") or lead.get("historico") or lead.get("notes"))
    needs = _safe_str(lead.get("needs") or lead.get("dores") or lead.get("trecho"))
    if any(k in history.lower() for k in ["precisa", "dor", "problema", "objetivo", "quer ", "necessidade"]):
        score += 40
    if needs:
        score += 40
    return min(100, score)


def _score_authority(lead: Dict[str, Any]) -> int:
    score = 20
    cargo = _safe_str(lead.get("cargo") or lead.get("role")).lower()
    company = _safe_str(lead.get("company") or lead.get("empresa"))
    decision_keywords = ["ceo", "diretor", "head", "fundador", "founder", "sócio", "socio", "owner", "presidente", "gerente"]
    if any(k in cargo for k in decision_keywords):
        score += 60
    elif any(k in cargo for k in ["coordenador", "especialista", "analista", "assistente"]):
        score += 25
    if company:
        score += 20
    return min(100, score)


def _score_timing(lead: Dict[str, Any]) -> int:
    score = 20
    urgency = _safe_str(lead.get("urgency") or lead.get("timing") or lead.get("Data Contato") or lead.get("data"))
    days = _days_since(urgency)
    if days is not None and days <= 7:
        score += 50
    elif days is not None and days <= 30:
        score += 35
    if _safe_str(lead.get("stage") or lead.get("status")).lower() in {"opportunity", "proposal", "negotiation"}:
        score += 30
    return min(100, score)


def _score_engagement(lead: Dict[str, Any]) -> int:
    score = 20
    steps = lead.get("steps") or lead.get("interactions") or []
    if isinstance(steps, list):
        score += min(50, len(steps) * 10)
    last_contact = lead.get("last_contact_at") or lead.get("Data Contato") or lead.get("data")
    days = _days_since(_safe_str(last_contact))
    if days is not None and days <= 7:
        score += 30
    return min(100, score)


def _score_explicit_intent(lead: Dict[str, Any]) -> int:
    score = 20
    text = json.dumps(lead, ensure_ascii=False).lower()
    intent_signals = ["proposta", "reunião", "reuniao", "fechar", "contratar", "iniciar", "começar", "comecar", "quero", "vamos"]
    if any(s in text for s in intent_signals):
        score += 80
    return min(100, score)


def evaluate_deal_health(lead: Dict[str, Any]) -> DealHealthResult:
    risks: List[str] = []
    stage = _safe_str(lead.get("stage") or lead.get("status")).lower()
    last_contact = _days_since(_safe_str(lead.get("last_contact_at") or lead.get("Data Contato") or lead.get("data")))
    interactions = lead.get("steps") or lead.get("interactions") or []
    engagement_score = min(100, len(interactions) * 10)
    need_clarity = 0
    text = _safe_str(lead.get("history") or lead.get("historico") or lead.get("needs") or lead.get("dores") or lead.get("trecho"))
    if text:
        need_clarity = 60
        if any(k in text.lower() for k in ["precisa", "dor", "problema", "objetivo"]):
            need_clarity = 90

    if last_contact is None:
        risks.append("sem data de último contato")
    elif last_contact > 21:
        risks.append(f"lead parado há {last_contact} dias")

    if engagement_score < 30:
        risks.append("engajamento baixo")
    if need_clarity < 50:
        risks.append("necessidade pouco clara")

    if stage in {"won", "lost"}:
        health = "encerrado"
        reason = "oportunidade finalizada"
    elif not risks:
        health = "🟢 HEALTHY"
        reason = "indicadores saudáveis"
    elif len(risks) == 1 and "lead parado" in risks[0]:
        health = "🟡 AT RISK"
        reason = "risco por atraso no follow-up"
    else:
        health = "🔴 CRITICAL"
        reason = "múltiplos riscos detectados"

    urgency = "alta" if health.startswith("🔴") else "média" if health.startswith("🟡") else "baixa"
    return DealHealthResult(
        health=health,
        reason=reason,
        risks=risks,
        next_step_urgency=urgency,
        last_contact_days=last_contact,
    )


def generate_next_best_action(lead: Dict[str, Any], score_result: Optional[SalesScoreResult] = None, health: Optional[DealHealthResult] = None) -> NextBestActionResult:
    score_result = score_result or calculate_sales_score(lead)
    health = health or evaluate_deal_health(lead)
    stage = _safe_str(lead.get("stage") or lead.get("status")).lower()
    channel = _safe_str(lead.get("channel") or lead.get("Fonte") or "whatsapp").lower()
    name = _safe_str(lead.get("nome") or lead.get("Nome") or "Lead")

    if stage in {"won"}:
        return NextBestActionResult("manter relacionamento", "oportunidade fechada", "continuar", channel, f"{name}, vou acompanhar para indicar materiais complementares se surgirem.", "baixa")
    if stage in {"lost"}:
        return NextBestActionResult("nutrir para reativação futura", "oportunidade perdida no momento", "em 30 dias", channel, f"{name}, vou manter contato leve sem pressionar para reativar quando timing mudar.", "baixa")

    if health.health.startswith("🔴") or score_result.sales_score >= 75:
        action = "propor reunião ou enviar case relevante"
        reason = "lead quente com fit alto" if score_result.sales_score >= 75 else "deal em risco e necessidade de avanço comercial"
        when = "amanhã"
        message = f"{name}, com base no que você comentou, um próximo passo rápido pode ser este material ou uma conversa de 15 minutos."
    elif score_result.sales_score >= 60:
        action = "fazer pergunta de diagnóstico e ajustar abordagem"
        reason = "potencial identificado, mas ainda sem clareza total"
        when = "nos próximos 3 dias"
        message = f"{name}, antes de enviar algo genérico, vou fazer uma pergunta curta para entender melhor sua realidade."
    elif score_result.sales_score >= 40:
        action = "nutrir com conteúdo e agendar follow-up leve"
        reason = "oportunidade em maturação"
        when = "em 7 dias"
        message = f"{name}, vou deixar um material leve para quando for mais oportuno e volto em breve."
    else:
        action = "aguardar maturação ou reclassificar contato"
        reason = "baixo sinal comercial no momento"
        when = "em 15 dias"
        message = f"{name}, vou manter esse contato em baixa intensidade até surgir um sinal melhor."

    priority = "alta" if score_result.sales_score >= 75 or health.health.startswith("🔴") else "média" if score_result.sales_score >= 60 else "baixa"

    if stage in {"opportunity", "proposal", "negotiation"} and score_result.sales_score >= 60:
        action = "propor reunião ou enviar material direcionado"
        reason = "estágio avançado com potencial comercial"
        when = "nos próximos 2 dias"
        message = f"{name}, pelo estágio atual, vale avançar com material direcionado ou uma conversa objetiva de 20 minutos."
        priority = "alta"

    if channel not in {"whatsapp", "linkedin", "email", "telegram"}:
        channel = "whatsapp"

    return NextBestActionResult(
        action=action,
        reason=reason,
        when=when,
        channel=channel,
        message_template=message,
        priority=priority,
    )
