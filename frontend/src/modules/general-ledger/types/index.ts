export interface GlAccount {
  id: string
  accountNumber: string
  name: string
  description?: string
  accountType: 'asset' | 'liability' | 'equity' | 'revenue' | 'expense' | 'gain' | 'loss'
  accountSubType?: string
  parentAccountId?: string
  isActive: boolean
  isSystemAccount: boolean
  currency: string
  taxCode?: string
  costCenter?: string
  projectCode?: string
  balance: number
  budgetAmount?: number
  budgetVariance?: number
  createdAt: string
  updatedAt: string
  createdBy: string
  updatedBy?: string
  children?: GlAccount[]
  level?: number
}

export interface JournalEntry {
  id: string
  entryNumber: string
  entryDate: string
  reference?: string
  description: string
  status: 'DRAFT' | 'POSTED' | 'REVERSED'
  totalDebit: number
  totalCredit: number
  lines: JournalEntryLine[]
  createdAt: string
  updatedAt: string
  createdBy: string
  updatedBy?: string
}

export interface JournalEntryLine {
  id: string
  journalEntryId: string
  accountId: string
  lineNumber: number
  debitAmount: number
  creditAmount: number
  description?: string
  account?: GlAccount
}

export interface AccountingPeriod {
  id: string
  name: string
  startDate: string
  endDate: string
  isClosed: boolean
  closedAt?: string
  closedBy?: string
  createdAt: string
  updatedAt: string
}

export interface TrialBalance {
  asOfDate: string
  accounts: TrialBalanceAccount[]
  totalDebits: number
  totalCredits: number
}

export interface TrialBalanceAccount {
  accountCode: string
  accountName: string
  debit: number
  credit: number
}