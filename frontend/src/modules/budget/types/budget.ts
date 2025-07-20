export enum BudgetStatus {
  DRAFT = 'draft',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  ARCHIVED = 'archived'
}

export enum BudgetType {
  OPERATIONAL = 'operational',
  CAPITAL = 'capital',
  PROJECT = 'project',
  DEPARTMENT = 'department'
}

export interface BudgetLine {
  id: number
  account_id: number
  department_id?: number
  project_id?: number
  amount: number
  description?: string
  created_at: string
  updated_at: string
}

export interface BudgetAllocation {
  id: number
  department_id?: number
  project_id?: number
  amount: number
  percentage?: number
  description?: string
  created_at: string
  updated_at: string
}

export interface BudgetRule {
  id: number
  rule_type: string
  rule_data: Record<string, any>
  description?: string
  created_at: string
  updated_at: string
}

export interface BudgetApproval {
  id: number
  approver_id: string
  approved_at: string
  notes?: string
}

export interface BudgetResponse {
  id: number
  name: string
  description?: string
  budget_type: BudgetType
  status: BudgetStatus
  start_date: string
  end_date: string
  total_amount: number
  created_at: string
  updated_at: string
  created_by: string
  updated_by?: string
  lines: BudgetLine[]
  allocations: BudgetAllocation[]
  rules: BudgetRule[]
  approvals: BudgetApproval[]
}

export interface BudgetListResponse {
  budgets: BudgetResponse[]
  total: number
  page: number
  limit: number
}

export interface BudgetCreate {
  name: string
  description?: string
  budget_type: BudgetType
  start_date: string
  end_date: string
  total_amount: number
  lines: BudgetLine[]
  allocations: BudgetAllocation[]
  rules: BudgetRule[]
}

export interface BudgetUpdate {
  name?: string
  description?: string
  budget_type?: BudgetType
  start_date?: string
  end_date?: string
  total_amount?: number
  status?: BudgetStatus
  lines?: BudgetLine[]
  allocations?: BudgetAllocation[]
  rules?: BudgetRule[]
}

export interface BudgetApprovalCreate {
  notes?: string
}

export interface BudgetFilters {
  status?: BudgetStatus
  type?: BudgetType
  startDate?: string
  endDate?: string
  departmentId?: number
  projectId?: number
}

export interface BudgetPerformance {
  budgeted_amount: number
  actual_amount: number
  variance: number
  variance_percentage: number
}

export interface BudgetAnalysisData {
  id: number
  name: string
  budgeted: number
  actual: number
  variance: number
  variance_percentage: number
}

export interface BudgetTrendData {
  period: string
  budgeted_amount: number
  actual_amount: number
  variance: number
  variance_percentage: number
}

export interface BudgetAllocationAnalysis {
  total_budgeted: number
  department_allocations: Array<{
    department_id: number
    amount: number
    percentage: number
  }>
  project_allocations: Array<{
    project_id: number
    amount: number
    percentage: number
  }>
}

export interface BudgetVarianceAnalysis {
  overall: {
    budgeted: number
    actual: number
    variance: number
    variance_percentage: number
  }
  by_department: Record<number, {
    budgeted: number
    actual: number
    variance: number
    variance_percentage: number
  }>
  by_project: Record<number, {
    budgeted: number
    actual: number
    variance: number
    variance_percentage: number
  }>
  by_account: Record<number, {
    budgeted: number
    actual: number
    variance: number
    variance_percentage: number
  }>
}
