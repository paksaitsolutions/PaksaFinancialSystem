import { apiClient } from '@/utils/apiClient'

export interface FinancialStatement {
  balance_sheet: any
  income_statement: any
  cash_flow: any
}

export interface AgingReport {
  report_type: string
  as_of_date: string
  aging_buckets: any[]
  totals: any
}

class ReportsService {
  private baseUrl = '/api/v1/reports'

  // Financial Statements
  async getBalanceSheet(asOfDate?: string) {
    const params = asOfDate ? { as_of_date: asOfDate } : {}
    const response = await apiClient.get(`${this.baseUrl}/financial-statements/balance-sheet`, { params })
    return response.data
  }

  async getIncomeStatement(startDate?: string, endDate?: string) {
    const params: any = {}
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    const response = await apiClient.get(`${this.baseUrl}/financial-statements/income-statement`, { params })
    return response.data
  }

  async getCashFlowStatement(startDate?: string, endDate?: string) {
    const params: any = {}
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    const response = await apiClient.get(`${this.baseUrl}/financial-statements/cash-flow`, { params })
    return response.data
  }

  // General Ledger Reports
  async getTrialBalance(asOfDate?: string) {
    const params = asOfDate ? { as_of_date: asOfDate } : {}
    const response = await apiClient.get(`${this.baseUrl}/general-ledger/trial-balance`, { params })
    return response.data
  }

  // Aging Reports
  async getARAging(asOfDate?: string): Promise<AgingReport> {
    const params = asOfDate ? { as_of_date: asOfDate } : {}
    const response = await apiClient.get(`${this.baseUrl}/aging/accounts-receivable`, { params })
    return response.data
  }

  async getAPAging(asOfDate?: string): Promise<AgingReport> {
    const params = asOfDate ? { as_of_date: asOfDate } : {}
    const response = await apiClient.get(`${this.baseUrl}/aging/accounts-payable`, { params })
    return response.data
  }

  // Available Reports
  async getAvailableReports() {
    const response = await apiClient.get(`${this.baseUrl}/available-reports`)
    return response.data
  }

  // Run Report
  async runReport(reportId: string, parameters: any = {}) {
    const response = await apiClient.post(`${this.baseUrl}/run-report`, {
      report_id: reportId,
      parameters
    })
    return response.data
  }

  async exportReport(reportId: string, format: 'pdf' | 'excel' | 'csv'): Promise<void> {
    try {
      await new Promise(resolve => setTimeout(resolve, 1500))
      console.log(`Exporting report: ${reportId} as ${format}`)
    } catch (error) {
      console.error('Error exporting report:', error)
      throw new Error('Failed to export report')
    }
  }
}

export const reportsService = new ReportsService()
export default reportsService