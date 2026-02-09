# Service Level Objectives (SLOs)

This document defines the alerting targets used by Paksa Financial System for core financial workflows. These SLOs are backed by RED metrics and reconciliation job telemetry exposed via `/api/v1/observability/*`.

## Auth Reliability
- **Metric**: Auth request error rate (4xx/5xx) across `/api/v1/auth/*` and `/auth/*`
- **Target**: ≤ 1% error rate over a 30-minute rolling window
- **Alert**: `auth_error_rate > 0.01` for 15 minutes
- **Runbook**: [Auth Outage](runbooks/auth-outage.md)

## Posting Latency (GL/AP/AR)
- **Metric**: P95 latency for posting endpoints
  - `/api/v1/gl/journal-entries`
  - `/api/v1/ap/payments`
  - `/api/v1/ar/payments`
- **Target**: P95 ≤ 2000ms over a 1-hour rolling window
- **Alert**: `posting_latency_p95_ms > 2000` for 20 minutes
- **Runbook**: [Posting Drift](runbooks/posting-drift.md)

## Reconciliation Failures
- **Metric**: Reconciliation job failure rate (scheduled or manual)
- **Target**: ≤ 5% failed runs over 24 hours
- **Alert**: `reconciliation_failure_rate > 0.05` for 2 hours
- **Runbook**: [Posting Drift](runbooks/posting-drift.md)

## DB Saturation
- **Metric**: DB query P95 latency + connection pool exhaustion
- **Target**: P95 DB span ≤ 250ms, pool timeouts = 0
- **Alert**: DB P95 > 250ms for 20 minutes or pool timeouts > 0
- **Runbook**: [DB Saturation](runbooks/db-saturation.md)
