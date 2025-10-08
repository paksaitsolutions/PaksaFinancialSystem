import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api/v1'

export interface TaxReturn {
  id?: number
  return_id: string
  tax_year: string
  return_type: string
  ntn?: string
  cnic?: string
  gross_income: number
  taxable_income: number
  tax_liability: number
  advance_tax_paid: number
  due_date: string
  filed_date?: string
  status: string
  remarks?: string
  created_at?: string
  updated_at?: string
}

export interface TaxReturnStats {
  filed: number
  pending: number
  overdue: number
  amendments: number
}

export interface TaxReturnFilters {
  tax_year?: string
  return_type?: string
  status?: string
}

class TaxReturnService {
  async getTaxReturns(filters?: TaxReturnFilters): Promise<TaxReturn[]> {
    const params = new URLSearchParams()
    if (filters?.tax_year) params.append('tax_year', filters.tax_year)
    if (filters?.return_type) params.append('return_type', filters.return_type)
    if (filters?.status) params.append('status', filters.status)
    
    const response = await axios.get(`${API_BASE_URL}/tax-returns/?${params}`)
    return response.data
  }

  async getTaxReturnStats(): Promise<TaxReturnStats> {
    const response = await axios.get(`${API_BASE_URL}/tax-returns/stats`)
    return response.data
  }

  async getTaxReturn(id: number): Promise<TaxReturn> {
    const response = await axios.get(`${API_BASE_URL}/tax-returns/${id}`)
    return response.data
  }

  async createTaxReturn(taxReturn: Omit<TaxReturn, 'id' | 'created_at' | 'updated_at'>): Promise<TaxReturn> {
    const response = await axios.post(`${API_BASE_URL}/tax-returns/`, taxReturn)
    return response.data
  }

  async updateTaxReturn(id: number, taxReturn: Partial<TaxReturn>): Promise<TaxReturn> {
    const response = await axios.put(`${API_BASE_URL}/tax-returns/${id}`, taxReturn)
    return response.data
  }

  async deleteTaxReturn(id: number): Promise<void> {
    await axios.delete(`${API_BASE_URL}/tax-returns/${id}`)
  }

  async fileTaxReturn(id: number): Promise<TaxReturn> {
    const response = await axios.post(`${API_BASE_URL}/tax-returns/${id}/file`)
    return response.data
  }
}

export default new TaxReturnService()