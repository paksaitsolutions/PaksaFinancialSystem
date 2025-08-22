import type { JournalEntry } from './journalEntry';

/**
 * Frequency options for recurring journal entries
 */
export type RecurrenceFrequency =
  | 'daily'
  | 'weekly'
  | 'biweekly'
  | 'monthly'
  | 'quarterly'
  | 'semi_annually'
  | 'annually'
  | 'custom';

/**
 * Options for when a recurring journal should end
 */
export type RecurrenceEndType = 'never' | 'after_occurrences' | 'on_date';

/**
 * Status of a recurring journal entry
 */
export type RecurringJournalStatus = 'active' | 'paused' | 'completed' | 'cancelled';

/**
 * Base interface for recurring journal entries
 */
export interface RecurringJournalBase {
  id: string;
  name: string;
  description: string | null;
  frequency: RecurrenceFrequency;
  interval: number;
  start_date: string; // ISO date string
  end_type: RecurrenceEndType;
  end_after_occurrences: number | null;
  end_date: string | null; // ISO date string
  status: RecurringJournalStatus;
  last_run_date: string | null; // ISO date string
  next_run_date: string | null; // ISO date string
  total_occurrences: number;
  company_id: string;
  created_by: string;
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
  deleted_at: string | null; // ISO date string
}

/**
 * Recurring journal entry with template data
 */
export interface RecurringJournal extends RecurringJournalBase {
  template: RecurringJournalTemplate;
}

/**
 * Data needed to create a new recurring journal entry
 */
export interface RecurringJournalCreate {
  name: string;
  description?: string | null;
  frequency: RecurrenceFrequency;
  interval?: number;
  start_date: string; // ISO date string
  end_type: RecurrenceEndType;
  end_after_occurrences?: number | null;
  end_date?: string | null; // ISO date string
  template: Omit<RecurringJournalTemplate, 'id' | 'created_at' | 'updated_at'>;
  company_id: string;
}

/**
 * Data needed to update an existing recurring journal entry
 */
export interface RecurringJournalUpdate {
  name?: string;
  description?: string | null;
  frequency?: RecurrenceFrequency;
  interval?: number;
  start_date?: string; // ISO date string
  end_type?: RecurrenceEndType;
  end_after_occurrences?: number | null;
  end_date?: string | null; // ISO date string
  status?: RecurringJournalStatus;
  next_run_date?: string | null; // ISO date string
  template?: Partial<Omit<RecurringJournalTemplate, 'id' | 'created_at' | 'updated_at'>>;
}

/**
 * Template data for a recurring journal entry
 */
export interface RecurringJournalTemplate {
  id: string;
  recurring_journal_id: string;
  // This is a JSONB field that contains the journal entry template data
  // It should match the structure expected by the journal entry API
  template_data: {
    journal_date: string; // ISO date string
    reference?: string;
    reference_date?: string; // ISO date string
    memo?: string;
    currency: string;
    exchange_rate?: number;
    company_id: string;
    entries: Array<{
      account_id: string;
      description?: string;
      debit: number;
      credit: number;
      tax_code_id?: string | null;
      department_id?: string | null;
      project_id?: string | null;
      cost_center_id?: string | null;
      custom_fields?: Record<string, any>;
    }>;
    attachments?: Array<{
      name: string;
      url: string;
      mime_type: string;
      size: number;
    }>;
    custom_fields?: Record<string, any>;
  };
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
}

/**
 * Parameters for listing recurring journal entries
 */
export interface RecurringJournalListParams {
  page?: number;
  per_page?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  status?: RecurringJournalStatus | RecurringJournalStatus[];
  company_id?: string;
  created_by?: string;
  start_date_from?: string; // ISO date string
  start_date_to?: string; // ISO date string
  next_run_from?: string; // ISO date string
  next_run_to?: string; // ISO date string
  search?: string;
}

/**
 * Response when listing recurring journal entries
 */
export interface RecurringJournalListResponse {
  data: RecurringJournal[];
  pagination: {
    total: number;
    page: number;
    per_page: number;
    total_pages: number;
  };
}

/**
 * Preview of a recurring journal's next occurrences
 */
export interface RecurringJournalPreview {
  occurrences: Array<{
    date: string; // ISO date string
    is_weekend: boolean;
    is_holiday: boolean;
  }>;
  total_occurrences: number;
  end_date: string | null; // ISO date string
}

/**
 * Parameters for running a recurring journal entry
 */
export interface RecurringJournalRunParams {
  run_date?: string; // ISO date string
  post_journal?: boolean;
  notify_on_completion?: boolean;
  notification_emails?: string[];
  dry_run?: boolean;
}

/**
 * Response from running a recurring journal entry
 */
export interface RecurringJournalRunResponse {
  success: boolean;
  message: string;
  journal_entries?: Array<{
    id: string;
    number: string;
    status: string;
    posted_at: string | null; // ISO date string
  }>;
  errors?: Array<{
    date: string; // ISO date string
    error: string;
  }>;
  dry_run: boolean;
  run_id: string;
  run_at: string; // ISO date string
}

/**
 * A past occurrence of a recurring journal entry
 */
export interface RecurringJournalOccurrence {
  id: string;
  recurring_journal_id: string;
  scheduled_date: string; // ISO date string
  run_date: string | null; // ISO date string
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'skipped';
  error_message: string | null;
  created_journal_entries: string[];
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
  run_id: string | null;
}

/**
 * Statistics about recurring journal entries
 */
export interface RecurringJournalStats {
  active: number;
  paused: number;
  completed: number;
  cancelled: number;
  next_run: string | null; // ISO date string
  last_run: string | null; // ISO date string
  total_occurrences: number;
  total_journal_entries: number;
  by_frequency: Record<RecurrenceFrequency, number>;
  by_status: Record<RecurringJournalStatus, number>;
  upcoming_occurrences: Array<{
    id: string;
    name: string;
    next_run_date: string; // ISO date string
    frequency: RecurrenceFrequency;
  }>;
  recent_activity: Array<{
    id: string;
    name: string;
    status: RecurringJournalStatus;
    last_run_date: string | null; // ISO date string
    next_run_date: string | null; // ISO date string
  }>;
}
