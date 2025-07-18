import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { useApi } from '@/composables/useApi'
import type {
  BudgetResponse,
  BudgetListResponse,
  BudgetCreate,
  BudgetUpdate,
  BudgetApprovalCreate,
  BudgetPerformance,
  BudgetAnalysisData,
  BudgetTrendData,
  BudgetAllocationAnalysis,
  BudgetVarianceAnalysis,
  BudgetStatus,
  BudgetType
} from '@/types/budget'
import { useToast } from 'primevue/usetoast'

export const useBudgetStore = defineStore('budget', () => {
  // Initialize API and Toast
  const api = useApi()
  const toast = useToast()

  // State
  const budgets = ref<BudgetResponse[]>([])
  const selectedBudget = ref<BudgetResponse | null>(null)
  const loading = ref<boolean>(false)
  const error = ref<string | null>(null)
  const pagination = ref({
    page: 1,
    limit: 10,
    total: 0
  })



  // Actions
  async function fetchBudgets(page = 1, limit = 10) {
    try {
      loading.value = true
      error.value = null
      const response = await api.get<BudgetListResponse>('/budget', {
        params: { 
          skip: (page - 1) * limit, 
          limit,
          status: filters.value.status,
          type: filters.value.type,
          startDate: filters.value.startDate,
          endDate: filters.value.endDate
        }
      })
      budgets.value = response.data.budgets || []
      pagination.value = {
        page,
        limit,
        total: response.data.total || 0
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to fetch budgets'
      error.value = message
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: message,
        life: 5000
      })
      console.error('Failed to fetch budgets:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchBudget(id: number) {
    try {
      loading.value = true
      error.value = null
      const response = await api.get<BudgetResponse>(`/budget/${id}`)
      selectedBudget.value = response
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch budget'
      console.error('Failed to fetch budget:', err)
    } finally {
      loading.value = false
    }
  }

  async function createBudget(data: BudgetCreate) {
    try {
      loading.value = true
      error.value = null
      const response = await api.post<BudgetResponse>('/budget', data)
      const newBudget = response
      budgets.value.push(newBudget)
      return newBudget
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to create budget'
      console.error('Failed to create budget:', err)
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
      const updatedBudget = response
      const index = budgets.value.findIndex(b => b.id === id)
      if (index !== -1) {
        budgets.value[index] = updatedBudget
      }
      if (selectedBudget.value?.id === id) {
        selectedBudget.value = updatedBudget
      }
      return updatedBudget
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to update budget'
      console.error('Failed to update budget:', err)
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
      const updatedBudget = response
      const index = budgets.value.findIndex(b => b.id === id)
      if (index !== -1) {
        budgets.value[index] = updatedBudget
      }
      if (selectedBudget.value?.id === id) {
        selectedBudget.value = updatedBudget
      }
      return updatedBudget
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to approve budget'
      console.error('Failed to approve budget:', err)
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
      const updatedBudget = response
      const index = budgets.value.findIndex(b => b.id === id)
      if (index !== -1) {
        budgets.value[index] = updatedBudget
      }
      if (selectedBudget.value?.id === id) {
        selectedBudget.value = updatedBudget
      }
      return updatedBudget
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to reject budget'
      console.error('Failed to reject budget:', err)
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
      const updatedBudget = response
      const index = budgets.value.findIndex(b => b.id === id)
      if (index !== -1) {
        budgets.value[index] = updatedBudget
      }
      if (selectedBudget.value?.id === id) {
        selectedBudget.value = updatedBudget
      }
      return updatedBudget
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to archive budget'
      console.error('Failed to archive budget:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function getBudgetPerformance(
    departmentId?: number,
    projectId?: number
  ): Promise<BudgetPerformance> {
    try {
      loading.value = true
      error.value = null
      const response = await api.get<BudgetPerformance>('/budget/performance', {
        params: { departmentId, projectId }
      })
      return response
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to get budget performance'
      error.value = message
      console.error('Failed to get budget performance:', err)
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function getDepartmentalAnalysis(): Promise<BudgetAnalysisData[]> {
    try {
      loading.value = true
      error.value = null
      const response = await api.get<BudgetAnalysisData[]>('/budget/analysis/department')
      return response
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to get departmental analysis'
      error.value = message
      console.error('Failed to get departmental analysis:', err)
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function getProjectAnalysis(): Promise<BudgetAnalysisData[]> {
    try {
      loading.value = true
      error.value = null
      const response = await api.get<BudgetAnalysisData[]>('/budget/analysis/project')
      return response
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to get project analysis'
      error.value = message
      console.error('Failed to get project analysis:', err)
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function getTrendAnalysis(period: string = 'month', months: number = 12): Promise<BudgetTrendData[]> {
    try {
      loading.value = true
      error.value = null
      const response = await api.get<BudgetTrendData[]>('/budget/analysis/trend', {
        params: { period, months }
      })
      return response
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to get trend analysis'
      error.value = message
      console.error('Failed to get trend analysis:', err)
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function getAllocationAnalysis(accountId: number): Promise<BudgetAllocationAnalysis> {
    try {
      loading.value = true
      error.value = null
      const response = await api.get<BudgetAllocationAnalysis>(`/budget/analysis/allocation/${accountId}`)
      return response
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to get allocation analysis'
      error.value = message
      console.error('Failed to get allocation analysis:', err)
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function getVarianceAnalysis(): Promise<BudgetVarianceAnalysis> {
    try {
      loading.value = true
      error.value = null
      const response = await api.get<BudgetVarianceAnalysis>('/budget/analysis/variance')
      return response
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to get variance analysis'
      error.value = message
      console.error('Failed to get variance analysis:', err)
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function exportBudgets(params: {
    format: 'pdf' | 'excel' | 'csv' | 'print'
    status?: string
    type?: string
    startDate?: string
    endDate?: string
    scope?: 'current' | 'all' | 'range'
    pageStart?: number
    pageEnd?: number
  }): Promise<Blob | string> {
    try {
      loading.value = true
      error.value = null

      // Prepare query parameters
      const queryParams: Record<string, any> = {
        format: params.format,
        status: params.status,
        type: params.type,
        startDate: params.startDate,
        endDate: params.endDate,
        scope: params.scope || 'current'
      }

      // Add pagination if scope is range
      if (params.scope === 'range' && params.pageStart !== undefined && params.pageEnd !== undefined) {
        queryParams.pageStart = params.pageStart
        queryParams.pageEnd = params.pageEnd
      }

      const response = await api.get<Blob>('/budget/export', {
        params: queryParams,
        responseType: 'blob'
      })

      // Handle different export formats
      const blob = new Blob([response as unknown as BlobPart], {
        type: params.format === 'pdf' 
          ? 'application/pdf' 
          : params.format === 'excel' 
            ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            : 'text/csv'
      })
      
      if (params.format === 'print') {
        return URL.createObjectURL(blob)
      }
      
      return blob
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to export budgets'
      error.value = message
      console.error('Failed to export budgets:', err)
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  // Helper function to format budget data for export
  function formatBudgetExportData(budget: BudgetResponse) {
    return {
      'Budget ID': budget.id,
      'Name': budget.name,
      'Description': budget.description || '',
      'Type': budget.budget_type,
      'Status': budget.status,
      'Start Date': budget.start_date,
      'End Date': budget.end_date,
      'Total Amount': budget.total_amount,
      'Created By': budget.created_by,
      'Created At': budget.created_at,
      'Updated At': budget.updated_at,
      'Updated By': budget.updated_by || ''
    } as Record<string, string | number | null | undefined>
  }

  // Reset store state
  function $reset() {
    budgets.value = []
    selectedBudget.value = null
    loading.value = false
    error.value = null
  }

  // Computed
  const budgetStatuses = computed(() => {
    return Object.entries(BudgetStatus).map(([key, value]) => ({
      label: key,
      value
    }))
  })

  const budgetTypes = computed(() => {
    return Object.entries(BudgetType).map(([key, value]) => ({
      label: key,
      value
    }))
  })

  // Filters
  const filters = ref({
    status: '' as BudgetStatus | '',
    type: '' as BudgetType | '',
    startDate: '',
    endDate: ''
  })

  // Reset filters
  function resetFilters() {
    filters.value = {
      status: '',
      type: '',
      startDate: '',
      endDate: ''
    }
  }

  return {
    // State
    budgets,
    selectedBudget,
    loading,
    error,
    pagination,
    filters,
    budgetStatuses,
    budgetTypes,
    loading,
    error,

    // Actions
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
    exportBudgets,
    formatBudgetExportData,
    $reset
  }
})
