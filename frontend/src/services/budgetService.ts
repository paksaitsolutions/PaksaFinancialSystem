import { api } from '@/utils/api'

export interface Budget {
  id?: string
  name: string
  description: string
  fiscal_year: number
  start_date: string
  end_date: string
  status: 'draft' | 'active' | 'pending_approval' | 'approved' | 'closed'
  line_items: BudgetLineItem[]
  total_budget?: number
  total_actual?: number
  variance?: number
}

export interface BudgetLineItem {
  id?: string
  budget_id?: string
  account_code: string
  account_name: string
  category: string
  budgeted_amount: number
  actual_amount: number
  variance: number
  period_type: 'monthly' | 'quarterly' | 'annual'
}

export interface BudgetTemplate {
  id: string
  name: string
  description: string
  template_data: Budget
}

export interface BudgetAnalytics {
  total_budgets: number
  active_budgets: number
  budget_utilization: number
  variance_percentage: number
  top_variances: Array<{
    account: string
    variance: number
    percentage: number
  }>
}

export default {
  async getBudgets(): Promise<Budget[]> {
    const response = await api.get('/budgets')
    return response.data
  },

  async getBudget(id: string): Promise<Budget> {
    const response = await api.get(`/budgets/${id}`)
    return response.data
  },

  async createBudget(budget: Omit<Budget, 'id'>): Promise<Budget> {
    const response = await api.post('/budgets', budget)
    return response.data
  },

  async updateBudget(id: string, budget: Partial<Budget>): Promise<Budget> {
    const response = await api.put(`/budgets/${id}`, budget)
    return response.data
  },

  async deleteBudget(id: string): Promise<void> {
    await api.delete(`/budgets/${id}`)
  },

  async importTemplate(templateId: string): Promise<Budget> {
    const response = await api.post(`/budgets/import-template/${templateId}`)
    return response.data
  },

  async exportBudget(id: string, format: 'excel' | 'csv' | 'pdf'): Promise<Blob> {
    const response = await api.get(`/budgets/${id}/export?format=${format}`, {
      responseType: 'blob'
    })
    return response.data
  },

  async copyFromPreviousYear(previousBudgetId: string, newFiscalYear: number): Promise<Budget> {
    const response = await api.post('/budgets/copy-previous', {
      previous_budget_id: previousBudgetId,
      new_fiscal_year: newFiscalYear
    })
    return response.data
  },

  async getBudgetAnalytics(): Promise<BudgetAnalytics> {
    const response = await api.get('/budgets/analytics')
    return response.data
  },

  async getTemplates(): Promise<BudgetTemplate[]> {
    const response = await api.get('/budgets/templates')
    return response.data
  },

  async generateForecast(budgetId: string, months: number): Promise<any> {
    const response = await api.post(`/budgets/${budgetId}/forecast`, { months })
    return response.data
  }
}