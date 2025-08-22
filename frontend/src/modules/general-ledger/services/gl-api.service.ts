import axios from 'axios'

const API_BASE = '/api/v1/general-ledger'

export interface Account {
  id: number
  account_code: string
  account_name: string
  account_type: string
  parent_account_id?: number
  is_active: boolean
  description?: string
}

export interface JournalEntryLine {
  account_id: number
  description?: string
  debit_amount: number
  credit_amount: number
}

export interface JournalEntry {
  id?: number
  entry_number?: string
  entry_date: string
  description: string
  reference?: string
  lines: JournalEntryLine[]
  total_debit?: number
  total_credit?: number
  status?: string
}

export interface TrialBalanceItem {
  account_code: string
  account_name: string
  debit_balance: number
  credit_balance: number
}

export interface TrialBalance {
  as_of_date: string
  accounts: TrialBalanceItem[]
  total_debits: number
  total_credits: number
}

class GLApiService {
  // Account methods
  async getAccounts(): Promise<Account[]> {
    const response = await axios.get(`${API_BASE}/accounts/`)
    return response.data
  }

  async getAccount(id: number): Promise<Account> {
    const response = await axios.get(`${API_BASE}/accounts/${id}`)
    return response.data
  }

  async createAccount(account: Omit<Account, 'id'>): Promise<Account> {
    const response = await axios.post(`${API_BASE}/accounts/`, account)
    return response.data
  }

  async updateAccount(id: number, account: Partial<Account>): Promise<Account> {
    const response = await axios.put(`${API_BASE}/accounts/${id}`, account)
    return response.data
  }

  async getChartOfAccounts(): Promise<Account[]> {
    const response = await axios.get(`${API_BASE}/chart-of-accounts/`)
    return response.data
  }

  // Journal Entry methods
  async getJournalEntries(): Promise<JournalEntry[]> {
    const response = await axios.get(`${API_BASE}/journal-entries/`)
    return response.data
  }

  async getJournalEntry(id: number): Promise<JournalEntry> {
    const response = await axios.get(`${API_BASE}/journal-entries/${id}`)
    return response.data
  }

  async createJournalEntry(entry: Omit<JournalEntry, 'id' | 'entry_number'>): Promise<JournalEntry> {
    const response = await axios.post(`${API_BASE}/journal-entries/`, entry)
    return response.data
  }

  // Reports
  async getTrialBalance(asOfDate: string): Promise<TrialBalance> {
    const response = await axios.get(`${API_BASE}/reports/trial-balance`, {
      params: { as_of_date: asOfDate }
    })
    return response.data
  }
}

export const glApiService = new GLApiService()