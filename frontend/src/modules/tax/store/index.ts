// Tax Module Store
// Central export for all tax-related stores

export * from './policy';
export * from './analytics';
export * from './reporting';
export * from './filing';

// Import and re-export types
export * from '../types';

// Initialize the module stores
import { useTaxPolicyStore } from './policy';
import { useTaxAnalyticsStore } from './analytics';
import { useTaxReportingStore } from './reporting';
import { useTaxFilingStore } from './filing';

export function useTaxModuleStores() {
  return {
    policy: useTaxPolicyStore(),
    analytics: useTaxAnalyticsStore(),
    reporting: useTaxReportingStore(),
    filing: useTaxFilingStore(),
  };
}

export type TaxModuleStores = ReturnType<typeof useTaxModuleStores>;
