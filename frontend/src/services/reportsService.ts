import { api } from '@/utils/api'

export interface Report {
  id: string
  name: string
  type: string
  module: string
  description?: string
  parameters?: Record<string, any>
  created_at: string
  updated_at: string
  created_by: string
  is_scheduled: boolean
  schedule?: ReportSchedule
}

export interface ReportSchedule {
  id: string
  report_id: string
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly'
  time: string
  day_of_week?: number
  day_of_month?: number
  is_active: boolean
  next_run: string
  last_run?: string
}

export interface ReportExecution {
  id: string
  report_id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  started_at: string
  completed_at?: string
  file_url?: string
  file_size?: number
  error_message?: string
  executed_by: string
}

export interface ReportModule {
  id: string
  name: string
  icon: string
  color: string
  report_count: number
  reports: Report[]
}

export interface ReportStats {
  total_reports: number
  scheduled_reports: number
  reports_this_month: number
  active_users: number
  executions_today: number
  failed_executions: number
}

export interface ReportActivity {
  id: string
  timestamp: string
  user: string
  action: 'generated' | 'scheduled' | 'exported' | 'failed' | 'cancelled'
  report_name: string
  module: string
  status: 'completed' | 'active' | 'failed' | 'pending'
  execution_time?: number
}

export interface FinancialReport {
  id: string
  type: 'balance_sheet' | 'income_statement' | 'cash_flow' | 'trial_balance'
  period_start: string
  period_end: string
  data: any
  generated_at: string
}

class ReportsService {
  // Dashboard
  async getReportStats(): Promise<ReportStats> {
    const response = await api.get('/reports/stats')
    return response.data
  }

  async getReportModules(): Promise<ReportModule[]> {
    const response = await api.get('/reports/modules')
    return response.data
  }

  async getRecentActivity(limit: number = 10): Promise<ReportActivity[]> {
    const response = await api.get(`/reports/activity?limit=${limit}`)
    return response.data
  }

  // Reports Management
  async getReports(params?: {
    module?: string
    type?: string
    page?: number
    limit?: number
  }): Promise<{ reports: Report[], total: number }> {
    const response = await api.get('/reports', { params })
    return response.data
  }

  async getReport(id: string): Promise<Report> {
    const response = await api.get(`/reports/${id}`)
    return response.data
  }

  async createReport(report: Omit<Report, 'id' | 'created_at' | 'updated_at' | 'created_by'>): Promise<Report> {
    const response = await api.post('/reports', report)
    return response.data
  }

  async updateReport(id: string, report: Partial<Report>): Promise<Report> {
    const response = await api.put(`/reports/${id}`, report)
    return response.data
  }

  async deleteReport(id: string): Promise<void> {
    await api.delete(`/reports/${id}`)
  }

  // Report Execution
  async executeReport(id: string, parameters?: Record<string, any>): Promise<ReportExecution> {
    const response = await api.post(`/reports/${id}/execute`, { parameters })
    return response.data
  }

  async getReportExecution(executionId: string): Promise<ReportExecution> {
    const response = await api.get(`/reports/executions/${executionId}`)
    return response.data
  }

  async getReportExecutions(reportId?: string): Promise<ReportExecution[]> {
    const params = reportId ? { report_id: reportId } : {}
    const response = await api.get('/reports/executions', { params })
    return response.data
  }

  async downloadReport(executionId: string): Promise<Blob> {
    const response = await api.get(`/reports/executions/${executionId}/download`, {
      responseType: 'blob'
    })
    return response.data
  }

  // Scheduling
  async getScheduledReports(): Promise<ReportSchedule[]> {
    const response = await api.get('/reports/schedules')
    return response.data
  }

  async createSchedule(schedule: Omit<ReportSchedule, 'id' | 'next_run' | 'last_run'>): Promise<ReportSchedule> {
    const response = await api.post('/reports/schedules', schedule)
    return response.data
  }

