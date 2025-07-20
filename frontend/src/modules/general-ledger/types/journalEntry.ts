/**
 * Type of journal entry line (debit or credit)
 */
export type JournalEntryType = 'debit' | 'credit';

/**
 * Journal entry line item
 */
export interface JournalEntryItem {
  id?: string;
  account_id: string;
  type: JournalEntryType;
  amount: number;
  description?: string;
  currency?: string;
  exchange_rate?: number;
  cost_center_id?: string | null;
  project_id?: string | null;
  tax_code?: string | null;
  tax_amount?: number;
  allocation_id?: string | null;
  metadata?: Record<string, any>;
}

/**
 * Journal entry status
 */
export type JournalEntryStatus = 
  | 'draft'
  | 'posted'
  | 'void'
  | 'reversed'
  | 'approved'
  | 'rejected';

/**
 * Base journal entry interface
 */
export interface JournalEntryBase {
  id: string;
  journal_number: string;
  reference?: string;
  memo?: string;
  journal_date: string; // ISO date string
  posted_date: string | null; // ISO date string
  status: JournalEntryStatus;
  currency: string;
  exchange_rate: number;
  company_id: string;
  created_by: string;
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
  deleted_at: string | null; // ISO date string
}

/**
 * Journal entry with line items
 */
export interface JournalEntry extends JournalEntryBase {
  items: JournalEntryItem[];
}

/**
 * Data needed to create a new journal entry
 */
export interface JournalEntryCreate {
  journal_date: string; // ISO date string
  reference?: string;
  memo?: string;
  currency: string;
  exchange_rate?: number;
  items: Omit<JournalEntryItem, 'id'>[];
  company_id: string;
  post?: boolean; // Whether to post the journal entry immediately
}

/**
 * Data needed to update an existing journal entry
 */
export interface JournalEntryUpdate {
  journal_date?: string; // ISO date string
  reference?: string;
  memo?: string;
  currency?: string;
  exchange_rate?: number;
  items?: Omit<JournalEntryItem, 'id'>[];
  status?: JournalEntryStatus;
  post?: boolean; // Whether to post the journal entry
  force?: boolean; // Whether to force update if already posted
}

/**
 * Parameters for listing journal entries
 */
export interface JournalEntryListParams {
  page?: number;
  per_page?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  status?: JournalEntryStatus | JournalEntryStatus[];
  company_id?: string;
  created_by?: string;
  start_date?: string; // ISO date string
  end_date?: string; // ISO date string
  account_id?: string;
  reference?: string;
  search?: string;
  include_items?: boolean;
}

/**
 * Response when listing journal entries
 */
export interface JournalEntryListResponse {
  data: JournalEntry[];
  pagination: {
    total: number;
    page: number;
    per_page: number;
    total_pages: number;
  };
}

/**
 * Response when posting a journal entry
 */
export interface JournalEntryPostResponse {
  success: boolean;
  message: string;
  journal_entry: JournalEntry;
}

/**
 * Response when voiding a journal entry
 */
export interface JournalEntryVoidResponse {
  success: boolean;
  message: string;
  reversal_entry: JournalEntry | null;
}

/**
 * Response when getting journal entry statistics
 */
export interface JournalEntryStats {
  total_entries: number;
  total_amount: number;
  total_debits: number;
  total_credits: number;
  by_status: Record<JournalEntryStatus, number>;
  by_month: Array<{
    month: string; // YYYY-MM
    count: number;
    total_amount: number;
  }>;
  by_account: Array<{
    account_id: string;
    account_name: string;
    account_code: string;
    total_debit: number;
    total_credit: number;
    net_amount: number;
  }>;
}

/**
 * Request for importing journal entries
 */
export interface JournalEntryImportRequest {
  entries: Array<{
    journal_date: string; // ISO date string
    reference?: string;
    memo?: string;
    currency: string;
    exchange_rate?: number;
    items: Omit<JournalEntryItem, 'id'>[];
  }>;
  company_id: string;
  created_by: string;
  post?: boolean;
  skip_validation?: boolean;
}
