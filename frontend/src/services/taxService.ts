import { api } from '@/utils/api'

export interface TaxJurisdiction {
  id: number
  name: string
  code: string
  level: 'federal' | 'state' | 'county' | 'city'
  parent_id?: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface TaxRate {
  id: number
  jurisdiction_id: number
  jurisdiction_name: string
  tax_type: 'sales' | 'vat' | 'income' | 'property' | 'excise'
  rate: number
  effective_date: string
  expiry_date?: string
  is_active: boolean
  description?: string
}

export interface TaxTransaction {
  id: number
  entity_type: 'customer' | 'vendor' | 'employee'
  entity_id: number
  entity_name: string
  transaction_date: string
  taxable_amount: number
  tax_amount: number
  total_amount: number
  tax_rate_id: number
  tax_rate: number
  jurisdiction_id: number
  jurisdiction_name: string
  reference_number?: string
  description?: string
  created_at: string
}

export interface TaxExemption {
  id: number
  entity_type: 'customer' | 'vendor'
  entity_id: number
  entity_name: string
  exemption_type: 'resale' | 'nonprofit' | 'government' | 'other'
  certificate_number: string
  jurisdiction_id: number
  jurisdiction_name: string
  effective_date: string
  expiry_date?: string
  is_active: boolean
  notes?: string
}

export interface TaxReturn {
  id: number
  jurisdiction_id: number
  jurisdiction_name: string
  period_start: string
  period_end: string
  filing_frequency: 'monthly' | 'quarterly' | 'annually'
  due_date: string
  status: 'draft' | 'submitted' | 'approved' | 'rejected'
  total_sales: number
  taxable_sales: number
  tax_collected: number
  tax_due: number
  filed_date?: string
  confirmation_number?: string
  notes?: string
}

export interface TaxSummary {
  period_start: string
  period_end: string
  summary: {
    total_transactions: number
    total_taxable_amount: number
    total_tax_amount: number
    total_amount: number
  }
  by_jurisdiction: {
    jurisdiction_name: string
    transaction_count: number
    taxable_amount: number
    tax_amount: number
  }[]
  by_tax_type: {
    tax_type: string
    transaction_count: number
    taxable_amount: number
    tax_amount: number
  }[]
}

export interface TaxKPIs {
  total_liability: number
  liability_change: number
  active_tax_codes: number
  pending_returns: number
  days_until_due: number
  compliance_score: number
}

class TaxService {
  // Dashboard
  async getTaxKPIs(): Promise<TaxKPIs> {
    const response = await api.get('/tax/dashboard/kpis')
    return response.data
  }

  async getTaxSummary(params: {
    start_date: string
    end_date: string
    jurisdiction_id?: number
  }): Promise<TaxSummary> {
    const response = await api.get('/tax/summary', { params })
    return response.data
  }

  // Jurisdictions
  async getJurisdictions(level?: string): Promise<TaxJurisdiction[]> {
    const params = level ? { level } : {}
    const response = await api.get('/tax/jurisdictions', { params })
    return response.data
  }

  async createJurisdiction(jurisdiction: Omit<TaxJurisdiction, 'id' | 'is_active' | 'created_at' | 'updated_at'>): Promise<TaxJurisdiction> {
    const response = await api.post('/tax/jurisdictions', jurisdiction)
    return response.data
  }

  async updateJurisdiction(id: number, jurisdiction: Partial<TaxJurisdiction>): Promise<TaxJurisdiction> {
    const response = await api.put(`/tax/jurisdictions/${id}`, jurisdiction)
    return response.data
  }

  async deleteJurisdiction(id: number): Promise<void> {
    await api.delete(`/tax/jurisdictions/${id}`)
  }

  // Tax Rates
  async getTaxRates(params?: {
    tax_type?: string
    active_only?: boolean
    jurisdiction_id?: number
  }): Promise<TaxRate[]> {
    const response = await api.get('/tax/rates', { params })
    return response.data
  }

  async createTaxRate(rate: Omit<TaxRate, 'id' | 'jurisdiction_name' | 'is_active'>): Promise<TaxRate> {
    const response = await api.post('/tax/rates', rate)
    return response.data
  }

  async updateTaxRate(id: number, rate: Partial<TaxRate>): Promise<TaxRate> {
    const response = await api.put(`/tax/rates/${id}`, rate)
    return response.data
  }

