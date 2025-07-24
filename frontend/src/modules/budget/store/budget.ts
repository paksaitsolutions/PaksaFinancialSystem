import { defineStore } from 'pinia'
import { budgetApiService } from '../services/budgetApiService'

export interface Budget {
  id: string
  name: string
  amount: number
  type: string
  status: string
  startDate: string
  endDate: string
  description?: string
  lineItems?: BudgetLineItem[]
  createdAt?: string
  updatedAt?: string
}

export interface BudgetLineItem {
  id?: string
  category: string
  description: string
  amount: number
}

export const useBudgetStore = defineStore('budget', {
  state: () => ({
    budgets: [] as Budget[],
    loading: false,
    error: null as string | null
  }),

  getters: {
    getBudgetById: (state) => (id: string) => {
      return state.budgets.find(budget => budget.id === id)
    },
    
    getBudgetsByStatus: (state) => (status: string) => {
      return state.budgets.filter(budget => budget.status === status)
    },
    
    getTotalBudgetAmount: (state) => {
      return state.budgets.reduce((total, budget) => total + budget.amount, 0)
    }
  },

  actions: {
    async fetchBudgets() {
      try {
        this.loading = true
        this.error = null
        this.budgets = await budgetApiService.getBudgets()
      } catch (error) {
        this.error = error instanceof Error ? error.message : 'Failed to fetch budgets'
        throw error
      } finally {
        this.loading = false
      }
    },

    async createBudget(budgetData: Omit<Budget, 'id'>) {
      try {
        this.loading = true
        this.error = null
        const newBudget = await budgetApiService.createBudget(budgetData)
        this.budgets.push(newBudget)
        return newBudget
      } catch (error) {
        this.error = error instanceof Error ? error.message : 'Failed to create budget'
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateBudget(id: string, budgetData: Partial<Budget>) {
      try {
        this.loading = true
        this.error = null
        const updatedBudget = await budgetApiService.updateBudget(id, budgetData)
        const index = this.budgets.findIndex(budget => budget.id === id)
        if (index !== -1) {
          this.budgets[index] = updatedBudget
        }
        return updatedBudget
      } catch (error) {
        this.error = error instanceof Error ? error.message : 'Failed to update budget'
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteBudget(id: string) {
      try {
        this.loading = true
        this.error = null
        await budgetApiService.deleteBudget(id)
        this.budgets = this.budgets.filter(budget => budget.id !== id)
      } catch (error) {
        this.error = error instanceof Error ? error.message : 'Failed to delete budget'
        throw error
      } finally {
        this.loading = false
      }
    },

    async approveBudget(id: string, notes?: string) {
      try {
        this.loading = true
        this.error = null
        const approvedBudget = await budgetApiService.approveBudget(id, notes)
        const index = this.budgets.findIndex(budget => budget.id === id)
        if (index !== -1) {
          this.budgets[index] = approvedBudget
        }
        return approvedBudget
      } catch (error) {
        this.error = error instanceof Error ? error.message : 'Failed to approve budget'
        throw error
      } finally {
        this.loading = false
      }
    },

    async rejectBudget(id: string, reason: string) {
      try {
        this.loading = true
        this.error = null
        const rejectedBudget = await budgetApiService.rejectBudget(id, reason)
        const index = this.budgets.findIndex(budget => budget.id === id)
        if (index !== -1) {
          this.budgets[index] = rejectedBudget
        }
        return rejectedBudget
      } catch (error) {
        this.error = error instanceof Error ? error.message : 'Failed to reject budget'
        throw error
      } finally {
        this.loading = false
      }
    },

    async getBudgetVsActual(id: string, period: string) {
      try {
        this.loading = true
        this.error = null
        return await budgetApiService.getBudgetVsActual(id, period)
      } catch (error) {
        this.error = error instanceof Error ? error.message : 'Failed to get budget vs actual'
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})