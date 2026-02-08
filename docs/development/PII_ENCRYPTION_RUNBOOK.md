# PII Field-Level Encryption & Key Rotation Runbook

This runbook defines the operational standards for PII encryption and key rotation.

## Scope
- User personal data (names, emails, phone numbers)
- Vendor/customer contact details
- Bank account metadata

## Encryption Policy
1. Use field-level encryption for PII columns.
2. Encrypt at rest and in transit.
3. Store encryption keys in a managed KMS.

## Key Rotation Procedure
1. Generate new data-encryption key (DEK) in KMS.
2. Update application configuration to use new DEK for new writes.
3. Run background re-encryption job for historical records.
4. Validate counts and reconciliation checks.
5. Retire old key after verification window.

## Verification Checklist
- [ ] Rotation executed in staging
- [ ] Key usage logs reviewed
- [ ] Data quality checks passed
- [ ] Audit trail entry created

## Incident Response
If a key compromise is suspected:
1. Rotate keys immediately.
2. Revoke affected tokens/sessions.
3. Notify compliance and security teams.
