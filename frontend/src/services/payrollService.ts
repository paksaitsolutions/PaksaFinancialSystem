import { api } from '@/utils/api'

export interface Employee {
  id: number
  employee_number: string
  first_name: string
  last_name: string
  full_name: string
  email: string
  phone?: string
  department: string
  position: string
  hire_date: string
  employment_type: 'full_time' | 'part_time' | 'contract'
  status: 'active' | 'inactive' | 'terminated'
  salary_type: 'hourly' | 'salary'
  base_salary: number
  hourly_rate?: number
  pay_frequency: 'weekly' | 'bi_weekly' | 'monthly'
  tax_id?: string
  bank_account?: string
  created_at: string
  updated_at: string
}

export interface PayRun {
  id: number
  pay_period_start: string
  pay_period_end: string
  pay_date: string
  status: 'draft' | 'processing' | 'approved' | 'paid' | 'cancelled'
  total_gross_pay: number
  total_deductions: number
  total_net_pay: number
  employee_count: number
  created_by: string
  created_at: string
  approved_at?: string
  paid_at?: string
}

export interface Payslip {
  id: number
  pay_run_id: number
  employee_id: number
  employee_name: string
  pay_period_start: string
  pay_period_end: string
  pay_date: string
  gross_pay: number
  total_deductions: number
  net_pay: number
  hours_worked?: number
  overtime_hours?: number
  earnings: PayslipEarning[]
  deductions: PayslipDeduction[]
  taxes: PayslipTax[]
  status: 'draft' | 'approved' | 'paid'
}

export interface PayslipEarning {
  id: number
  type: 'base_salary' | 'overtime' | 'bonus' | 'commission' | 'allowance'
  description: string
  amount: number
  hours?: number
  rate?: number
}

export interface PayslipDeduction {
  id: number
  type: 'health_insurance' | 'dental' | 'retirement' | 'loan' | 'other'
  description: string
  amount: number
  is_pre_tax: boolean
}

export interface PayslipTax {
  id: number
  tax_type: 'federal_income' | 'state_income' | 'social_security' | 'medicare' | 'unemployment'
  description: string
  taxable_amount: number
  tax_rate: number
  tax_amount: number
}

export interface PayrollKPIs {
  total_payroll: number
  payroll_change: number
  total_employees: number
  employee_change: number
  average_salary: number
  salary_change: number
  upcoming_payroll: number
}

export interface DeductionBenefit {
  id: number
  name: string
  type: 'deduction' | 'benefit'
  category: 'health' | 'retirement' | 'insurance' | 'loan' | 'other'
  calculation_type: 'fixed' | 'percentage' | 'tiered'
  amount?: number
  percentage?: number
  is_pre_tax: boolean
  is_mandatory: boolean
  employer_contribution?: number
  description?: string
  is_active: boolean
}

export interface TaxConfiguration {
  id: number
  tax_type: string
  jurisdiction: string
  rate: number
  threshold?: number
  cap?: number
  is_active: boolean
  effective_date: string
}

export interface PayrollReport {
  id: string
  name: string
  type: 'payroll_summary' | 'tax_liability' | 'employee_earnings' | 'deductions'
  period_start: string
  period_end: string
  generated_at: string
  data: any
}

class PayrollService {
  // Dashboard
  async getPayrollKPIs(): Promise<PayrollKPIs> {
    const response = await api.get('/payroll/dashboard/kpis')
    return response.data
  }

  async getPayrollSummary(months: number = 6): Promise<{
    monthly_data: { month: string, budget: number, actual: number }[]
    total_budget: number
    total_actual: number
  }> {
    const response = await api.get(`/payroll/dashboard/summary?months=${months}`)
    return response.data
  }

  async getRecentActivity(limit: number = 10): Promise<{
    id: number
    type: string
    title: string
    details: string
    timestamp: string
    user: string
  }[]> {
    const response = await api.get(`/payroll/dashboard/activity?limit=${limit}`)
    return response.data
  }

  // Employees
  async getEmployees(params?: {
    page?: number
    limit?: number
    search?: string
    department?: string
    status?: string
  }): Promise<{ employees: Employee[], total: number }> {
    const response = await api.get('/payroll/employees', { params })
    return response.data
  }

  async getEmployee(id: number): Promise<Employee> {
    const response = await api.get(`/payroll/employees/${id}`)
    return response.data
  }

  async createEmployee(employee: Omit<Employee, 'id' | 'full_name' | 'created_at' | 'updated_at'>): Promise<Employee> {
    const response = await api.post('/payroll/employees', employee)
    return response.data
  }

  async updateEmployee(id: number, employee: Partial<Employee>): Promise<Employee> {
    const response = await api.put(`/payroll/employees/${id}`, employee)
    return response.data
  }

  async deleteEmployee(id: number): Promise<void> {
    await api.delete(`/payroll/employees/${id}`)
  }

