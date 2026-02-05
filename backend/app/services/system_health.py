"""System health utilities for production-grade observability."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import engine


def _utc_now() -> str:
    return datetime.utcnow().isoformat()


def get_liveness_payload() -> Dict[str, Any]:
    """Return liveness information without hitting external dependencies."""
    return {
        "status": "alive",
        "service": "paksa-financial-system",
        "timestamp": _utc_now(),
        "version": os.getenv("APP_VERSION", "1.0.0"),
    }


def get_readiness_payload() -> Dict[str, Any]:
    """Return readiness state with dependency checks.

    Database connectivity is validated with a simple query to support
    orchestrator-ready probes (Kubernetes, ECS, etc.).
    """
    db_status = "disconnected"
    details: Dict[str, Any] = {}

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            db_status = "connected"
    except SQLAlchemyError as exc:
        details["database_error"] = str(exc)

    ready = db_status == "connected"
    return {
        "status": "ready" if ready else "degraded",
        "service": "paksa-financial-system",
        "timestamp": _utc_now(),
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "checks": {
            "database": db_status,
        },
        "details": details,
    }

