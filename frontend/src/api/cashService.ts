import { api } from '@/utils/api'

export interface BankAccount {
  id: string
  name: string
  account_number: string
  bank_name: string
  account_type: 'checking' | 'savings' | 'money_market' | 'credit_line'
  current_balance: number
  available_balance: number
  currency: string
  is_active: boolean
}

export interface CashTransaction {
  id: string
  account_id: string
  transaction_date: string
  transaction_type: 'deposit' | 'withdrawal' | 'transfer_in' | 'transfer_out'
  amount: number
  memo: string
  reference: string
  account?: BankAccount
}

export interface CashFlowForecast {
  period: string
  projected_inflow: number
  projected_outflow: number
  net_cash_flow: number
  ending_balance: number
  confidence_level: number
}

export interface CashDashboard {
  total_balance: number
  account_count: number
  monthly_inflow: number
  monthly_outflow: number
  cash_flow_trend: number[]
  liquidity_ratio: number
}

export const cashService = {
  async getDashboard(): Promise<CashDashboard> {
    const response = await api.get('/cash/dashboard')
    return response.data
  },

  async getBankAccounts(): Promise<BankAccount[]> {
    const response = await api.get('/cash/accounts')
    return response.data
  },

  async createBankAccount(account: Omit<BankAccount, 'id'>): Promise<BankAccount> {
    const response = await api.post('/cash/accounts', account)
    return response.data
  },

  async getTransactions(params?: { limit?: number }): Promise<CashTransaction[]> {
    const response = await api.get('/cash/transactions', { params })
    return response.data
  },

  async createTransaction(transaction: Omit<CashTransaction, 'id'>): Promise<CashTransaction> {
    const response = await api.post('/cash/transactions', transaction)
    return response.data
  },

  async getCashFlowForecast(days: number = 30): Promise<CashFlowForecast[]> {
    const response = await api.get(`/cash/forecast?days=${days}`)
    return response.data
  },

  async reconcileAccount(accountId: string, statementData: any): Promise<{ success: boolean }> {
    const response = await api.post(`/cash/accounts/${accountId}/reconcile`, statementData)
    return response.data
  }
}