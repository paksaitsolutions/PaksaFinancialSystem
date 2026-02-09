# Runbook: DB Saturation

**Trigger:** Elevated DB P95 latency or connection pool exhaustion.

## Impact
- API response times degrade across all domains.
- Timeouts or 500 responses during posting or reconciliation.

## Immediate Checks
1. **DB latency** from `/api/v1/observability/metrics` (db P95).
2. **Connection pool** utilization and timeouts.
3. **Active queries** and locks in the DB.

## Mitigation Steps
1. **Scale DB resources** (CPU/IOPS) or add read replicas.
2. **Throttle batch workloads** and heavy reporting exports.
3. **Terminate long-running queries** if safe.
4. **Enable query caching** for read-heavy endpoints.

## Validation
- DB P95 returns to ≤ 250ms.
- Connection pool timeouts = 0.

## Follow-up
- Add indexes for hot paths.
- Adjust pooling configuration.
