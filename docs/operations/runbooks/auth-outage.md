# Runbook: Auth Outage

**Trigger:** Auth SLO breach, login failures, or elevated `auth_error_rate`.

## Impact
- Users cannot log in or refresh sessions.
- API calls with expired access tokens fail.

## Immediate Checks
1. **Confirm scope**: Review `/api/v1/observability/slo-status` for `auth_error_rate`.
2. **Health endpoints**: Check `/health/ready` and `/health/live`.
3. **Recent deploys**: Inspect the latest release and configuration changes.

## Mitigation Steps
1. **Scale API pods** if CPU or memory saturation is observed.
2. **Restart auth workers** if token signing or verification is failing.
3. **Verify secrets**: ensure `SECRET_KEY`, token expiry, and encryption keys are unchanged.
4. **Roll back** the latest release if regression is confirmed.

## Validation
- Auth error rate returns to ≤ 1%.
- Login and refresh flows succeed in staging and production.

## Follow-up
- Record the incident and timeline.
- Add regression tests for the identified failure mode.
