"""Service helpers for alerting SLO evaluation."""

from __future__ import annotations

from typing import Dict

from app.core.observability import metrics_store


def _aggregate_error_rate(metrics: Dict[str, Dict[str, float]], prefix: str) -> float:
    counts = 0
    errors = 0
    for key, entry in metrics.items():
        if key.startswith(prefix):
            counts += int(entry["count"])
            errors += int(entry["errors"])
    return (errors / counts) if counts else 0.0


def get_slo_status() -> Dict[str, Dict[str, object]]:
    snapshot = metrics_store.snapshot()
    request_metrics = snapshot["requests"]
    job_metrics = snapshot["jobs"]

    auth_error_rate = _aggregate_error_rate(request_metrics, "auth:")

    posting_p95 = max(
        request_metrics.get("gl:post", {}).get("p95_ms", 0.0),
        request_metrics.get("ap:post", {}).get("p95_ms", 0.0),
        request_metrics.get("ar:post", {}).get("p95_ms", 0.0),
    )

    reconciliation_error_rate = job_metrics.get("reconciliation", {}).get("error_rate", 0.0)

    return {
        "auth_error_rate": {
            "value": auth_error_rate,
            "target": 0.01,
            "status": "ok" if auth_error_rate <= 0.01 else "breach",
        },
        "posting_latency_p95_ms": {
            "value": posting_p95,
            "target": 2000,
            "status": "ok" if posting_p95 <= 2000 else "breach",
        },
        "reconciliation_failure_rate": {
            "value": reconciliation_error_rate,
            "target": 0.05,
            "status": "ok" if reconciliation_error_rate <= 0.05 else "breach",
        },
    }
