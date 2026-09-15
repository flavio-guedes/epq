"""Analytics helpers."""

from __future__ import annotations

from typing import Any, Dict, List

from sales_enablement_agent.crm.adapter import CRMAdapter


def pipeline_summary(crm: CRMAdapter) -> Dict[str, Any]:
    stages: Dict[str, int] = {}
    for data in crm._state.values():
        stage = data.get("stage") or data.get("status") or "unknown"
        stages[stage] = stages.get(stage, 0) + 1
    return {"total_leads": len(crm._state), "stages": stages}


def conversion_metrics(crm: CRMAdapter) -> Dict[str, Any]:
    won = sum(1 for data in crm._state.values() if (data.get("stage") or data.get("status") or "").lower() == "won")
    total = len(crm._state) or 1
    return {"win_rate": round(won / total, 4), "won": won, "total": total}


def what_to_do_now(crm: CRMAdapter, max_items: int = 10) -> List[Dict[str, Any]]:
    hot = [
        {
            "lead_id": key,
            "nome": data.get("nome"),
            "sales_score": data.get("sales_score"),
            "next_action": data.get("next_action"),
            "channel": data.get("next_action_channel"),
            "deal_health": data.get("deal_health"),
        }
        for key, data in crm._state.items()
        if (data.get("sales_score") or 0) >= 60
    ]
    hot.sort(key=lambda item: -(item.get("sales_score") or 0))
    return hot[:max_items]
