// General Ledger Module Store
// Central export for all general ledger related stores

// Import store types first to avoid circular dependencies
import type { GlAccount } from './gl-accounts';
import type { ReportMetadata } from '../services/gl-reporting.service';
import type { ScheduledReport } from './gl-reporting';

// Export all stores (excluding recurring to avoid conflicts)
export * from './gl-accounts';
export * from './gl-account';
export * from './journal-entries';
export * from './gl-analytics';
export * from './gl-reporting';

// Explicitly export from recurring with a different name to avoid conflicts
import { 
  useRecurringJournalStore as useLegacyRecurringJournalStore,
  type RecurringJournalStore as LegacyRecurringJournalStore 
} from './recurring';

export { useLegacyRecurringJournalStore, type LegacyRecurringJournalStore };

// Export the new recurring journal store
export { 
  useRecurringJournalStore,
  type RecurringJournalStore 
} from './recurring-journal';

// Export types
export type { GlAccount, GlAccountState, ReportMetadata, ScheduledReport };

// Import store instances
import { useGlAccountsStore } from './gl-accounts';
import { useGlAccountStore } from './gl-account';
import { useJournalEntriesStore } from './journal-entries';
import { useGlAnalyticsStore } from './gl-analytics';
import { useGlReportingStore } from './gl-reporting';
import { useRecurringJournalStore } from './recurring-journal';

// Define the module stores interface
interface GlModuleStores {
  accounts: ReturnType<typeof useGlAccountsStore>;
  glAccount: ReturnType<typeof useGlAccountStore>;
  journalEntries: ReturnType<typeof useJournalEntriesStore>;
  legacyRecurringJournals: ReturnType<typeof useLegacyRecurringJournalStore>;
  analytics: ReturnType<typeof useGlAnalyticsStore>;
  reporting: ReturnType<typeof useGlReportingStore>;
  recurringJournal: ReturnType<typeof useRecurringJournalStore>;
}

/**
 * Composable function to access all GL module stores
 * @returns Object containing all GL module stores
 */
export function useGlModuleStores(): GlModuleStores {
  return {
    accounts: useGlAccountsStore(),
    glAccount: useGlAccountStore(),
    journalEntries: useJournalEntriesStore(),
    legacyRecurringJournals: useLegacyRecurringJournalStore(),
    analytics: useGlAnalyticsStore(),
    reporting: useGlReportingStore(),
    recurringJournal: useRecurringJournalStore(),
  };
}

// Export the module stores type
export type { GlModuleStores };
