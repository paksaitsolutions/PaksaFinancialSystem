"""Compensating transaction utilities."""

from __future__ import annotations

import json
from typing import Any, Dict

from sqlalchemy.orm import Session

from app.models.core_models import CompensationAction


def record_compensation(
    db: Session,
    entity_type: str,
    entity_id: str,
    reason: str,
    payload: Dict[str, Any],
    status: str = "pending",
) -> None:
    action = CompensationAction(
        entity_type=entity_type,
        entity_id=entity_id,
        reason=reason,
        status=status,
        payload=json.dumps(payload, default=str),
    )
    db.add(action)
    db.commit()
