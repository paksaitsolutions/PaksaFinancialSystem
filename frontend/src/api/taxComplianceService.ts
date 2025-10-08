/**
 * Tax Compliance API Service
 */
import axios from 'axios'

const API_BASE = '/api/v1/tax/compliance'

export interface ComplianceOverview {
  total_checks: number
  passed_checks: number
  failed_checks: number
  warning_checks: number
  compliance_score: number
  last_check: string
  next_check: string
  active_alerts: number
}

export interface ComplianceAlert {
  id: string
  title: string
  description: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  status: 'open' | 'acknowledged' | 'resolved'
  entity_type: string
  entity_id: string
  created_at: string
  resolved_at?: string
}

export interface ComplianceRule {
  id: string
  name: string
  description: string
  check_type: string
  jurisdiction: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface TaxJurisdiction {
  id: string
  name: string
  code: string
  country: string
  state?: string
  tax_types: string[]
  compliance_requirements: string[]
  filing_frequency: string
  next_filing_date?: string
}

export interface ComplianceCheckRequest {
  check_type: string
  entity_id: string
  entity_type: string
  jurisdiction: string
  check_data: Record<string, any>
  rules?: string[]
  priority?: string
}

export interface ComplianceScoreReport {
  overall_score: number
  period: {
    start_date: string
    end_date: string
  }
  jurisdiction_scores: Array<{
    jurisdiction: string
    score: number
    checks: number
    issues: number
  }>
  trend: Array<{
    date: string
    score: number
  }>
}

export interface FilingCalendar {
  year: number
  jurisdiction?: string
  filings: Array<{
    id: string
    title: string
    jurisdiction: string
    due_date: string
    status: string
    type: string
    estimated_amount: number
  }>
}

class TaxComplianceService {
  /**
   * Get compliance overview dashboard data
   */
  async getOverview(): Promise<ComplianceOverview> {
    const response = await axios.get(`${API_BASE}/overview`)
    return response.data
  }

  /**
   * Get compliance alerts
   */
  async getAlerts(filters?: {
    status?: string
    severity?: string
    limit?: number
  }): Promise<ComplianceAlert[]> {
    const params = new URLSearchParams()
    if (filters?.status) params.append('status_filter', filters.status)
    if (filters?.severity) params.append('severity', filters.severity)
    if (filters?.limit) params.append('limit', filters.limit.toString())

    const response = await axios.get(`${API_BASE}/alerts?${params}`)
    return response.data
  }

  /**
   * Get compliance rules
   */
  async getRules(filters?: {
    jurisdiction?: string
    check_type?: string
    is_active?: boolean
  }): Promise<ComplianceRule[]> {
    const params = new URLSearchParams()
    if (filters?.jurisdiction) params.append('jurisdiction', filters.jurisdiction)
    if (filters?.check_type) params.append('check_type', filters.check_type)
    if (filters?.is_active !== undefined) params.append('is_active', filters.is_active.toString())

    const response = await axios.get(`${API_BASE}/rules?${params}`)
    return response.data
  }

  /**
   * Get tax jurisdictions
   */
  async getJurisdictions(country?: string): Promise<TaxJurisdiction[]> {
    const params = new URLSearchParams()
    if (country) params.append('country', country)

    const response = await axios.get(`${API_BASE}/jurisdictions?${params}`)
    return response.data
  }

  /**
   * Run a compliance check
   */
  async runComplianceCheck(request: ComplianceCheckRequest): Promise<any> {
    const response = await axios.post(`${API_BASE}/check`, request)
    return response.data
  }

  /**
   * Resolve a compliance alert
   */
  async resolveAlert(alertId: string, resolutionNotes?: string): Promise<any> {
    const response = await axios.put(`${API_BASE}/alerts/${alertId}/resolve`, {
      resolution_notes: resolutionNotes
    })
    return response.data
  }

