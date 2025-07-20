import type { Account } from './account';

/**
 * Allocation method options
 */
export type AllocationMethod =
  | 'fixed_amount'
  | 'percentage'
  | 'quantity'
  | 'weighted'
  | 'custom';

/**
 * Base interface for allocation rules
 */
export interface AllocationRuleBase {
  id: string;
  name: string;
  description: string | null;
  is_active: boolean;
  allocation_method: AllocationMethod;
  company_id: string;
  created_by: string;
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
  deleted_at: string | null; // ISO date string
}

/**
 * Allocation rule with its destinations
 */
export interface AllocationRule extends AllocationRuleBase {
  destinations: AllocationDestination[];
}

/**
 * Data needed to create a new allocation rule
 */
export interface AllocationRuleCreate {
  name: string;
  description?: string | null;
  is_active?: boolean;
  allocation_method: AllocationMethod;
  company_id: string;
  destinations?: Omit<AllocationDestinationCreate, 'allocation_rule_id'>[];
}

/**
 * Data needed to update an existing allocation rule
 */
export interface AllocationRuleUpdate {
  name?: string;
  description?: string | null;
  is_active?: boolean;
  allocation_method?: AllocationMethod;
}

/**
 * Parameters for listing allocation rules
 */
export interface AllocationRuleListParams {
  page?: number;
  per_page?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  is_active?: boolean;
  company_id?: string;
  created_by?: string;
  search?: string;
}

/**
 * Response when listing allocation rules
 */
export interface AllocationRuleListResponse {
  data: AllocationRule[];
  pagination: {
    total: number;
    page: number;
    per_page: number;
    total_pages: number;
  };
}

/**
 * Allocation destination (where amounts are allocated to)
 */
export interface AllocationDestination {
  id: string;
  allocation_rule_id: string;
  account_id: string;
  account: Account;
  percentage: number | null;
  fixed_amount: number | null;
  description: string | null;
  reference: string | null;
  sequence: number;
  is_active: boolean;
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
}

/**
 * Data needed to create a new allocation destination
 */
export interface AllocationDestinationCreate {
  allocation_rule_id: string;
  account_id: string;
  percentage?: number | null;
  fixed_amount?: number | null;
  description?: string | null;
  reference?: string | null;
  sequence?: number;
  is_active?: boolean;
}

/**
 * Data needed to update an allocation destination
 */
export interface AllocationDestinationUpdate {
  account_id?: string;
  percentage?: number | null;
  fixed_amount?: number | null;
  description?: string | null;
  reference?: string | null;
  sequence?: number;
  is_active?: boolean;
}

/**
 * Preview of an allocation
 */
export interface AllocationPreview {
  source_account: Account;
  source_amount: number;
  currency: string;
  allocations: Array<{
    destination: Account;
    amount: number;
    percentage: number | null;
    fixed_amount: number | null;
  }>;
  total_allocated: number;
  remaining_amount: number;
  is_balanced: boolean;
  validation_errors: string[];
}

/**
 * Parameters for running an allocation rule
 */
export interface AllocationRunParams {
  source_account_id: string;
  amount: number;
  date: string; // ISO date string
  reference?: string;
  memo?: string;
  post_journal?: boolean;
  journal_date?: string; // ISO date string
  journal_reference?: string;
  journal_memo?: string;
  notify_on_completion?: boolean;
  notification_emails?: string[];
  dry_run?: boolean;
}

/**
 * Response from running an allocation rule
 */
export interface AllocationRunResponse {
  success: boolean;
  message: string;
  journal_entry_id?: string;
  journal_entry_number?: string;
  allocation_run_id: string;
  dry_run: boolean;
  preview: AllocationPreview;
  errors: string[];
  warnings: string[];
}

/**
 * A past run of an allocation rule
 */
export interface AllocationRun {
  id: string;
  allocation_rule_id: string;
  run_by: string;
  run_at: string; // ISO date string
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  source_account_id: string;
  source_amount: number;
  currency: string;
  total_allocated: number;
  remaining_amount: number;
  is_balanced: boolean;
  reference: string | null;
  memo: string | null;
  journal_entry_id: string | null;
  journal_entry_number: string | null;
  error_message: string | null;
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
}

/**
 * Statistics about allocation rules
 */
export interface AllocationRuleStats {
  total_rules: number;
  active_rules: number;
  inactive_rules: number;
  last_run: string | null; // ISO date string
  total_allocated: number;
  total_runs: number;
  by_method: Record<AllocationMethod, number>;
  recent_runs: Array<{
    id: string;
    allocation_rule_id: string;
    allocation_rule_name: string;
    run_at: string; // ISO date string
    status: string;
    source_account_name: string;
    source_amount: number;
    total_allocated: number;
  }>;
  top_destinations: Array<{
    account_id: string;
    account_name: string;
    account_code: string;
    total_allocated: number;
    percentage_of_total: number;
  }>;
}
