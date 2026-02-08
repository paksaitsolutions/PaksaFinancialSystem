# Migration Guardrails (Forward-Only + Rollback Playbooks)

This guide defines the enterprise migration policy for Paksa Financial System.

## Principles
1. **Forward-only migrations**: schema changes must be additive whenever possible.
2. **Deterministic rollbacks**: every release includes a rollback playbook.
3. **Data safety**: never drop columns without at least one release of deprecation.

## Required Checklist (Per Release)
- [ ] Migration reviewed by DB owner
- [ ] Forward migration validated in staging
- [ ] Rollback steps documented and tested
- [ ] Data backfill/reconciliation plan attached
- [ ] Index impact reviewed

## Rollback Playbook Template
1. Freeze writes to affected services
2. Snapshot database
3. Run rollback migration scripts
4. Verify reconciliation checks
5. Resume writes

## Forward-Only Example
- Step 1: Add new column (nullable)
- Step 2: Backfill data via script
- Step 3: Update application to use new column
- Step 4: Enforce NOT NULL in a later release
