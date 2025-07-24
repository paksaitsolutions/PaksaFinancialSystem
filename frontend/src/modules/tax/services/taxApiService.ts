import axios from 'axios'
import { TaxTransaction, TaxRate, TaxJurisdiction, TaxExemption, TaxReturn } from '../types/tax'

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
}

export const taxApiService = new TaxApiService()