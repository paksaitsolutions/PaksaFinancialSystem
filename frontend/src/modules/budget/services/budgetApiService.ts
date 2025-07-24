import axios from 'axios'
import type { Budget } from '../store/budget'

const API_BASE = '/api/v1/budget'

export interface BudgetVsActual {
  budgetId: string
  period: string
  budgetAmount: number
  actualAmount: number
  variance: number
  variancePercent: number
  lineItems: {
    category: string
    budgetAmount: number
    actualAmount: number
    variance: number
  }[]
}

class BudgetApiService {
  async getBudgets(): Promise<Budget[]> {
    const response = await axios.get(`${API_BASE}/`)
    return response.data
  }

  async getBudget(id: string): Promise<Budget> {
    const response = await axios.get(`${API_BASE}/${id}`)
    return response.data
  }

  async createBudget(budget: Omit<Budget, 'id'>): Promise<Budget> {
    const response = await axios.post(`${API_BASE}/`, budget)
    return response.data
  }

  async updateBudget(id: string, budget: Partial<Budget>): Promise<Budget> {
    const response = await axios.put(`${API_BASE}/${id}`, budget)
    return response.data
  }

  async deleteBudget(id: string): Promise<void> {
    await axios.delete(`${API_BASE}/${id}`)
  }

  async approveBudget(id: string, notes?: string): Promise<Budget> {
    const response = await axios.post(`${API_BASE}/${id}/approve`, { notes })
    return response.data
  }

  async rejectBudget(id: string, reason: string): Promise<Budget> {
    const response = await axios.post(`${API_BASE}/${id}/reject`, { reason })
    return response.data
  }

  async getBudgetVsActual(id: string, period: string): Promise<BudgetVsActual> {
    const response = await axios.get(`${API_BASE}/${id}/vs-actual`, {
      params: { period }
    })
    return response.data
  }

  async submitForApproval(id: string): Promise<Budget> {
    const response = await axios.post(`${API_BASE}/${id}/submit`)
    return response.data
  }
}

export const budgetApiService = new BudgetApiService()