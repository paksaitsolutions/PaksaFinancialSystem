/**
 * Types for the Accounting module
 */

export type AccountCategory = 'asset' | 'liability' | 'equity' | 'revenue' | 'expense';

export type AccountType = {
  id: string;
  name: string;
  category: AccountCategory;
  code: string;
  parent_id: string | null;
  is_active: boolean;
  description?: string;
  created_at: string;
  updated_at: string;
};

export type JournalEntryStatus = 'draft' | 'posted' | 'approved' | 'rejected' | 'reversed';

export type JournalEntryLine = {
  id: string;
  journal_entry_id: string;
  account_id: string;
  account_code: string;
  account_name: string;
  description: string;
  debit: number;
  credit: number;
  tax_code?: string;
  tax_amount?: number;
  entity_type?: string;
  entity_id?: string;
  created_at: string;
  updated_at: string;
};

export type JournalEntry = {
  id: string;
  entry_number: string;
  entry_date: string;
  reference: string;
  description: string;
  status: JournalEntryStatus;
  currency: string;
  notes?: string;
  total_debit: number;
  total_credit: number;
  created_by: string;
  created_at: string;
  updated_at: string;
  approved_by?: string;
  approved_at?: string;
  posted_at?: string;
  reversed_entry_id?: string;
  reversal_id?: string;
  line_items?: JournalEntryLine[];
};

export type FinancialPeriod = {
  id: string;
  name: string;
  start_date: string;
  end_date: string;
  status: 'open' | 'closed' | 'future';
  is_current: boolean;
  created_at: string;
  updated_at: string;
};

export type FinancialStatement = {
  id: string;
  name: string;
  description?: string;
  type: 'balance_sheet' | 'income_statement' | 'cash_flow' | 'custom';
  currency: string;
  period_id: string;
  period_name: string;
  generated_at: string;
  data: Record<string, any>;
  created_at: string;
  updated_at: string;
};

export type TrialBalanceItem = {
  account_id: string;
  account_code: string;
  account_name: string;
  account_type: AccountCategory;
  opening_debit: number;
  opening_credit: number;
  period_debit: number;
  period_credit: number;
  closing_debit: number;
  closing_credit: number;
};

export type TrialBalanceReport = {
  period_id: string;
  period_name: string;
  currency: string;
  generated_at: string;
  items: TrialBalanceItem[];
  total_opening_debit: number;
  total_opening_credit: number;
  total_period_debit: number;
  total_period_credit: number;
  total_closing_debit: number;
  total_closing_credit: number;
};

export type AccountBalance = {
  account_id: string;
  account_code: string;
  account_name: string;
  account_type: AccountCategory;
  balance: number;
  balance_type: 'debit' | 'credit';
  as_of_date: string;
};

export type AccountTransaction = {
  id: string;
  transaction_date: string;
  reference: string;
  description: string;
  journal_entry_id: string;
  journal_entry_number: string;
  account_id: string;
  account_code: string;
  account_name: string;
  debit: number;
  credit: number;
  balance: number;
  created_at: string;
};

export type AccountLedger = {
  account_id: string;
  account_code: string;
  account_name: string;
  account_type: AccountCategory;
  currency: string;
  period_id: string;
  period_name: string;
  opening_balance: number;
  opening_balance_type: 'debit' | 'credit';
  closing_balance: number;
  closing_balance_type: 'debit' | 'credit';
  transactions: AccountTransaction[];
  total_debit: number;
  total_credit: number;
};