  /**
   * Get compliance score report
   */
  async getComplianceScoreReport(filters?: {
    start_date?: string
    end_date?: string
    jurisdiction?: string
  }): Promise<ComplianceScoreReport> {
    const params = new URLSearchParams()
    if (filters?.start_date) params.append('start_date', filters.start_date)
    if (filters?.end_date) params.append('end_date', filters.end_date)
    if (filters?.jurisdiction) params.append('jurisdiction', filters.jurisdiction)

    const response = await axios.get(`${API_BASE}/reports/compliance-score?${params}`)
    return response.data
  }

  /**
   * Get tax filing calendar
   */
  async getFilingCalendar(year?: number, jurisdiction?: string): Promise<FilingCalendar> {
    const params = new URLSearchParams()
    if (year) params.append('year', year.toString())
    if (jurisdiction) params.append('jurisdiction', jurisdiction)

    const response = await axios.get(`${API_BASE}/reports/filing-calendar?${params}`)
    return response.data
  }

  /**
   * Create a new compliance rule
   */
  async createRule(rule: Omit<ComplianceRule, 'id' | 'created_at' | 'updated_at'>): Promise<ComplianceRule> {
    const response = await axios.post(`${API_BASE}/rules`, rule)
    return response.data
  }

  /**
   * Update a compliance rule
   */
  async updateRule(ruleId: string, updates: Partial<ComplianceRule>): Promise<ComplianceRule> {
    const response = await axios.put(`${API_BASE}/rules/${ruleId}`, updates)
    return response.data
  }

  /**
   * Delete a compliance rule
   */
  async deleteRule(ruleId: string): Promise<void> {
    await axios.delete(`${API_BASE}/rules/${ruleId}`)
  }

  /**
   * Get compliance history for an entity
   */
  async getComplianceHistory(entityId: string, entityType: string): Promise<any[]> {
    const response = await axios.get(`${API_BASE}/history/${entityType}/${entityId}`)
    return response.data
  }

  /**
   * Export compliance report
   */
  async exportReport(format: 'pdf' | 'excel' | 'csv', filters?: {
    start_date?: string
    end_date?: string
    jurisdiction?: string
    report_type?: string
  }): Promise<Blob> {
    const params = new URLSearchParams()
    params.append('format', format)
    if (filters?.start_date) params.append('start_date', filters.start_date)
    if (filters?.end_date) params.append('end_date', filters.end_date)
    if (filters?.jurisdiction) params.append('jurisdiction', filters.jurisdiction)
    if (filters?.report_type) params.append('report_type', filters.report_type)

    const response = await axios.get(`${API_BASE}/export?${params}`, {
      responseType: 'blob'
    })
    return response.data
  }

  /**
   * Get compliance dashboard metrics
   */
  async getDashboardMetrics(period?: string): Promise<{
    compliance_score: number
    total_checks: number
    failed_checks: number
    active_alerts: number
    upcoming_deadlines: number
    score_trend: Array<{ date: string; score: number }>
  }> {
    const params = new URLSearchParams()
    if (period) params.append('period', period)

    const response = await axios.get(`${API_BASE}/dashboard/metrics?${params}`)
    return response.data
  }

  /**
   * Schedule a compliance check
   */
  async scheduleCheck(schedule: {
    check_type: string
    entity_id: string
    entity_type: string
    jurisdiction: string
    frequency: string
    next_run: string
    rules?: string[]
  }): Promise<any> {
    const response = await axios.post(`${API_BASE}/schedule`, schedule)
    return response.data
  }

  /**
   * Get scheduled compliance checks
   */
  async getScheduledChecks(): Promise<any[]> {
    const response = await axios.get(`${API_BASE}/scheduled`)
    return response.data
  }

  /**
   * Update compliance settings
   */
  async updateSettings(settings: {
    auto_check_frequency?: string
    enable_notifications?: boolean
    realtime_monitoring?: boolean
    alert_thresholds?: Record<string, number>
  }): Promise<any> {
    const response = await axios.put(`${API_BASE}/settings`, settings)
    return response.data
  }

  /**
   * Get compliance settings
   */
  async getSettings(): Promise<any> {
    const response = await axios.get(`${API_BASE}/settings`)
    return response.data
  }
}

export const taxComplianceService = new TaxComplianceService()
export default taxComplianceService