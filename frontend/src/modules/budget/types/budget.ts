export interface BudgetLineItem {
  id: number
  budget_id: number
  category: string
  description: string
  amount: number
  created_at?: string
  updated_at?: string
}

export interface Budget {
  id: number
  name: string
  amount: number
  type: BudgetType
  status: BudgetStatus
  start_date: string
  end_date: string
  description?: string
  line_items: BudgetLineItem[]
  
  // Approval workflow fields
  submitted_at?: string
  approved_at?: string
  rejected_at?: string
  approval_notes?: string
  rejection_reason?: string
  
  // Audit fields
  created_at?: string
  updated_at?: string
  created_by?: number
}

export interface BudgetCreate {
  name: string
  amount: number
  type: BudgetType
  start_date: string
  end_date: string
  description?: string
  line_items?: Omit<BudgetLineItem, 'id' | 'budget_id'>[]
}

export interface BudgetUpdate {
  name?: string
  amount?: number
  type?: BudgetType
  status?: BudgetStatus
  start_date?: string
  end_date?: string
  description?: string
  line_items?: Omit<BudgetLineItem, 'id' | 'budget_id'>[]
}

export type BudgetType = 'OPERATIONAL' | 'CAPITAL' | 'PROJECT' | 'DEPARTMENT'

export type BudgetStatus = 'DRAFT' | 'PENDING_APPROVAL' | 'APPROVED' | 'REJECTED' | 'ARCHIVED'

export interface BudgetVsActualLineItem {
  category: string
  budgetAmount: number
  actualAmount: number
  variance: number
}

export interface BudgetVsActual {
  budgetId: string
  period: string
  budgetAmount: number
  actualAmount: number
  variance: number
  variancePercent: number
  lineItems: BudgetVsActualLineItem[]
}

export interface BudgetSummary {
  totalBudgets: number
  totalAmount: number
  totalSpent: number
  totalRemaining: number
  byStatus: Record<BudgetStatus, number>
  byType: Record<BudgetType, number>
}

export interface BudgetFilters {
  status?: BudgetStatus
  type?: BudgetType
  search?: string
  dateFrom?: string
  dateTo?: string
}