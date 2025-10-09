/**
 * Tax service for API interactions
 */
import { api } from '@/utils/api'

export interface TaxRate {
  id: string
  name: string
  code: string
  rate: number
  tax_type: string
  jurisdiction: string
  country_code: string
  state_code?: string
  city?: string
  effective_date: string
  expiry_date?: string
  status: string
  description?: string
  created_at: string
  updated_at: string
}

export interface TaxCalculationRequest {
  amount: number
  tax_type: string
  jurisdiction: string
  country_code: string
  state_code?: string
  city?: string
  exemption_id?: string
}

export interface TaxCalculationResponse {
  taxable_amount: number
  tax_amount: number
  total_amount: number
  tax_rate: number
  tax_rate_id?: string
  tax_rate_name?: string
  exemption_applied: boolean
  exemption_certificate?: string
  error?: string
}

export interface TaxTransaction {
  id: string
  transaction_id: string
  entity_type: string
  entity_id: string
  taxable_amount: number
  tax_amount: number
  total_amount: number
  transaction_date: string
  description?: string
  reference?: string
  tax_rate: TaxRate
  created_at: string
}

export interface TaxExemption {
  id: string
  certificate_number: string
  entity_type: string
  entity_id: string
  exemption_type: string
  tax_types: string[]
  jurisdiction?: string
  issue_date: string
  expiry_date?: string
  status: string
  issuing_authority?: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface TaxSummary {
  period: {
    start_date: string
    end_date: string
  }
  summary: {
    total_taxable_amount: number
    total_tax_amount: number
    transaction_count: number
  }
  by_tax_type: Record<string, {
    taxable_amount: number
    tax_amount: number
    transaction_count: number
  }>
}

class TaxService {
  // Tax Calculations
  async calculateTax(request: TaxCalculationRequest): Promise<TaxCalculationResponse> {
    const response = await api.post('/tax/calculate', request)
    return response.data
  }

  // Tax Rates
  async getTaxRates(params?: {
    tax_type?: string
    jurisdiction?: string
    active_only?: boolean
  }): Promise<TaxRate[]> {
    const response = await api.get('/tax/rates', { params })
    return response.data
  }

  async getTaxRate(id: string): Promise<TaxRate> {
    const response = await api.get(`/tax/rates/${id}`)
    return response.data
  }

  async createTaxRate(data: Omit<TaxRate, 'id' | 'status' | 'created_at' | 'updated_at'>): Promise<TaxRate> {
    const response = await api.post('/tax/rates', data)
    return response.data
  }

  async updateTaxRate(id: string, data: Partial<TaxRate>): Promise<TaxRate> {
    const response = await api.put(`/tax/rates/${id}`, data)
    return response.data
  }

  async deleteTaxRate(id: string): Promise<{ message: string }> {
    const response = await api.delete(`/tax/rates/${id}`)
    return response.data
  }

  // Tax Transactions
  async getTaxTransactions(params?: {
    entity_type?: string
    entity_id?: string
    start_date?: string
    end_date?: string
    limit?: number
  }): Promise<TaxTransaction[]> {
    const response = await api.get('/tax/transactions', { params })
    return response.data
  }

  // Tax Exemptions
  async getTaxExemptions(params?: {
    entity_type?: string
    entity_id?: string
    active_only?: boolean
  }): Promise<TaxExemption[]> {
    const response = await api.get('/tax/exemptions', { params })
    return response.data
  }

  async createTaxExemption(data: Omit<TaxExemption, 'id' | 'status' | 'created_at' | 'updated_at'>): Promise<TaxExemption> {
    const response = await api.post('/tax/exemptions', data)
    return response.data
  }

  // Tax Summary
  async getTaxSummary(params: {
    start_date: string
    end_date: string
    tax_type?: string
  }): Promise<TaxSummary> {
    const response = await api.get('/tax/summary', { params })
    return response.data
  }

  // Utility methods
  formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  formatPercentage(rate: number): string {
    return `${rate.toFixed(2)}%`
  }

  getTaxTypeLabel(taxType: string): string {
    const labels: Record<string, string> = {
      sales: 'Sales Tax',
      vat: 'VAT',
      gst: 'GST',
      income: 'Income Tax',
      property: 'Property Tax',
      excise: 'Excise Tax',
      customs: 'Customs Duty'
    }
    return labels[taxType] || taxType
  }

  getStatusColor(status: string): string {
    const colors: Record<string, string> = {
      active: 'success',
      inactive: 'secondary',
      pending: 'warning',
      expired: 'danger'
    }
    return colors[status] || 'secondary'
  }
}

export const taxService = new TaxService()
export default taxService