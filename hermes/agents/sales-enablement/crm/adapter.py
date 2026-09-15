"""Sales Enablement Agent — CRM integration.

Regras:
- Nunca inventar dados.
- Ler do CRM existente quando disponível.
- Atualizar apenas campos permitidos.
- Sempre registrar origem e timestamp.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class LeadRecord:
    id: Optional[str] = None
    nome: Optional[str] = None
    empresa: Optional[str] = None
    cargo: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    linkedin: Optional[str] = None
    fonte: Optional[str] = None
    stage: Optional[str] = None
    status: Optional[str] = None
    sales_score: Optional[int] = None
    deal_health: Optional[str] = None
    next_action: Optional[str] = None
    next_action_channel: Optional[str] = None
    next_action_due: Optional[str] = None
    last_contact_at: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    interactions: List[Dict[str, Any]] = field(default_factory=list)
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CRMAdapter:
    def __init__(self, base_path: str = "/Users/mac/HermesWorkspace/sales-enablement-agent/crm"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.state_file = self.base_path / "state.json"
        self.export_dir = self.base_path / "exports"
        self.export_dir.mkdir(parents=True, exist_ok=True)
        self._state: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if self.state_file.exists():
            try:
                self._state = json.loads(self.state_file.read_text(encoding="utf-8"))
            except Exception:
                self._state = {}

    def _save(self) -> None:
        self.state_file.write_text(json.dumps(self._state, ensure_ascii=False, indent=2), encoding="utf-8")

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def upsert_lead(self, lead: LeadRecord) -> LeadRecord:
        key = lead.id or lead.email or lead.linkedin or lead.nome or ""
        if not key:
            raise ValueError("lead id/email/linkedin/nome obrigatório para upsert")

        existing = self._state.get(key, {})
        data = existing.copy()
        payload = lead.to_dict()
        payload.pop("id", None)
        payload.pop("updated_at", None)
        data.update({k: v for k, v in payload.items() if v is not None and v != "" and v != []})
        data["updated_at"] = self._now()
        data["id"] = existing.get("id") or key
        self._state[key] = data
        self._save()

        lead.id = data["id"]
        lead.updated_at = data["updated_at"]
        return lead

    def get_lead(self, lead_id: str) -> Optional[LeadRecord]:
        data = self._state.get(lead_id)
        if not data:
            return None
        return LeadRecord(**data)

    def add_interaction(self, lead_id: str, interaction: Dict[str, Any]) -> None:
        lead = self._state.get(lead_id)
        if not lead:
            raise KeyError(f"lead {lead_id} não encontrado")
        interactions = lead.get("interactions", [])
        interaction["timestamp"] = interaction.get("timestamp") or self._now()
        interactions.append(interaction)
        lead["interactions"] = interactions
        lead["updated_at"] = self._now()
        self._save()

    def search(self, query: str) -> List[LeadRecord]:
        query = query.lower()
        results: List[LeadRecord] = []
        for key, data in self._state.items():
            blob = json.dumps(data, ensure_ascii=False).lower()
            if query in blob or query in key.lower():
                results.append(LeadRecord(**data))
        return results

    def export_csv(self, filename: str = "sales_enablement_export.csv") -> Path:
        import csv

        path = self.export_dir / filename
        rows: List[Dict[str, Any]] = []
        all_keys: List[str] = []
        for data in self._state.values():
            row = data.copy()
            row["tags"] = ";".join(row.get("tags", []))
            row["notes"] = " | ".join(row.get("notes", []))
            row["interactions"] = json.dumps(row.get("interactions", []), ensure_ascii=False)
            for k in row.keys():
                if k not in all_keys:
                    all_keys.append(k)
            rows.append(row)

        if rows:
            with path.open("w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=all_keys, extrasaction="ignore")
                writer.writeheader()
                for row in rows:
                    normalized = {k: row.get(k, "") for k in all_keys}
                    writer.writerow(normalized)
        return path

    def pending_followups(self) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        pending: List[Dict[str, Any]] = []
        for key, data in self._state.items():
            due = data.get("next_action_due")
            next_action = data.get("next_action")
            if due and next_action:
                try:
                    due_dt = datetime.fromisoformat(due.replace("Z", "+00:00"))
                    if due_dt <= now:
                        pending.append({
                            "lead_id": key,
                            "nome": data.get("nome"),
                            "next_action": next_action,
                            "channel": data.get("next_action_channel"),
                            "due": due,
                            "deal_health": data.get("deal_health"),
                            "sales_score": data.get("sales_score"),
                        })
                except Exception:
                    continue
        pending.sort(key=lambda item: -(item.get("sales_score") or 0))
        return pending
