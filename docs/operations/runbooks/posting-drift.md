# Runbook: Posting Drift / Reconciliation Failures

**Trigger:** Posting latency SLO breach or reconciliation failure rate > 5%.

## Impact
- AP/AR/GL postings may be delayed or inconsistent.
- Reconciliation dashboards show drift or stale balances.

## Immediate Checks
1. **Confirm SLO breach** via `/api/v1/observability/slo-status`.
2. **Review reconciliation output** via `/api/v1/data-integrity/reconciliation`.
3. **Inspect DB health** for slow queries or blocking locks.

## Mitigation Steps
1. **Pause heavy batch jobs** (imports, bulk postings) if latency spikes.
2. **Re-run reconciliation** after load stabilizes.
3. **Identify slow endpoints** using `/api/v1/observability/metrics`.
4. **Evaluate compensating actions** for partial failures.

## Validation
- Posting latency P95 returns to ≤ 2000ms.
- Reconciliation failure rate returns to ≤ 5%.

## Follow-up
- Add targeted tests for the drift cause.
- Consider sharding or indexing hot tables.
