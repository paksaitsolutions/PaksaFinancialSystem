# Testing Gates (PR Quality Requirements)

The following checks must pass before merging a change:

## 1) Unit Tests
```bash
cd frontend
npm run test:run
```

## 2) Backend Integration Suite
```bash
PYTHONPATH=backend pytest backend/tests/integration -q
```

## 3) Contract Tests
```bash
PYTHONPATH=backend pytest backend/tests/contract/test_api_contracts.py -q
```

## 4) E2E Smoke Suite (Frontend)
```bash
cd frontend
npm run e2e -- --grep Smoke
```

## 5) Backend E2E Financial Scenarios
```bash
PYTHONPATH=backend pytest backend/tests/e2e/test_financial_scenarios.py -q
```

### Notes
- The smoke suite requires a running frontend dev server at `http://localhost:3003`.
- The backend integration suite uses seeded SQLite fixtures and can run locally or in CI.