  // Pay Runs
  async getPayRuns(params?: {
    page?: number
    limit?: number
    status?: string
    start_date?: string
    end_date?: string
  }): Promise<{ pay_runs: PayRun[], total: number }> {
    const response = await api.get('/payroll/pay-runs', { params })
    return response.data
  }

  async getPayRun(id: number): Promise<PayRun> {
    const response = await api.get(`/payroll/pay-runs/${id}`)
    return response.data
  }

  async createPayRun(payRun: {
    pay_period_start: string
    pay_period_end: string
    pay_date: string
    employee_ids?: number[]
  }): Promise<PayRun> {
    const response = await api.post('/payroll/pay-runs', payRun)
    return response.data
  }

  async processPayRun(id: number): Promise<PayRun> {
    const response = await api.post(`/payroll/pay-runs/${id}/process`)
    return response.data
  }

  async approvePayRun(id: number): Promise<PayRun> {
    const response = await api.post(`/payroll/pay-runs/${id}/approve`)
    return response.data
  }

  async payPayRun(id: number): Promise<PayRun> {
    const response = await api.post(`/payroll/pay-runs/${id}/pay`)
    return response.data
  }

  async cancelPayRun(id: number): Promise<PayRun> {
    const response = await api.post(`/payroll/pay-runs/${id}/cancel`)
    return response.data
  }

  // Payslips
  async getPayslips(params?: {
    pay_run_id?: number
    employee_id?: number
    page?: number
    limit?: number
  }): Promise<{ payslips: Payslip[], total: number }> {
    const response = await api.get('/payroll/payslips', { params })
    return response.data
  }

  async getPayslip(id: number): Promise<Payslip> {
    const response = await api.get(`/payroll/payslips/${id}`)
    return response.data
  }

  async generatePayslipPDF(id: number): Promise<Blob> {
    const response = await api.get(`/payroll/payslips/${id}/pdf`, {
      responseType: 'blob'
    })
    return response.data
  }

  // Deductions & Benefits
  async getDeductionsBenefits(): Promise<DeductionBenefit[]> {
    const response = await api.get('/payroll/deductions-benefits')
    return response.data
  }

  async createDeductionBenefit(item: Omit<DeductionBenefit, 'id' | 'is_active'>): Promise<DeductionBenefit> {
    const response = await api.post('/payroll/deductions-benefits', item)
    return response.data
  }

  async updateDeductionBenefit(id: number, item: Partial<DeductionBenefit>): Promise<DeductionBenefit> {
    const response = await api.put(`/payroll/deductions-benefits/${id}`, item)
    return response.data
  }

  async deleteDeductionBenefit(id: number): Promise<void> {
    await api.delete(`/payroll/deductions-benefits/${id}`)
  }

  // Tax Configuration
  async getTaxConfigurations(): Promise<TaxConfiguration[]> {
    const response = await api.get('/payroll/tax-configurations')
    return response.data
  }

  async createTaxConfiguration(config: Omit<TaxConfiguration, 'id' | 'is_active'>): Promise<TaxConfiguration> {
    const response = await api.post('/payroll/tax-configurations', config)
    return response.data
  }

  async updateTaxConfiguration(id: number, config: Partial<TaxConfiguration>): Promise<TaxConfiguration> {
    const response = await api.put(`/payroll/tax-configurations/${id}`, config)
    return response.data
  }

  // Reports
  async generatePayrollReport(type: string, params: {
    start_date: string
    end_date: string
    employee_ids?: number[]
    department?: string
  }): Promise<PayrollReport> {
    const response = await api.post('/payroll/reports/generate', { type, ...params })
    return response.data
  }

  async getPayrollReports(): Promise<PayrollReport[]> {
    const response = await api.get('/payroll/reports')
    return response.data
  }

  async downloadReport(id: string, format: 'pdf' | 'excel' = 'pdf'): Promise<Blob> {
    const response = await api.get(`/payroll/reports/${id}/download?format=${format}`, {
      responseType: 'blob'
    })
    return response.data
  }

  // Analytics
  async getPayrollAnalytics(params: {
    start_date: string
    end_date: string
    group_by?: 'month' | 'department' | 'employee'
  }): Promise<{
    total_payroll: number
    average_salary: number
    by_period: { period: string, amount: number }[]
    by_department: { department: string, amount: number, employee_count: number }[]
    top_earners: { employee_name: string, amount: number }[]
  }> {
    const response = await api.get('/payroll/analytics', { params })
    return response.data
  }

  // Import/Export
  async importEmployees(file: File): Promise<{ success: number, errors: string[] }> {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/payroll/employees/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  }

  async exportEmployees(format: 'csv' | 'excel' = 'csv'): Promise<Blob> {
    const response = await api.get(`/payroll/employees/export?format=${format}`, {
      responseType: 'blob'
    })
    return response.data
  }
}

export const payrollService = new PayrollService()