  async deleteRate(id: number): Promise<void> {
    await api.delete(`/tax/rates/${id}`)
  }

  // Tax Transactions
  async getTaxTransactions(params?: {
    page?: number
    limit?: number
    entity_type?: string
    start_date?: string
    end_date?: string
  }): Promise<TaxTransaction[]> {
    const response = await api.get('/tax/transactions', { params })
    return response.data
  }

  async createTaxTransaction(transaction: Omit<TaxTransaction, 'id' | 'entity_name' | 'jurisdiction_name' | 'created_at'>): Promise<TaxTransaction> {
    const response = await api.post('/tax/transactions', transaction)
    return response.data
  }

  async calculateTax(params: {
    taxable_amount: number
    tax_rate_id: number
    jurisdiction_id?: number
  }): Promise<{
    taxable_amount: number
    tax_amount: number
    total_amount: number
    tax_rate: number
  }> {
    const response = await api.post('/tax/calculate', params)
    return response.data
  }

  // Tax Exemptions
  async getTaxExemptions(params?: {
    entity_type?: string
    active_only?: boolean
  }): Promise<TaxExemption[]> {
    const response = await api.get('/tax/exemptions', { params })
    return response.data
  }

  async createTaxExemption(exemption: Omit<TaxExemption, 'id' | 'entity_name' | 'jurisdiction_name' | 'is_active'>): Promise<TaxExemption> {
    const response = await api.post('/tax/exemptions', exemption)
    return response.data
  }

  async updateTaxExemption(id: number, exemption: Partial<TaxExemption>): Promise<TaxExemption> {
    const response = await api.put(`/tax/exemptions/${id}`, exemption)
    return response.data
  }

  async deleteExemption(id: number): Promise<void> {
    await api.delete(`/tax/exemptions/${id}`)
  }

  // Tax Returns
  async getTaxReturns(params?: {
    jurisdiction_id?: number
    status?: string
    start_date?: string
    end_date?: string
  }): Promise<TaxReturn[]> {
    const response = await api.get('/tax/returns', { params })
    return response.data
  }

  async createTaxReturn(taxReturn: Omit<TaxReturn, 'id' | 'jurisdiction_name'>): Promise<TaxReturn> {
    const response = await api.post('/tax/returns', taxReturn)
    return response.data
  }

  async updateTaxReturn(id: number, taxReturn: Partial<TaxReturn>): Promise<TaxReturn> {
    const response = await api.put(`/tax/returns/${id}`, taxReturn)
    return response.data
  }

  async submitTaxReturn(id: number): Promise<TaxReturn> {
    const response = await api.post(`/tax/returns/${id}/submit`)
    return response.data
  }

  async getUpcomingDeadlines(): Promise<{
    id: number
    description: string
    jurisdiction: string
    due_date: string
    days_remaining: number
    status: string
  }[]> {
    const response = await api.get('/tax/deadlines/upcoming')
    return response.data
  }

  // Reports
  async getTaxLiabilityReport(params: {
    start_date: string
    end_date: string
    jurisdiction_id?: number
  }): Promise<{
    total_liability: number
    by_period: { period: string, amount: number }[]
    by_jurisdiction: { jurisdiction: string, amount: number }[]
    by_tax_type: { tax_type: string, amount: number }[]
  }> {
    const response = await api.get('/tax/reports/liability', { params })
    return response.data
  }

  async getTaxComplianceReport(): Promise<{
    compliance_score: number
    filed_on_time: number
    filed_late: number
    pending_filings: number
    overdue_filings: number
    recent_filings: TaxReturn[]
  }> {
    const response = await api.get('/tax/reports/compliance')
    return response.data
  }

  // Import/Export
  async importTaxData(file: File, type: 'transactions' | 'rates' | 'exemptions'): Promise<{
    success: number
    errors: string[]
  }> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('type', type)
    const response = await api.post('/tax/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  }

  async exportTaxData(type: 'transactions' | 'rates' | 'exemptions', format: 'csv' | 'excel' = 'csv'): Promise<Blob> {
    const response = await api.get(`/tax/export/${type}?format=${format}`, {
      responseType: 'blob'
    })
    return response.data
  }
}

export default new TaxService()