import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useApi } from '@/composables/useApi'
import type { BudgetResponse, BudgetListResponse, BudgetCreate, BudgetUpdate, BudgetApprovalCreate } from '@/types/budget'

export const useBudgetStore = defineStore('budget', () => {
  const api = useApi()
  const budgets = ref<BudgetResponse[]>([])
  const selectedBudget = ref<BudgetResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const filteredBudgets = computed(() => {
    return budgets.value.filter(budget => {
      // Add filtering logic here
      return true
    })
  })

  const totalBudgets = computed(() => budgets.value.length)

  async function fetchBudgets(page = 1, limit = 10) {
    try {
      loading.value = true
      error.value = null
      const response = await api.get<BudgetListResponse>(`/budget`, {
        params: { skip: (page - 1) * limit, limit }
      })
      budgets.value = response.data.budgets
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  async function fetchBudget(id: number) {
    try {
      loading.value = true
      error.value = null
      const response = await api.get<BudgetResponse>(`/budget/${id}`)
      selectedBudget.value = response.data
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  async function createBudget(data: BudgetCreate) {
    try {
      loading.value = true
      error.value = null
      const response = await api.post<BudgetResponse>(`/budget`, data)
      budgets.value.unshift(response.data)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateBudget(id: number, data: BudgetUpdate) {
    try {
      loading.value = true
      error.value = null
      const response = await api.put<BudgetResponse>(`/budget/${id}`, data)
      const index = budgets.value.findIndex(b => b.id === id)
      if (index !== -1) {
        budgets.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function approveBudget(id: number, approvalData: BudgetApprovalCreate) {
    try {
      loading.value = true
      error.value = null
      const response = await api.post<BudgetResponse>(`/budget/${id}/approve`, approvalData)
      const index = budgets.value.findIndex(b => b.id === id)
      if (index !== -1) {
        budgets.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function rejectBudget(id: number, notes: string) {
    try {
      loading.value = true
      error.value = null
      const response = await api.post<BudgetResponse>(`/budget/${id}/reject`, { notes })
      const index = budgets.value.findIndex(b => b.id === id)
      if (index !== -1) {
        budgets.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function archiveBudget(id: number) {
    try {
      loading.value = true
      error.value = null
      const response = await api.post<BudgetResponse>(`/budget/${id}/archive`)
      const index = budgets.value.findIndex(b => b.id === id)
      if (index !== -1) {
        budgets.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function getBudgetPerformance(
    departmentId?: number,
    projectId?: number
  ) {
    try {
      loading.value = true
      error.value = null
      const response = await api.get(`/budget/stats`, {
        params: { department_id: departmentId, project_id: projectId }
      })
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function getDepartmentalAnalysis() {
    try {
      loading.value = true
      error.value = null
      const response = await api.get(`/budget/analysis/department`)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function getProjectAnalysis() {
    try {
      loading.value = true
      error.value = null
      const response = await api.get(`/budget/analysis/project`)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function getTrendAnalysis(period: string = 'month', months: number = 12) {
    try {
      loading.value = true
      error.value = null
      const response = await api.get(`/budget/analysis/trend`, {
        params: { period, months }
      })
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function getAllocationAnalysis(accountId: number) {
    try {
      loading.value = true
      error.value = null
      const response = await api.get(`/budget/analysis/allocation/${accountId}`)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function getVarianceAnalysis() {
    try {
      loading.value = true
      error.value = null
      const response = await api.get(`/budget/analysis/variance`)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function exportData(format: string, data: any) {
    try {
      loading.value = true
      error.value = null
      const response = await api.post(`/budget/export/${format}`, data)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    budgets,
    selectedBudget,
    loading,
    error,
    filteredBudgets,
    totalBudgets,
    fetchBudgets,
    fetchBudget,
    createBudget,
    updateBudget,
    approveBudget,
    rejectBudget,
    archiveBudget,
    getBudgetPerformance,
    getDepartmentalAnalysis,
    getProjectAnalysis,
    getTrendAnalysis,
    getAllocationAnalysis,
    getVarianceAnalysis,
    exportData
  }
})
