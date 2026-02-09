"""Idempotency utilities for safe retry behavior on posting endpoints."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.core_models import IdempotencyKey


def _hash_payload(payload: Dict[str, Any]) -> str:
    normalized = json.dumps(payload or {}, sort_keys=True, default=str)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def get_idempotency_response(
    db: Session,
    key: str,
    endpoint: str,
    payload: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Return stored response if the idempotency key already exists."""
    record = db.query(IdempotencyKey).filter(IdempotencyKey.key == key).first()
    if not record:
        return None

    request_hash = _hash_payload(payload)
    if record.request_hash != request_hash or record.endpoint != endpoint:
        raise ValueError("Idempotency key reuse detected with different payload.")

    return {
        "status_code": record.status_code,
        "body": json.loads(record.response_body) if record.response_body else {},
    }


def save_idempotency_response(
    db: Session,
    key: str,
    endpoint: str,
    payload: Dict[str, Any],
    response_body: Dict[str, Any],
    status_code: int = 200,
) -> None:
    """Persist response for a given idempotency key."""
    record = IdempotencyKey(
        key=key,
        endpoint=endpoint,
        request_hash=_hash_payload(payload),
        response_body=json.dumps(response_body, default=str),
        status_code=status_code,
    )
    db.add(record)
    db.commit()
