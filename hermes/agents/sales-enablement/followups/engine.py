"""Follow-up engine."""

from __future__ import annotations

from typing import Any, Dict, List

from sales_enablement_agent.crm.adapter import CRMAdapter


def build_followup_list(crm: CRMAdapter, limit: int = 10) -> List[Dict[str, Any]]:
    pending = crm.pending_followups()
    if not pending:
        return []
    return pending[:limit]


def mark_followup_done(crm: CRMAdapter, lead_id: str, note: str = "") -> None:
    lead = crm.get_lead(lead_id)
    if not lead:
        raise KeyError(f"lead {lead_id} não encontrado")
    lead.next_action_due = None
    if note:
        lead.notes.append(note)
    crm.upsert_lead(lead)
