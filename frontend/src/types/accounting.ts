export interface JournalEntryLine {
  id?: string;
  account_id: string | null;
  account_name?: string;
  debit: number;
  credit: number;
  memo: string;
}

export interface JournalEntry {
  id?: string;
  reference: string;
  date: Date | string;
  memo: string;
  status: 'draft' | 'posted' | 'void';
  lines: JournalEntryLine[];
  total_amount?: number;
  created_at?: string;
  updated_at?: string;
  created_by?: string;
  updated_by?: string;
}

export interface Account {
  id: string;
  name: string;
  code: string;
  type: string;
  status: 'active' | 'inactive';
  description?: string;
  parent_id?: string | null;
  account_type?: string;
  created_at?: string;
  updated_at?: string;
}
