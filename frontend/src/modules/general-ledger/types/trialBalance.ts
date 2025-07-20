export interface TrialBalanceEntry {
  accountCode: string;
  accountName: string;
  accountType: string;
  openingBalance: number;
  periodActivity: number;
  endingBalance: number;
  debitAmount: number;
  creditAmount: number;
}

export interface TrialBalance {
  startDate: string;
  endDate: string;
  entries: TrialBalanceEntry[];
  totalDebit: number;
  totalCredit: number;
  difference: number;
}

export interface TrialBalanceParams {
  startDate: string;
  endDate: string;
  includeZeros: boolean;
  format?: 'json' | 'csv' | 'excel';
}
