import { apiClient } from '@/utils/apiClient'
import type { Budget, BudgetCreate, BudgetUpdate, BudgetLineItem } from '../types/budget'

export interface BudgetListResponse {
  items: Budget[]
  total: number
}

export interface BudgetFilters {
  status?: string
  type?: string
  search?: string
}

class BudgetService {
  private readonly baseUrl = '/api/v1/budget'

  async createBudget(budget: BudgetCreate): Promise<Budget> {
    return await apiClient.post<Budget>(`${this.baseUrl}/`, budget)
  }

  async getBudget(id: number): Promise<Budget> {
    return await apiClient.get<Budget>(`${this.baseUrl}/${id}`)
  }

  async updateBudget(id: number, budget: BudgetUpdate): Promise<Budget> {
    return await apiClient.put<Budget>(`${this.baseUrl}/${id}`, budget)
  }

  async deleteBudget(id: number): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/${id}`)
  }

  async listBudgets(
    page: number = 1,
    limit: number = 10,
    filters?: BudgetFilters
  ): Promise<BudgetListResponse> {
    const params = new URLSearchParams({
      skip: ((page - 1) * limit).toString(),
      limit: limit.toString()
    })

    if (filters?.status) params.append('status', filters.status)
    if (filters?.type) params.append('type', filters.type)
    if (filters?.search) params.append('search', filters.search)

    return await apiClient.get<BudgetListResponse>(`${this.baseUrl}/?${params}`)
  }

  async approveBudget(id: number, notes?: string): Promise<Budget> {
    return await apiClient.post<Budget>(`${this.baseUrl}/${id}/approve`, { notes })
  }

  async rejectBudget(id: number, reason: string): Promise<Budget> {
    return await apiClient.post<Budget>(`${this.baseUrl}/${id}/reject`, { reason })
  }

  async submitForApproval(id: number): Promise<Budget> {
    return await apiClient.post<Budget>(`${this.baseUrl}/${id}/submit`)
  }

  async getBudgetVsActual(id: number, period?: string) {
    const params = period ? `?period=${period}` : ''
    return await apiClient.get(`${this.baseUrl}/${id}/vs-actual${params}`)
  }

  async addLineItem(budgetId: number, lineItem: Omit<BudgetLineItem, 'id' | 'budget_id'>): Promise<BudgetLineItem> {
    return await apiClient.post<BudgetLineItem>(`${this.baseUrl}/${budgetId}/line-items`, lineItem)
  }

  async updateLineItem(lineItemId: number, lineItem: Partial<BudgetLineItem>): Promise<BudgetLineItem> {
    return await apiClient.put<BudgetLineItem>(`${this.baseUrl}/line-items/${lineItemId}`, lineItem)
  }

  async deleteLineItem(lineItemId: number): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/line-items/${lineItemId}`)
  }
}

export const budgetService = new BudgetService()
export default budgetService