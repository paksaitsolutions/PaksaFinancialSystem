import { ref, computed } from 'vue'
import { useBudgetStore } from '../store/budget'
import { useGLStore } from '@/modules/general-ledger/store'
import { useAPStore } from '@/stores/ap'
import { useARStore } from '@/stores/ar'
import { useProcurementStore } from '@/stores/procurement'
import { usePayrollStore } from '@/stores/payroll'
import { useApi } from '@/composables/useApi'
import { BudgetStatus } from '../types/budget'

export function useBudgetIntegration() {
  const api = useApi()
  const budgetStore = useBudgetStore()
  const glStore = useGLStore()
  const apStore = useAPStore()
  const arStore = useARStore()
  const procurementStore = useProcurementStore()
  const payrollStore = usePayrollStore()

  // State
  const loading = ref(false)
  const error = ref(null)

  // Computed
  const activeBudgets = computed(() => {
    return budgetStore.budgets.filter(b => 
      b.status === BudgetStatus.APPROVED && 
      new Date(b.start_date) <= new Date() && 
      new Date(b.end_date) >= new Date()
    )
  })

  // Methods
  const checkBudgetAvailability = async (
    account_id: number,
    amount: number,
    department_id?: number,
    project_id?: number,
    date?: Date
  ) => {
    try {
      loading.value = true
      const response = await api.post('/budget/check-availability', {
        account_id,
        amount,
        department_id,
        project_id,
        date: date?.toISOString()
      })
      return response.data.available
    } catch (err) {
      error.value = err
      return false
    } finally {
      loading.value = false
    }
  }

  const allocateBudget = async (
    module: 'gl' | 'ap' | 'ar' | 'procurement' | 'payroll',
    moduleId: number,
    amount: number,
    account_id: number,
    department_id?: number,
    project_id?: number,
    description?: string
  ) => {
    try {
      loading.value = true
      const response = await api.post(`/budget/allocate/${module}`, {
        module_id: moduleId,
        amount,
        account_id,
        department_id,
        project_id,
        description
      })
      return response.data
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

  const getBudgetSpendingReport = async (
    account_id: number,
    department_id?: number,
    project_id?: number,
    start_date?: Date,
    end_date?: Date
  ) => {
    try {
      loading.value = true
      const response = await api.post('/budget/spending-report', {
        account_id,
        department_id,
        project_id,
        start_date: start_date?.toISOString(),
        end_date: end_date?.toISOString()
      })
      return response.data
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

  // Integration hooks
  const beforeGLEntryCreate = async (entry: any) => {
    if (!entry.budget_allocation_id && entry.amount > 0) {
      const available = await checkBudgetAvailability(
        entry.account_id,
        entry.amount,
        entry.department_id,
        entry.project_id
      )
      if (!available) {
        throw new Error('Insufficient budget allocation')
      }
    }
  }

  const afterGLEntryCreate = async (entry: any) => {
    if (entry.amount > 0) {
      await allocateBudget(
        'gl',
        entry.id,
        entry.amount,
        entry.account_id,
        entry.department_id,
        entry.project_id,
        `GL Entry: ${entry.description}`
      )
    }
  }

  const beforeAPInvoiceCreate = async (invoice: any) => {
    if (!invoice.budget_allocation_id && invoice.amount > 0) {
      const available = await checkBudgetAvailability(
        invoice.account_id,
        invoice.amount,
        invoice.department_id,
        invoice.project_id
      )
      if (!available) {
        throw new Error('Insufficient budget allocation')
      }
    }
  }

  const afterAPInvoiceCreate = async (invoice: any) => {
    if (invoice.amount > 0) {
      await allocateBudget(
        'ap',
        invoice.id,
        invoice.amount,
        invoice.account_id,
        invoice.department_id,
        invoice.project_id,
        `AP Invoice: ${invoice.number}`
      )
    }
  }

  const beforeARInvoiceCreate = async (invoice: any) => {
    if (!invoice.budget_allocation_id && invoice.amount > 0) {
      const available = await checkBudgetAvailability(
        invoice.account_id,
        invoice.amount,
        invoice.department_id,
        invoice.project_id
      )
      if (!available) {
        throw new Error('Insufficient budget allocation')
      }
    }
  }

  const afterARInvoiceCreate = async (invoice: any) => {
    if (invoice.amount > 0) {
      await allocateBudget(
        'ar',
        invoice.id,
        invoice.amount,
        invoice.account_id,
        invoice.department_id,
        invoice.project_id,
        `AR Invoice: ${invoice.number}`
      )
    }
  }

  const beforePurchaseOrderCreate = async (po: any) => {
    if (!po.budget_allocation_id && po.total_amount > 0) {
      const available = await checkBudgetAvailability(
        po.account_id,
        po.total_amount,
        po.department_id,
        po.project_id
      )
      if (!available) {
        throw new Error('Insufficient budget allocation')
      }
    }
  }

  const afterPurchaseOrderCreate = async (po: any) => {
    if (po.total_amount > 0) {
      await allocateBudget(
        'procurement',
        po.id,
        po.total_amount,
        po.account_id,
        po.department_id,
        po.project_id,
        `Purchase Order: ${po.number}`
      )
    }
  }

  const beforePayrollCreate = async (payroll: any) => {
    if (!payroll.budget_allocation_id && payroll.net_pay > 0) {
      const available = await checkBudgetAvailability(
        payroll.account_id,
        payroll.net_pay,
        payroll.department_id
      )
      if (!available) {
        throw new Error('Insufficient budget allocation')
      }
    }
  }

  const afterPayrollCreate = async (payroll: any) => {
    if (payroll.net_pay > 0) {
      await allocateBudget(
        'payroll',
        payroll.id,
        payroll.net_pay,
        payroll.account_id,
        payroll.department_id,
        null,
        `Payroll: ${payroll.employee_id}`
      )
    }
  }

  // Export hooks
  return {
    // Core functions
    checkBudgetAvailability,
    allocateBudget,
    getBudgetSpendingReport,

    // GL hooks
    beforeGLEntryCreate,
    afterGLEntryCreate,

    // AP hooks
    beforeAPInvoiceCreate,
    afterAPInvoiceCreate,

    // AR hooks
    beforeARInvoiceCreate,
    afterARInvoiceCreate,

    // Procurement hooks
    beforePurchaseOrderCreate,
    afterPurchaseOrderCreate,

    // Payroll hooks
    beforePayrollCreate,
    afterPayrollCreate,

    // State
    loading,
    error
  }
}
