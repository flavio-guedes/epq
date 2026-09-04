import os
from datetime import datetime, time, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from models import User, Lead, Interaction, AuditLog, UserProfile, InteractionType
from auth import hash_password


TEAM_IDS = {
    "andressa": os.getenv("ROUTING_ANDRESSA_ID"),
    "clara": os.getenv("ROUTING_CLARA_ID"),
    "ronan": os.getenv("ROUTING_RONAN_ID"),
}

CAPACITY_LIMITS = {
    "green": int(os.getenv("ROUTING_CAP_GREEN", "5")),
    "yellow": int(os.getenv("ROUTING_CAP_YELLOW", "10")),
}
SLA_MINUTES = {
    "Quente": int(os.getenv("SLA_QUENTE", "5")),
    "Morno": int(os.getenv("SLA_MORNO", "15")),
    "Frio": int(os.getenv("SLA_FRIO", "30")),
}
MODE = os.getenv("ROUTING_MODE", "simulation").lower()

ANDRESSA_SCHEDULE = [
    {"days": [0, 1, 2, 3, 4], "start": time(9, 0), "end": time(17, 0)},
    {"days": [5], "start": time(9, 0), "end": time(13, 0)},
]
CLARA_SCHEDULE = [
    {"days": [0, 1, 2, 3, 4], "start": time(9, 0), "end": time(15, 0)},
]
RONAN_SCHEDULE = [
    {"days": [0, 1, 2, 3, 4, 5, 6], "start": time(0, 0), "end": time(23, 59)},
]
CLARA_TUE_THU_SECONDARY_START = time(14, 0)


def _is_in_schedule(now: datetime, schedule: List[Dict[str, Any]]) -> bool:
    weekday = now.weekday()
    current = now.time()
    for item in schedule:
        if weekday in item["days"]:
            if item["start"] <= current <= item["end"]:
                return True
            if current == time(23, 59, 59):
                return True
    return False


def _load_user(db: Session, user_id: Optional[str]) -> Optional[User]:
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()


def _active_lead_count(db: Session, user_id: Optional[str]) -> int:
    if not user_id:
        return 0
    return db.query(func.count(Lead.id)).filter(
        Lead.responsavel_id == user_id,
        Lead.status == "ativo",
    ).scalar() or 0


def _capacity_status(active: int) -> str:
    if active <= CAPACITY_LIMITS["green"]:
        return "green"
    if active <= CAPACITY_LIMITS["yellow"]:
        return "yellow"
    return "red"


def available_attendants(db: Session, now: Optional[datetime] = None) -> List[Dict[str, Any]]:
    now = now or datetime.utcnow()
    attendants = []
    for key, user_id in TEAM_IDS.items():
        user = _load_user(db, user_id)
        if not user or user.status != "ativo":
            continue
        schedule = RONAN_SCHEDULE if key == "ronan" else (ANDRESSA_SCHEDULE if key == "andressa" else CLARA_SCHEDULE)
        in_window = _is_in_schedule(now, schedule)
        secondary_today = False
        if key == "clara" and now.weekday() in [1, 3]:
            secondary_today = now.time() >= CLARA_TUE_THU_SECONDARY_START and _is_in_schedule(now, [
                {"days": [1, 3], "start": CLARA_TUE_THU_SECONDARY_START, "end": time(15, 0)}
            ])
        active = _active_lead_count(db, user.id)
        capacity = _capacity_status(active)
        status = "FORA DO HORÁRIO"
        if key == "ronan":
            status = "DISPONÍVEL" if in_window else "DISPONÍVEL"
        elif in_window or secondary_today:
            if capacity == "red":
                status = "OCUPADA"
            elif capacity == "yellow":
                status = "ATENÇÃO"
            else:
                status = "DISPONÍVEL"
        attendants.append({
            "key": key,
            "id": user.id,
            "name": user.nome,
            "status": status,
            "active": active,
            "capacity": capacity,
            "in_window": bool(in_window or secondary_today),
        })
    return attendants


def _temperature_rank(temperature: Optional[str]) -> int:
    mapping = {"Quente": 0, "Morno": 1, "Frio": 2}
    return mapping.get(temperature or "", 3)


