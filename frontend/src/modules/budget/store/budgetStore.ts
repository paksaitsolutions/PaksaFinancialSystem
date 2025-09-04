import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Budget, BudgetCreate, BudgetUpdate, BudgetFilters, BudgetSummary } from '../types/budget'
import { budgetService } from '../services/budgetService'

export const useBudgetStore = defineStore('budget', () => {
  // State
  const budgets = ref<Budget[]>([])
  const currentBudget = ref<Budget | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(10)

  // Getters
  const totalBudgetAmount = computed(() => 
    budgets.value.reduce((sum, budget) => sum + budget.amount, 0)
  )

  const budgetsByStatus = computed(() => {
    const grouped: Record<string, Budget[]> = {}
    budgets.value.forEach(budget => {
      if (!grouped[budget.status]) {
        grouped[budget.status] = []
      }
      grouped[budget.status].push(budget)
    })
    return grouped
  })

  const budgetsByType = computed(() => {
    const grouped: Record<string, Budget[]> = {}
    budgets.value.forEach(budget => {
      if (!grouped[budget.type]) {
        grouped[budget.type] = []
      }
      grouped[budget.type].push(budget)
    })
    return grouped
  })

  const summary = computed((): BudgetSummary => {
    const statusCounts = budgets.value.reduce((acc, budget) => {
      acc[budget.status] = (acc[budget.status] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    const typeCounts = budgets.value.reduce((acc, budget) => {
      acc[budget.type] = (acc[budget.type] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    return {
      totalBudgets: budgets.value.length,
      totalAmount: totalBudgetAmount.value,
      totalSpent: 0, // This would come from actual spending data
      totalRemaining: totalBudgetAmount.value,
      byStatus: statusCounts as any,
      byType: typeCounts as any
    }
  })

  // Actions
  const fetchBudgets = async (filters?: BudgetFilters) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await budgetService.listBudgets(currentPage.value, pageSize.value, filters)
      budgets.value = response.items
      total.value = response.total
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch budgets'
      console.error('Error fetching budgets:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchBudget = async (id: number) => {
    loading.value = true
    error.value = null
    
    try {
      currentBudget.value = await budgetService.getBudget(id)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch budget'
      console.error('Error fetching budget:', err)
    } finally {
      loading.value = false
    }
  }

  const createBudget = async (budgetData: BudgetCreate) => {
    loading.value = true
    error.value = null
    
    try {
      const newBudget = await budgetService.createBudget(budgetData)
      budgets.value.unshift(newBudget)
      total.value += 1
      return newBudget
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create budget'
      console.error('Error creating budget:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateBudget = async (id: number, budgetData: BudgetUpdate) => {
    loading.value = true
    error.value = null
    
    try {
      const updatedBudget = await budgetService.updateBudget(id, budgetData)
      const index = budgets.value.findIndex(b => b.id === id)
      if (index !== -1) {
        budgets.value[index] = updatedBudget
      }
      if (currentBudget.value?.id === id) {
        currentBudget.value = updatedBudget
      }
      return updatedBudget
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update budget'
      console.error('Error updating budget:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteBudget = async (id: number) => {
    loading.value = true
    error.value = null
    
    try {
      await budgetService.deleteBudget(id)
      budgets.value = budgets.value.filter(b => b.id !== id)
      total.value -= 1
      if (currentBudget.value?.id === id) {
        currentBudget.value = null
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete budget'
      console.error('Error deleting budget:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const approveBudget = async (id: number, notes?: string) => {
    try {
      const approvedBudget = await budgetService.approveBudget(id, notes)
      const index = budgets.value.findIndex(b => b.id === id)
      if (index !== -1) {
        budgets.value[index] = approvedBudget
      }
      return approvedBudget
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to approve budget'
      throw err
    }
  }

  const rejectBudget = async (id: number, reason: string) => {
    try {
      const rejectedBudget = await budgetService.rejectBudget(id, reason)
      const index = budgets.value.findIndex(b => b.id === id)
      if (index !== -1) {
        budgets.value[index] = rejectedBudget
      }
      return rejectedBudget
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to reject budget'
      throw err
    }
  }

  const submitForApproval = async (id: number) => {
    try {
      const submittedBudget = await budgetService.submitForApproval(id)
      const index = budgets.value.findIndex(b => b.id === id)
      if (index !== -1) {
        budgets.value[index] = submittedBudget
      }
      return submittedBudget
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to submit budget for approval'
      throw err
    }
  }

  const setPage = (page: number) => {
    currentPage.value = page
  }

  const setPageSize = (size: number) => {
    pageSize.value = size
  }

  const clearError = () => {
    error.value = null
  }

  const clearCurrentBudget = () => {
    currentBudget.value = null
  }

  return {
    // State
    budgets,
    currentBudget,
    loading,
    error,
    total,
    currentPage,
    pageSize,
    
    // Getters
    totalBudgetAmount,
    budgetsByStatus,
    budgetsByType,
    summary,
    
    // Actions
    fetchBudgets,
    fetchBudget,
    createBudget,
    updateBudget,
    deleteBudget,
    approveBudget,
    rejectBudget,
    submitForApproval,
    setPage,
    setPageSize,
    clearError,
    clearCurrentBudget
  }
})