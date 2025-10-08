import { api as apiClient } from './index.js'

export interface BudgetLineItem {
  id?: number
  category: string
  description?: string
  amount: number
}

export interface Budget {
  id?: number
  name: string
  type: string
  amount: number
  period_start: string
  period_end: string
  status: string
  description?: string
  created_at?: string
  updated_at?: string
  line_items: BudgetLineItem[]
}

export interface BudgetSummary {
  total_budgets: number
  total_amount: number
  approved_amount: number
  pending_amount: number
  utilization_rate: number
}

export interface BudgetVariance {
  category: string
  budget: number
  actual: number
  variance: number
  variance_percent: number
  status: string
}

export const budgetService = {
  async getBudgets(status?: string, type?: string) {
    const params = new URLSearchParams()
    if (status) params.append('status', status)
    if (type) params.append('type', type)
    
    const response = await apiClient.get(`/budgets/?${params.toString()}`)
    return response.data
  },

  async createBudget(budget: Partial<Budget>) {
    const response = await apiClient.post('/budgets/', budget)
    return response.data
  },

  async getBudget(id: number) {
    const response = await apiClient.get(`/budgets/${id}`)
    return response.data
  },

  async updateBudget(id: number, budget: Partial<Budget>) {
    const response = await apiClient.put(`/budgets/${id}`, budget)
    return response.data
  },

  async deleteBudget(id: number) {
    const response = await apiClient.delete(`/budgets/${id}`)
    return response.data
  },

  async getBudgetSummary(): Promise<BudgetSummary> {
    const response = await apiClient.get('/budgets/summary/dashboard')
    return response.data
  },

  async getBudgetVariance(): Promise<BudgetVariance[]> {
    const response = await apiClient.get('/budgets/variance/analysis')
    return response.data
  },

  async approveBudget(id: number, notes: string = '') {
    const response = await apiClient.post(`/budgets/${id}/approve`, null, {
      params: { notes }
    })
    return response.data
  },

  async rejectBudget(id: number, notes: string = '') {
    const response = await apiClient.post(`/budgets/${id}/reject`, null, {
      params: { notes }
    })
    return response.data
  },

  async getBudgetVsActualReport() {
    const response = await apiClient.get('/budgets/reports/budget-vs-actual')
    return response.data
  }
}