  async updateSchedule(id: string, schedule: Partial<ReportSchedule>): Promise<ReportSchedule> {
    const response = await api.put(`/reports/schedules/${id}`, schedule)
    return response.data
  }

  async deleteSchedule(id: string): Promise<void> {
    await api.delete(`/reports/schedules/${id}`)
  }

  async pauseSchedule(id: string): Promise<ReportSchedule> {
    const response = await api.post(`/reports/schedules/${id}/pause`)
    return response.data
  }

  async resumeSchedule(id: string): Promise<ReportSchedule> {
    const response = await api.post(`/reports/schedules/${id}/resume`)
    return response.data
  }

  // Financial Reports
  async generateBalanceSheet(params: {
    as_of_date: string
    comparison_date?: string
    include_details?: boolean
  }): Promise<FinancialReport> {
    const response = await api.post('/reports/financial/balance-sheet', params)
    return response.data
  }

  async generateIncomeStatement(params: {
    period_start: string
    period_end: string
    comparison_period_start?: string
    comparison_period_end?: string
    include_details?: boolean
  }): Promise<FinancialReport> {
    const response = await api.post('/reports/financial/income-statement', params)
    return response.data
  }

  async generateCashFlowStatement(params: {
    period_start: string
    period_end: string
    method?: 'direct' | 'indirect'
  }): Promise<FinancialReport> {
    const response = await api.post('/reports/financial/cash-flow', params)
    return response.data
  }

  async generateTrialBalance(params: {
    as_of_date: string
    include_zero_balances?: boolean
  }): Promise<FinancialReport> {
    const response = await api.post('/reports/financial/trial-balance', params)
    return response.data
  }

  // Aging Reports
  async generateAPAging(params: {
    as_of_date: string
    aging_periods?: number[]
    vendor_ids?: string[]
  }): Promise<any> {
    const response = await api.post('/reports/aging/ap', params)
    return response.data
  }

  async generateARAging(params: {
    as_of_date: string
    aging_periods?: number[]
    customer_ids?: string[]
  }): Promise<any> {
    const response = await api.post('/reports/aging/ar', params)
    return response.data
  }

  // Operational Reports
  async generateInventoryReport(params: {
    report_type: 'valuation' | 'movement' | 'reorder' | 'abc_analysis'
    period_start?: string
    period_end?: string
    location_ids?: string[]
  }): Promise<any> {
    const response = await api.post('/reports/operational/inventory', params)
    return response.data
  }

  async generatePayrollReport(params: {
    report_type: 'summary' | 'earnings' | 'taxes' | 'benefits'
    period_start: string
    period_end: string
    employee_ids?: string[]
    department?: string
  }): Promise<any> {
    const response = await api.post('/reports/operational/payroll', params)
    return response.data
  }

  // Tax Reports
  async generateTaxReport(params: {
    report_type: 'liability' | 'compliance' | 'returns'
    period_start: string
    period_end: string
    jurisdiction_id?: string
  }): Promise<any> {
    const response = await api.post('/reports/tax', params)
    return response.data
  }

  // Custom Reports
  async getReportTemplates(): Promise<any[]> {
    const response = await api.get('/reports/templates')
    return response.data
  }

  async createCustomReport(params: {
    name: string
    description?: string
    query: string
    parameters?: Record<string, any>
    visualization?: any
  }): Promise<Report> {
    const response = await api.post('/reports/custom', params)
    return response.data
  }

  async executeCustomReport(id: string, parameters?: Record<string, any>): Promise<any> {
    const response = await api.post(`/reports/custom/${id}/execute`, { parameters })
    return response.data
  }

  // Export
  async exportReport(executionId: string, format: 'pdf' | 'excel' | 'csv'): Promise<Blob> {
    const response = await api.get(`/reports/executions/${executionId}/export?format=${format}`, {
      responseType: 'blob'
    })
    return response.data
  }
}

export const reportsService = new ReportsService()