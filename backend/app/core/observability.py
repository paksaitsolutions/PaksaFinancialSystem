"""Observability utilities for RED metrics and tracing."""

from __future__ import annotations

import time
import uuid
from collections import defaultdict, deque
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Deque, Dict, Iterable, Optional

TRACE_ID: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)


def set_trace_id(value: Optional[str]) -> None:
    TRACE_ID.set(value)


def get_trace_id() -> Optional[str]:
    return TRACE_ID.get()


def _percentile(values: Iterable[float], percentile: float) -> float:
    sorted_values = sorted(values)
    if not sorted_values:
        return 0.0
    index = int(round((percentile / 100) * (len(sorted_values) - 1)))
    return sorted_values[index]


class MetricsStore:
    def __init__(self) -> None:
        self.requests: Dict[str, Dict[str, object]] = defaultdict(
            lambda: {"count": 0, "errors": 0, "durations": deque(maxlen=1000)}
        )
        self.db: Dict[str, object] = {"count": 0, "durations": deque(maxlen=2000)}
        self.jobs: Dict[str, Dict[str, object]] = defaultdict(
            lambda: {"count": 0, "errors": 0, "durations": deque(maxlen=500)}
        )

    def record_request(self, domain: str, method: str, status_code: int, duration_ms: float) -> None:
        key = f"{domain}:{method.lower()}"
        entry = self.requests[key]
        entry["count"] = int(entry["count"]) + 1
        if status_code >= 400:
            entry["errors"] = int(entry["errors"]) + 1
        durations: Deque[float] = entry["durations"]  # type: ignore[assignment]
        durations.append(duration_ms)

    def record_db_span(self, duration_ms: float) -> None:
        self.db["count"] = int(self.db["count"]) + 1
        durations: Deque[float] = self.db["durations"]  # type: ignore[assignment]
        durations.append(duration_ms)

    def record_job(self, name: str, success: bool, duration_ms: float) -> None:
        entry = self.jobs[name]
        entry["count"] = int(entry["count"]) + 1
        if not success:
            entry["errors"] = int(entry["errors"]) + 1
        durations: Deque[float] = entry["durations"]  # type: ignore[assignment]
        durations.append(duration_ms)

    def snapshot(self) -> Dict[str, object]:
        request_metrics = {}
        for key, entry in self.requests.items():
            durations: Deque[float] = entry["durations"]  # type: ignore[assignment]
            count = int(entry["count"])
            errors = int(entry["errors"])
            request_metrics[key] = {
                "count": count,
                "errors": errors,
                "error_rate": (errors / count) if count else 0.0,
                "avg_ms": (sum(durations) / len(durations)) if durations else 0.0,
                "p95_ms": _percentile(durations, 95),
            }

        db_durations: Deque[float] = self.db["durations"]  # type: ignore[assignment]
        job_metrics = {}
        for name, entry in self.jobs.items():
            durations: Deque[float] = entry["durations"]  # type: ignore[assignment]
            count = int(entry["count"])
            errors = int(entry["errors"])
            job_metrics[name] = {
                "count": count,
                "errors": errors,
                "error_rate": (errors / count) if count else 0.0,
                "avg_ms": (sum(durations) / len(durations)) if durations else 0.0,
                "p95_ms": _percentile(durations, 95),
            }

        return {
            "requests": request_metrics,
            "db": {
                "count": int(self.db["count"]),
                "avg_ms": (sum(db_durations) / len(db_durations)) if db_durations else 0.0,
                "p95_ms": _percentile(db_durations, 95),
            },
            "jobs": job_metrics,
        }


metrics_store = MetricsStore()


def classify_domain(path: str) -> str:
    if path.startswith("/api/v1/auth") or path.startswith("/auth"):
        return "auth"
    if path.startswith("/api/v1/gl"):
        return "gl"
    if path.startswith("/api/v1/ap"):
        return "ap"
    if path.startswith("/api/v1/ar"):
        return "ar"
    if path.startswith("/cash"):
        return "cash"
    if path.startswith("/api/v1/data-integrity"):
        return "data-integrity"
    if path.startswith("/api/v1/security"):
        return "security"
    if path.startswith("/api/v1/compliance"):
        return "compliance"
    if path.startswith("/api/v1/observability"):
        return "observability"
    return "core"


def ensure_trace_id(incoming_trace_id: Optional[str] = None) -> str:
    trace_id = incoming_trace_id or str(uuid.uuid4())
    set_trace_id(trace_id)
    return trace_id


def get_trace_context() -> Dict[str, Optional[str]]:
    return {"trace_id": get_trace_id()}


@contextmanager
def trace_job(name: str):
    start = time.perf_counter()
    success = True

    def mark_failed() -> None:
        nonlocal success
        success = False

    try:
        yield mark_failed
    except Exception:
        success = False
        raise
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        metrics_store.record_job(name, success, duration_ms)