def _sla_risk(lead: Lead, now: datetime) -> Optional[Dict[str, Any]]:
    temp = lead.temperatura or "Frio"
    sla = SLA_MINUTES.get(temp, SLA_MINUTES["Frio"])
    wait_minutes = None
    if lead.created_at:
        wait_minutes = int((now - lead.created_at).total_seconds() // 60)
    near_breach = False
    breached = False
    if wait_minutes is not None:
        near_breach = wait_minutes >= sla * 0.8 and wait_minutes < sla
        breached = wait_minutes >= sla
    return {
        "sla_minutes": sla,
        "wait_minutes": wait_minutes,
        "near_breach": near_breach,
        "breached": breached,
    }


def _should_escalate_to_ronan(lead: Lead, available_ids: List[str], now: datetime) -> bool:
    if lead.temperatura == "Quente":
        return True
    advanced_stages = {"Negociação", "Matriculado", "Proposta"}
    if lead.etapa in advanced_stages:
        return True
    if (lead.origem or "").lower() in {"parceiro", "indicação", "indicacao"}:
        return True
    if (lead.produto or "").lower() in {"PMERJ", "TJ", "MPF", "Prefeitura", "Concurso"}:
        return True
    if lead.etapa == "Novo" and lead.temperatura == "Frio":
        return False
    return False


def suggest_assignee(db: Session, lead: Lead, now: Optional[datetime] = None) -> Dict[str, Any]:
    now = now or datetime.utcnow()
    attendants = available_attendants(db, now)
    if not attendants:
        raise RuntimeError("Sem atendentes disponíveis para distribuição")

    current = next((a for a in attendants if a["id"] == lead.responsavel_id), None)
    if current and current["in_window"] and current["status"] in {"DISPONÍVEL", "ATENÇÃO"}:
        return {
            "assignee_id": current["id"],
            "assignee_name": current["name"],
            "reason": "Mantém atendente atual",
            "mode": MODE,
        }

    attendants_in_window = [a for a in attendants if a["in_window"] and a["key"] != "ronan"]
    if not lead.responsavel_id and attendants_in_window:
        attendants_in_window.sort(key=lambda a: (a["active"], a["name"]))
        candidate = attendants_in_window[0]
        return {
            "assignee_id": candidate["id"],
            "assignee_name": candidate["name"],
            "reason": f"Round robin inteligente por capacidade disponível: {candidate['name']} tem {candidate['active']} leads",
            "mode": MODE,
        }

    escalation = _should_escalate_to_ronan(lead, [a["id"] for a in attendants_in_window], now)
    if escalation:
        ronan = next((a for a in attendants if a["key"] == "ronan"), None)
        if ronan:
            return {
                "assignee_id": ronan["id"],
                "assignee_name": ronan["name"],
                "reason": "Escalação por temperatura/etapa/complexidade",
                "mode": MODE,
            }

    fallback = next((a for a in attendants if a["in_window"]), None)
    if fallback:
        return {
            "assignee_id": fallback["id"],
            "assignee_name": fallback["name"],
            "reason": f"Fallback para atendente em janela: {fallback['name']}",
            "mode": MODE,
        }

    ronan = next((a for a in attendants if a["key"] == "ronan"), None)
    if ronan:
        return {
            "assignee_id": ronan["id"],
            "assignee_name": ronan["name"],
            "reason": "Fora do horário das atendentes -> Ronan",
            "mode": MODE,
        }

    raise RuntimeError("Sem responsável definido para este lead")


def assign_lead(db: Session, lead_id: str, to_user_id: str, reason: str, from_user_id: Optional[str] = None, actor_user_id: Optional[str] = None) -> Lead:
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise ValueError("Lead não encontrado")
    previous = lead.responsavel_id
    lead.responsavel_id = to_user_id
    lead.updated_by = actor_user_id
    lead.updated_at = datetime.utcnow()
    db.add(lead)
    db.flush()
    db.add(AuditLog(
        user_id=actor_user_id,
        lead_id=lead.id,
        acao="Transferiu lead",
        campo="responsavel_id",
        valor_anterior=previous,
        valor_novo=to_user_id,
    ))
    db.add(Interaction(
        lead_id=lead.id,
        user_id=to_user_id,
        tipo=InteractionType.NOTA.value if hasattr(InteractionType, "NOTA") else "Nota",
        descricao=f"Distribuição automática: {reason}. De {previous} para {to_user_id}.",
    ))
    db.commit()
    db.refresh(lead)
    return lead


def build_queue(db: Session, now: Optional[datetime] = None) -> List[Dict[str, Any]]:
    now = now or datetime.utcnow()
    leads = db.query(Lead).filter(Lead.status == "ativo").order_by(Lead.created_at.asc()).all()
    enriched = []
    for lead in leads:
        sla = _sla_risk(lead, now)
        has_response = db.query(Interaction.id).filter(
            Interaction.lead_id == lead.id,
            Interaction.tipo == InteractionType.WHATSAPP.value if hasattr(InteractionType, "WHATSAPP") else "WhatsApp"
        ).first() is not None
        enriched.append({
            "id": lead.id,
            "name": lead.nome,
            "phone": lead.whatsapp or lead.telefone,
            "temperature": lead.temperatura,
            "etapa": lead.etapa,
            "produto": lead.produto,
            "origem": lead.origem,
            "responsavel_id": lead.responsavel_id,
            "created_at": lead.created_at.isoformat() if lead.created_at else None,
            "updated_at": lead.updated_at.isoformat() if lead.updated_at else None,
            "sla": sla,
            "has_response": has_response,
        })

    def rank(item: Dict[str, Any]) -> tuple:
        temp_rank = _temperature_rank(item["temperature"])
        response_wait = 0 if item["has_response"] else 1
        sla_penalty = 2 if item["sla"]["breached"] else (1 if item["sla"]["near_breach"] else 0)
        return (sla_penalty, temp_rank, response_wait, item["created_at"] or datetime.utcnow().isoformat())

    enriched.sort(key=rank)
    return enriched
