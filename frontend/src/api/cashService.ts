import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token') || sessionStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export interface Transaction {
  id: string
  account_id: string
  transaction_date: string
  posted_date?: string
  transaction_type: string
  status: string
  amount: number
  reference_number?: string
  check_number?: string
  memo?: string
  notes?: string
  category_id?: string
  payment_method?: string
  payee?: string
  running_balance?: number
  is_reconciled: boolean
  created_at: string
  updated_at: string
}

export interface BankAccount {
  id: string
  name: string
  account_number: string
  account_type: string
  status: string
  bank_name: string
  current_balance: number
  available_balance: number
}

export interface CreateTransactionRequest {
  account_id: string
  transaction_date: string
  transaction_type: string
  amount: number
  memo?: string
  payee?: string
  payment_method?: string
}

export const cashService = {
  async getTransactions(params?: {
    account_id?: string
    start_date?: string
    end_date?: string
    transaction_type?: string
    status?: string
    search?: string
    skip?: number
    limit?: number
  }) {
    const response = await apiClient.get('/api/v1/cash-management/transactions', { params })
    return response.data
  },

  async createTransaction(data: CreateTransactionRequest) {
    const response = await apiClient.post('/api/v1/cash-management/transactions', data)
    return response.data
  },

  async getTransaction(id: string) {
    const response = await apiClient.get(`/api/v1/cash-management/transactions/${id}`)
    return response.data
  },

  async getBankAccounts() {
    const response = await apiClient.get('/api/v1/cash-management/accounts')
    return response.data
  },

  async createBankAccount(data: any) {
    const response = await apiClient.post('/api/v1/cash-management/accounts', data)
    return response.data
  },

  async getDashboard() {
    const response = await apiClient.get('/api/v1/cash-management/dashboard')
    return response.data
  }
}