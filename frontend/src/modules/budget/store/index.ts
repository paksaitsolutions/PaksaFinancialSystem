import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

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
      // Mock data - replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      budgets.value = [
        {
          id: '1',
          name: 'Marketing',
          category: 'Expenses',
          budgetedAmount: 50000,
          actualAmount: 45000,
          variance: -5000,
          period: '2024-Q1',
          status: 'under-budget'
        },
        {
          id: '2',
          name: 'Operations',
          category: 'Expenses',
          budgetedAmount: 100000,
          actualAmount: 110000,
          variance: 10000,
          period: '2024-Q1',
          status: 'over-budget'
        }
      ]
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
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 500))
      
      const newBudget: BudgetItem = {
        ...budget,
        id: Date.now().toString()
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
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 500))
      
      const index = budgets.value.findIndex(b => b.id === id)
      if (index !== -1) {
        budgets.value[index] = { ...budgets.value[index], ...updates }
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
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 500))
      
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