"""Sales Enablement Agent — tests obrigatórios."""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta

import pytest

from sales_enablement_agent.crm.adapter import CRMAdapter, LeadRecord
from sales_enablement_agent.intelligence.engine import (
    calculate_sales_score,
    evaluate_deal_health,
    generate_next_best_action,
)


@pytest.fixture
def crm(tmp_path):
    adapter = CRMAdapter(base_path=str(tmp_path / "sales-enablement-agent-crm"))
    yield adapter
    # nothing to cleanup explicitly


def make_lead(**overrides):
    lead = {
        "id": overrides.pop("id", "lead-1"),
        "nome": overrides.pop("nome", "Flávio Teste"),
        "empresa": overrides.pop("empresa", "Empresa Teste"),
        "cargo": overrides.pop("cargo", "CEO"),
        "telefone": overrides.pop("telefone", "(21) 99971-9474"),
        "email": overrides.pop("email", "flavio@teste.com"),
        "linkedin": overrides.pop("linkedin", "https://www.linkedin.com/in/flavio"),
        "fonte": overrides.pop("fonte", "LinkedIn"),
        "stage": overrides.pop("stage", None),
        "status": overrides.pop("status", None),
        "sales_score": overrides.pop("sales_score", None),
        "deal_health": overrides.pop("deal_health", None),
        "next_action": overrides.pop("next_action", None),
        "next_action_channel": overrides.pop("next_action_channel", None),
        "next_action_due": overrides.pop("next_action_due", None),
        "last_contact_at": overrides.pop("last_contact_at", None),
        "tags": overrides.pop("tags", []),
        "notes": overrides.pop("notes", []),
        "interactions": overrides.pop("interactions", []),
        "updated_at": overrides.pop("updated_at", None),
    }
    lead.update(overrides)
    return lead


def test_lead_novo_sem_contexto():
    lead = make_lead(nome="", empresa="", cargo="", email="", stage=None)
    score = calculate_sales_score(lead)
    assert 0 <= score.sales_score <= 100
    assert score.missing_fields


def test_lead_sem_contexto_com_id():
    lead = make_lead(nome="Lead Vazio", empresa="", cargo="", email="")
    score = calculate_sales_score(lead)
    assert score.sales_score < 60
    assert score.confidence in {"low", "medium"}


def test_lead_quente():
    lead = make_lead(
        nome="Lead Quente",
        empresa="Empresa Quente",
        cargo="CEO",
        fonte="LinkedIn",
        stage="opportunity",
        last_contact_at=datetime.now(timezone.utc).isoformat(),
        interactions=[{"type": "message"}, {"type": "reply"}],
        needs="precisa reduzir custo oculto",
    )
    score = calculate_sales_score(lead)
    assert score.sales_score >= 40
    assert score.classification in {"OPORTUNIDADE", "ALTA PRIORIDADE", "PRIORIDADE MÁXIMA"}


def test_lead_parado():
    old_date = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
    lead = make_lead(stage="negotiation", last_contact_at=old_date)
    health = evaluate_deal_health(lead)
    assert "parado" in health.health or "AT RISK" in health.health or "CRITICAL" in health.health


def test_lead_com_objeção():
    lead = make_lead(notes=["Está caro para mim."])
    action = generate_next_best_action(lead)
    assert action.action
    assert action.when
    assert action.channel in {"whatsapp", "linkedin", "email", "telegram"}


def test_lead_solicitando_proposta():
    lead = make_lead(stage="discovery", notes=["Me manda uma proposta por e-mail."])
    action = generate_next_best_action(lead)
    assert action.action


def test_lead_pronto_para_reunião():
    lead = make_lead(stage="opportunity", last_contact_at=datetime.now(timezone.utc).isoformat(), interactions=[{"type": "proposal"}])
    action = generate_next_best_action(lead)
    assert action.action
    assert "reunião" in action.action or "case" in action.action or "proposta" in action.action


def test_oportunidade_perdida():
    lead = make_lead(stage="lost")
    action = generate_next_best_action(lead)
    assert "nutrir" in action.action or "manter" in action.action


def test_oportunidade_em_risco():
    old_date = (datetime.now(timezone.utc) - timedelta(days=25)).isoformat()
    lead = make_lead(stage="negotiation", last_contact_at=old_date)
    health = evaluate_deal_health(lead)
    assert health.next_step_urgency == "alta"
    action = generate_next_best_action(lead)
    assert action.priority == "alta"


def test_lead_com_dados_conflitantes():
    lead = make_lead(nome="A", empresa="Empresa A", email="a@a.com", linkedin="https://www.linkedin.com/in/b")
    score = calculate_sales_score(lead)
    assert score.sales_score >= 0
    assert score.missing_fields is not None


def test_crm_e_followup(crm):
    lead = LeadRecord(
        nome="Flávio CRM",
        empresa="Empresa CRM",
        cargo="CEO",
        email="flavio@crm.com",
        stage="new",
        next_action="enviar primeira abordagem",
        next_action_channel="linkedin",
        next_action_due=datetime.now(timezone.utc).isoformat(),
        sales_score=80,
    )
    saved = crm.upsert_lead(lead)
    assert saved.id is not None

    loaded = crm.get_lead(saved.id)
    assert loaded.nome == "Flávio CRM"

    crm.add_interaction(saved.id, {"type": "message", "text": "Olá"})
    loaded = crm.get_lead(saved.id)
    assert len(loaded.interactions) == 1

    pending = crm.pending_followups()
    assert any(item["lead_id"] == saved.id for item in pending)
