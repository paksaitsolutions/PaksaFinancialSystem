export interface JournalEntryLine {
  id?: string;
  account_id: string | null;
  account_name?: string;
  debit: number;
  credit: number;
  memo: string;
}

export interface JournalEntry {
  id: string;
  reference: string;
  date: Date | string;
  status: 'draft' | 'posted' | 'void';
  memo: string;
  lines: JournalEntryLine[];
  total_amount?: number;
}

export type NewJournalEntry = Omit<JournalEntry, 'id' | 'total_amount'>;

export interface JournalEntryState {
  entries: JournalEntry[];
  loading: boolean;
  error: string | null;
}
