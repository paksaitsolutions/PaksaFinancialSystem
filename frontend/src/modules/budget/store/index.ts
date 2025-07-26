import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { budgetApi } from '@/services/api'

export interface BudgetItem {
  id: string
  name: string
  category: string
  budgetedAmount: number
  actualAmount: number
  variance: number
  period: string
  status: 'on-track' | 'over-budget' | 'under-budget'
}

export const useBudgetStore = defineStore('budget', () => {
  const budgets = ref<BudgetItem[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const totalBudgeted = computed(() => 
    budgets.value.reduce((sum, item) => sum + item.budgetedAmount, 0)
  )

  const totalActual = computed(() => 
    budgets.value.reduce((sum, item) => sum + item.actualAmount, 0)
  )

  const totalVariance = computed(() => totalActual.value - totalBudgeted.value)

  const fetchBudgets = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await budgetApi.getAll()
      budgets.value = (response.items || []).map(budget => ({
        id: budget.id,
        name: budget.name,
        category: budget.category || 'General',
        budgetedAmount: budget.budgeted_amount || 0,
        actualAmount: budget.actual_amount || 0,
        variance: (budget.actual_amount || 0) - (budget.budgeted_amount || 0),
        period: budget.period || '2024-Q1',
        status: budget.status || 'on-track'
      }))
    } catch (err) {
      error.value = 'Failed to fetch budgets'
      console.error('Error fetching budgets:', err)
    } finally {
      loading.value = false
    }
  }

  const createBudget = async (budget: Omit<BudgetItem, 'id'>) => {
    loading.value = true
    try {
      const response = await budgetApi.create({
        name: budget.name,
        category: budget.category,
        budgeted_amount: budget.budgetedAmount,
        actual_amount: budget.actualAmount,
        period: budget.period,
        status: budget.status
      })
      
      const newBudget: BudgetItem = {
        id: response.data.id,
        name: response.data.name,
        category: response.data.category,
        budgetedAmount: response.data.budgeted_amount,
        actualAmount: response.data.actual_amount,
        variance: response.data.actual_amount - response.data.budgeted_amount,
        period: response.data.period,
        status: response.data.status
      }
      
      budgets.value.push(newBudget)
      return newBudget
    } catch (err) {
      error.value = 'Failed to create budget'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateBudget = async (id: string, updates: Partial<BudgetItem>) => {
    loading.value = true
    try {
      const response = await budgetApi.update(id, {
        name: updates.name,
        category: updates.category,
        budgeted_amount: updates.budgetedAmount,
        actual_amount: updates.actualAmount,
        period: updates.period,
        status: updates.status
      })
      
      const index = budgets.value.findIndex(b => b.id === id)
      if (index !== -1) {
        budgets.value[index] = {
          ...budgets.value[index],
          name: response.data.name,
          category: response.data.category,
          budgetedAmount: response.data.budgeted_amount,
          actualAmount: response.data.actual_amount,
          variance: response.data.actual_amount - response.data.budgeted_amount,
          period: response.data.period,
          status: response.data.status
        }
      }
    } catch (err) {
      error.value = 'Failed to update budget'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteBudget = async (id: string) => {
    loading.value = true
    try {
      await budgetApi.delete(id)
      budgets.value = budgets.value.filter(b => b.id !== id)
    } catch (err) {
      error.value = 'Failed to delete budget'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    budgets,
    loading,
    error,
    totalBudgeted,
    totalActual,
    totalVariance,
    fetchBudgets,
    createBudget,
    updateBudget,
    deleteBudget
  }
})