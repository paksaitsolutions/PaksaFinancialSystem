"""Audit event utilities for state transition logging."""

from __future__ import annotations

import json
from enum import Enum
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.core_models import AuditEvent


class AuditAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    POST = "post"
    REVERSE = "reverse"


class AuditLogger:
    def __init__(self, db: Session) -> None:
        self.db = db

    def log(
        self,
        action: AuditAction,
        resource_type: str,
        resource_id: str | None = None,
        user_id: str | None = None,
        company_id: str | None = None,
        tenant_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        log_audit_event(
            db=self.db,
            entity_type=resource_type,
            entity_id=resource_id or "-",
            event_type=action.value,
            actor_id=user_id,
            metadata={"company_id": company_id, "tenant_id": tenant_id, **kwargs},
        )


def log_audit_event(
    db: Session,
    entity_type: str,
    entity_id: str,
    event_type: str,
    actor_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    event = AuditEvent(
        entity_type=entity_type,
        entity_id=entity_id,
        event_type=event_type,
        actor_id=actor_id,
        metadata_json=json.dumps(metadata or {}, default=str),
    )
    db.add(event)
    db.commit()
