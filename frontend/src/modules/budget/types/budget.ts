export interface Budget {
  id?: string
  name: string
  description: string
  fiscal_year: number
  start_date: string
  end_date: string
  status: 'draft' | 'active' | 'pending_approval' | 'approved' | 'closed'
  line_items: BudgetLineItem[]
  total_budget?: number
  total_actual?: number
  variance?: number
  created_at?: string
  updated_at?: string
  created_by?: string
  approved_by?: string
  approved_at?: string
}

export interface BudgetLineItem {
  id?: string
  budget_id?: string
  account_code: string
  account_name: string
  category: string
  budgeted_amount: number
  actual_amount: number
  variance: number
  period_type: 'monthly' | 'quarterly' | 'annual'
  department?: string
  cost_center?: string
  project_code?: string
}

export interface BudgetTemplate {
  id: string
  name: string
  description: string
  category: string
  template_data: Budget
  is_active: boolean
  created_at: string
}

export interface BudgetAnalytics {
  total_budgets: number
  active_budgets: number
  budget_utilization: number
  variance_percentage: number
  top_variances: BudgetVariance[]
  budget_performance: {
    on_track: number
    over_budget: number
    under_budget: number
  }
}

export interface BudgetVariance {
  account: string
  variance: number
  percentage: number
  category: string
}

export interface BudgetForecast {
  budget_id: string
  forecast_period: string
  projected_total: number
  confidence_score: number
  monthly_projections: MonthlyProjection[]
  risk_factors: string[]
}

export interface MonthlyProjection {
  month: string
  projected_actual: number
  confidence: number
  factors: string[]
}

export interface BudgetApproval {
  budget_id: string
  status: 'pending' | 'approved' | 'rejected'
  approver_id: string
  approved_at?: string
  approval_notes?: string
  approval_level: number
}

export interface BudgetComparison {
  current_budget: Budget
  previous_budget?: Budget
  variance_analysis: {
    total_variance: number
    variance_percentage: number
    category_variances: Array<{
      category: string
      current_amount: number
      previous_amount: number
      variance: number
      percentage: number
    }>
  }
}