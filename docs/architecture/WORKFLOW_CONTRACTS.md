# End-to-End Financial Workflow Contracts

This document defines the canonical enterprise contract for Quote → Order → Invoice → Payment → GL Posting and establishes cross-module integration expectations.

---

## 1) Canonical Workflow (Quote → Order → Invoice → Payment → GL Posting)

### Common Contract Fields
| Field | Description | Example |
| --- | --- | --- |
| `workflow_id` | Cross-module correlation identifier | `wf_2026_02_01_000123` |
| `source_module` | Origin system | `sales`, `procurement`, `ar`, `ap` |
| `reference_number` | External ID or document number | `SO-000124` |
| `company_id` | Tenant/company identifier | `uuid` |
| `currency` | ISO currency code | `USD` |
| `amount` | Total monetary value | `12500.00` |
| `status` | State | `draft`, `approved`, `posted` |

### State Transitions
1. **Quote** → **Order**: Approved quote creates sales/procurement order.
2. **Order** → **Invoice**: Fulfillment triggers invoice issuance.
3. **Invoice** → **Payment**: Payments settle invoices.
4. **Payment** → **GL Posting**: Every payment and invoice posts journal entries.

---

## 2) Idempotency Requirements (Posting/Payment Endpoints)

All POST endpoints that create financial events must accept the `Idempotency-Key` header.

**Contract**:
```
Idempotency-Key: <uuid-or-client-generated-key>
```

If the same `Idempotency-Key` is replayed:
- **Same payload**: return the original response (safe retry).
- **Different payload**: return `409 Conflict` to prevent data drift.

---

## 3) Compensating Transaction Patterns

When a downstream posting fails:
- Record a compensating action (reversal or offset).
- Emit an audit event.
- Mark the workflow record as `requires_attention`.

**Examples**:
- Payment created but GL posting failed → create a reversal journal entry stub and flag the payment.
- Invoice posted but AR ledger failed → create a compensating AR adjustment.

---

## 4) Audit Event Schema for All State Transitions

Every state transition emits an audit event with:
| Field | Description |
| --- | --- |
| `entity_type` | `ap_payment`, `ar_payment`, `gl_journal_entry`, etc. |
| `entity_id` | Identifier |
| `event_type` | `created`, `approved`, `posted`, `reversed` |
| `actor_id` | User or system actor |
| `metadata` | JSON context: workflow id, document refs |

---

## 5) Frontend/Backend Integration Expectations

- Frontend must attach `Idempotency-Key` for any create/payment/post action.
- Backend guarantees idempotent behavior and emits audit events.
- Workflow status and audit trails are surfaced in UI for compliance.

