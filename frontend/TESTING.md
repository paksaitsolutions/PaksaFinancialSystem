# Frontend Testing Guide

## Overview
Comprehensive testing setup for Paksa Financial System frontend using Vitest for unit/integration tests and Playwright for E2E tests.

## Test Structure
```
frontend/
├── src/
│   ├── components/test/
│   │   ├── setup.ts          # Test setup and mocks
│   │   └── utils.ts          # Test utilities
│   ├── **/*.spec.ts          # Component unit tests
│   ├── stores/*.spec.ts      # Store tests
│   └── composables/*.spec.ts # Composable tests
├── e2e/
│   ├── auth.spec.ts          # Authentication E2E tests
│   ├── ap-workflow.spec.ts   # AP workflow tests
│   └── ar-workflow.spec.ts   # AR workflow tests
├── vitest.config.ts          # Vitest configuration
└── playwright.config.ts      # Playwright configuration
```

## Running Tests

### Unit Tests (Vitest)
```bash
# Run all tests
npm run test

# Run tests in watch mode
npm run test:ui

# Run tests once
npm run test:run

# Generate coverage report
npm run test:coverage
```

### E2E Tests (Playwright)
```bash
# Run E2E tests
npm run e2e

# Run with UI
npm run e2e:ui

# Run in headed mode
npm run e2e:headed
```

## Test Categories

### 1. Component Unit Tests
- **Location**: `src/**/*.spec.ts`
- **Purpose**: Test individual Vue components
- **Examples**: APDashboard.spec.ts, AccountsReceivableView.spec.ts

### 2. Store Tests
- **Location**: `src/stores/*.spec.ts`
- **Purpose**: Test Pinia store logic
- **Examples**: auth.spec.ts

### 3. Composable Tests
- **Location**: `src/composables/*.spec.ts`
- **Purpose**: Test Vue composables
- **Examples**: useApi.spec.ts

### 4. E2E Tests
- **Location**: `e2e/*.spec.ts`
- **Purpose**: Test complete user workflows
- **Examples**: auth.spec.ts, ap-workflow.spec.ts

## Test Utilities

### createTestWrapper()
Helper function for mounting Vue components with proper setup:
```typescript
import { createTestWrapper } from '@/components/test/utils'

const wrapper = createTestWrapper(MyComponent, {
  props: { prop1: 'value' }
})
```

### Mock API Responses
```typescript
import { mockApiResponse, mockApiError } from '@/components/test/utils'

vi.mocked(apiCall).mockResolvedValue(mockApiResponse(data))
vi.mocked(apiCall).mockRejectedValue(mockApiError('Error message'))
```

## Coverage Targets
- **Unit Tests**: 80% coverage
- **Critical Components**: 90% coverage
- **Stores**: 95% coverage
- **Composables**: 85% coverage

## Best Practices

### Unit Tests
1. Test component behavior, not implementation
2. Mock external dependencies
3. Use data-testid attributes for element selection
4. Test error states and edge cases

### E2E Tests
1. Test complete user workflows
2. Use realistic test data
3. Clean up test data after tests
4. Test across different browsers

### Mocking
1. Mock API calls consistently
2. Mock external libraries (PrimeVue, etc.)
3. Use vi.mock() for module mocking
4. Clear mocks between tests

## CI/CD Integration
Tests run automatically on:
- Pull requests
- Main branch commits
- Release builds

## Debugging Tests
1. Use `test.only()` to run single tests
2. Add `console.log()` for debugging
3. Use Playwright's trace viewer for E2E debugging
4. Check coverage reports for missed cases