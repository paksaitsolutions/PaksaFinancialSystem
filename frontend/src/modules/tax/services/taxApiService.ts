import axios from 'axios'
import {
  TaxTransaction,
  TaxRate,
  TaxJurisdiction,
  TaxExemption,
  TaxReturn,
  SalesTaxNexus,
  TaxAutomationRule,
  TaxEFilingIntegration,
  TaxPaymentSchedule
} from '../types/tax'

const API_BASE = '/api/v1/tax'

export class TaxApiService {
  // Tax Jurisdictions
  async getJurisdictions(level?: string): Promise<TaxJurisdiction[]> {
    const params = level ? { level } : {}
    const response = await axios.get(`${API_BASE}/jurisdictions/`, { params })
    return response.data
  }

  async createJurisdiction(jurisdiction: Omit<TaxJurisdiction, 'id' | 'is_active'>): Promise<TaxJurisdiction> {
    const response = await axios.post(`${API_BASE}/jurisdictions/`, jurisdiction)
    return response.data
  }

  async getJurisdiction(id: number): Promise<TaxJurisdiction> {
    const response = await axios.get(`${API_BASE}/jurisdictions/${id}`)
    return response.data
  }

  // Tax Rates
  async getTaxRates(taxType?: string, activeOnly: boolean = true): Promise<TaxRate[]> {
    const params = { tax_type: taxType, active_only: activeOnly }
    const response = await axios.get(`${API_BASE}/rates/`, { params })
    return response.data
  }

  async createTaxRate(rate: Omit<TaxRate, 'id' | 'is_active'>): Promise<TaxRate> {
    const response = await axios.post(`${API_BASE}/rates/`, rate)
    return response.data
  }

  async getRateForJurisdiction(
    jurisdictionId: number, 
    taxType: string, 
    effectiveDate?: string
  ): Promise<TaxRate> {
    const params = { tax_type: taxType, effective_date: effectiveDate }
    const response = await axios.get(`${API_BASE}/rates/jurisdiction/${jurisdictionId}`, { params })
    return response.data
  }

  // Tax Transactions
  async getTaxTransactions(skip: number = 0, limit: number = 100): Promise<TaxTransaction[]> {
    const params = { skip, limit }
    const response = await axios.get(`${API_BASE}/transactions/`, { params })
    return response.data
  }

  async createTaxTransaction(transaction: Omit<TaxTransaction, 'id'>): Promise<TaxTransaction> {
    const response = await axios.post(`${API_BASE}/transactions/`, transaction)
    return response.data
  }

  async getTaxTransaction(id: number): Promise<TaxTransaction> {
    const response = await axios.get(`${API_BASE}/transactions/${id}`)
    return response.data
  }

  async calculateTax(taxableAmount: number, taxRateId: number): Promise<{
    taxable_amount: number;
    tax_amount: number;
    total_amount: number;
  }> {
    const response = await axios.post(`${API_BASE}/transactions/calculate`, {
      taxable_amount: taxableAmount,
      tax_rate_id: taxRateId
    })
    return response.data
  }

  // Tax Exemptions
  async getTaxExemptions(activeOnly: boolean = true): Promise<TaxExemption[]> {
    const params = { active_only: activeOnly }
    const response = await axios.get(`${API_BASE}/exemptions/`, { params })
    return response.data
  }

  async createTaxExemption(exemption: Omit<TaxExemption, 'id' | 'is_active'>): Promise<TaxExemption> {
    const response = await axios.post(`${API_BASE}/exemptions/`, exemption)
    return response.data
  }

  // Tax Returns
  async getTaxReturns(startDate?: string, endDate?: string): Promise<TaxReturn[]> {
    const params = { start_date: startDate, end_date: endDate }
    const response = await axios.get(`${API_BASE}/returns/`, { params })
    return response.data
  }

  async createTaxReturn(taxReturn: Omit<TaxReturn, 'id' | 'is_active'>): Promise<TaxReturn> {
    const response = await axios.post(`${API_BASE}/returns/`, taxReturn)
    return response.data
  }

  async getTaxReturn(id: number): Promise<TaxReturn> {
    const response = await axios.get(`${API_BASE}/returns/${id}`)
    return response.data
  }

  // Sales Tax Nexus
  async getSalesTaxNexus(): Promise<SalesTaxNexus[]> {
    const response = await axios.get(`${API_BASE}/nexus`)
    return response.data
  }

  async createSalesTaxNexus(payload: Omit<SalesTaxNexus, 'id' | 'last_evaluated_at'>): Promise<{ id: string }> {
    const response = await axios.post(`${API_BASE}/nexus`, payload)
    return response.data
  }

  async updateSalesTaxNexus(id: string, payload: Partial<SalesTaxNexus>): Promise<{ id: string }> {
    const response = await axios.put(`${API_BASE}/nexus/${id}`, payload)
    return response.data
  }

  // Tax Automation Rules
  async getAutomationRules(): Promise<TaxAutomationRule[]> {
    const response = await axios.get(`${API_BASE}/automation-rules`)
    return response.data
  }

  async createAutomationRule(payload: Omit<TaxAutomationRule, 'id' | 'last_triggered_at'>): Promise<{ id: string }> {
    const response = await axios.post(`${API_BASE}/automation-rules`, payload)
    return response.data
  }

  async updateAutomationRule(id: string, payload: Partial<TaxAutomationRule>): Promise<{ id: string }> {
    const response = await axios.put(`${API_BASE}/automation-rules/${id}`, payload)
    return response.data
  }

  // E-filing integrations
  async getEFilingIntegrations(): Promise<TaxEFilingIntegration[]> {
    const response = await axios.get(`${API_BASE}/e-filing-integrations`)
    return response.data
  }

  async createEFilingIntegration(payload: Omit<TaxEFilingIntegration, 'id' | 'last_sync_at'>): Promise<{ id: string }> {
    const response = await axios.post(`${API_BASE}/e-filing-integrations`, payload)
    return response.data
  }

  async updateEFilingIntegration(id: string, payload: Partial<TaxEFilingIntegration>): Promise<{ id: string }> {
    const response = await axios.put(`${API_BASE}/e-filing-integrations/${id}`, payload)
    return response.data
  }

  // Payment scheduling
  async getPaymentSchedules(): Promise<TaxPaymentSchedule[]> {
    const response = await axios.get(`${API_BASE}/payment-schedules`)
    return response.data
  }

  async createPaymentSchedule(payload: Omit<TaxPaymentSchedule, 'id' | 'paid_at'>): Promise<{ id: string }> {
    const response = await axios.post(`${API_BASE}/payment-schedules`, payload)
    return response.data
  }

  async updatePaymentSchedule(id: string, payload: Partial<TaxPaymentSchedule>): Promise<{ id: string }> {
    const response = await axios.put(`${API_BASE}/payment-schedules/${id}`, payload)
    return response.data
  }
}

export const taxApiService = new TaxApiService()
