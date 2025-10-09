/**
 * Payroll service for API interactions
 */
import { api } from '@/utils/api'

export interface Employee {
  id: string
  employee_id: string
  first_name: string
  last_name: string
  full_name: string
  email: string
  phone_number?: string
  department: string
  job_title: string
  employment_type: string
  hire_date: string
  base_salary: number
  pay_frequency: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface PayRun {
  id: string
  run_number: string
  pay_period_start: string
  pay_period_end: string
  pay_date: string
  status: string
  total_gross_pay: number
  total_deductions: number
  total_taxes: number
  total_net_pay: number
  processed_at?: string
  approved_at?: string
  created_at: string
}

export interface Payslip {
  id: string
  payslip_number: string
  employee_id: string
  pay_period_start: string
  pay_period_end: string
  pay_date: string
  gross_pay: number
  total_deductions: number
  net_pay: number
  federal_tax: number
  state_tax: number
  health_insurance: number
  regular_hours: number
  overtime_hours: number
  is_paid: boolean
  created_at: string
}

export interface PayrollSummary {
  period: {
    start_date: string
    end_date: string
  }
  summary: {
    pay_runs_count: number
    total_gross_pay: number
    total_net_pay: number
    total_taxes: number
    total_deductions: number
  }
  by_department: Record<string, {
    employee_count: number
    total_gross: number
    total_net: number
  }>
}

export interface Deduction {
  id: string
  name: string
  type: string
  employeeId: string
  employee?: {
    name: string
    employee_id: string
  }
  amount: number
  frequency: string
  description?: string
  status: string
  created_at: string
  updated_at: string
}

export interface Tax {
  id: string
  tax_type: string
  employeeId: string
  employee?: {
    name: string
    employee_id: string
  }
  jurisdiction: string
  amount: number
  tax_period: string
  description?: string
  status: string
  created_at: string
  updated_at: string
}

class PayrollService {
  // Employee Management
  async getEmployees(params?: {
    active_only?: boolean
    department?: string
  }): Promise<Employee[]> {
    const response = await api.get('/payroll/employees', { params })
    return response.data
  }

  async getEmployee(id: string): Promise<Employee> {
    const response = await api.get(`/payroll/employees/${id}`)
    return response.data
  }

  async createEmployee(data: Omit<Employee, 'id' | 'full_name' | 'is_active' | 'created_at' | 'updated_at'>): Promise<Employee> {
    const response = await api.post('/payroll/employees', data)
    return response.data
  }

  async updateEmployee(id: string, data: Partial<Employee>): Promise<Employee> {
    const response = await api.put(`/payroll/employees/${id}`, data)
    return response.data
  }

  async deleteEmployee(id: string): Promise<{ message: string }> {
    const response = await api.delete(`/payroll/employees/${id}`)
    return response.data
  }

  // Pay Run Management
  async getPayRuns(limit?: number): Promise<PayRun[]> {
    const response = await api.get('/payroll/pay-runs', { params: { limit } })
    return response.data
  }

  async getPayRun(id: string): Promise<PayRun> {
    const response = await api.get(`/payroll/pay-runs/${id}`)
    return response.data
  }

  async createPayRun(data: {
    pay_period_start: string
    pay_period_end: string
    pay_date: string
    employee_ids?: string[]
  }): Promise<PayRun> {
    const response = await api.post('/payroll/pay-runs', data)
    return response.data
  }

  async processPayRun(id: string): Promise<PayRun> {
    const response = await api.post(`/payroll/pay-runs/${id}/process`)
    return response.data
  }

  async approvePayRun(id: string): Promise<PayRun> {
    const response = await api.post(`/payroll/pay-runs/${id}/approve`)
    return response.data
  }

  // Payslip Management
  async getPayslips(params?: {
    employee_id?: string
    pay_run_id?: string
    limit?: number
  }): Promise<Payslip[]> {
    const response = await api.get('/payroll/payslips', { params })
    return response.data
  }

  async getPayslip(id: string): Promise<Payslip> {
    const response = await api.get(`/payroll/payslips/${id}`)
    return response.data
  }

  // Analytics and Reporting
  async getPayrollSummary(params: {
    start_date: string
    end_date: string
  }): Promise<PayrollSummary> {
    const response = await api.get('/payroll/summary', { params })
    return response.data
  }

  async getDepartments(): Promise<string[]> {
    const response = await api.get('/payroll/departments/list')
    return response.data
  }

  async getDepartmentStats(): Promise<Record<string, number>> {
    const response = await api.get('/payroll/employees/stats/department-counts')
    return response.data
  }

  // Deduction Management
  async getDeductions(params?: {
    employee_id?: string
    type?: string
    status?: string
  }): Promise<{ data: Deduction[] }> {
    const response = await api.get('/payroll/deductions', { params })
    return response
  }

  async getDeduction(id: string): Promise<Deduction> {
    const response = await api.get(`/payroll/deductions/${id}`)
    return response.data
  }

  async createDeduction(data: Omit<Deduction, 'id' | 'created_at' | 'updated_at'>): Promise<Deduction> {
    const response = await api.post('/payroll/deductions', data)
    return response.data
  }

  async updateDeduction(id: string, data: Partial<Deduction>): Promise<Deduction> {
    const response = await api.put(`/payroll/deductions/${id}`, data)
    return response.data
  }

  async deleteDeduction(id: string): Promise<{ message: string }> {
    const response = await api.delete(`/payroll/deductions/${id}`)
    return response.data
  }

  // Tax Management
  async getTaxes(params?: {
    employee_id?: string
    tax_type?: string
    jurisdiction?: string
  }): Promise<{ data: Tax[] }> {
    const response = await api.get('/payroll/taxes', { params })
    return response
  }

  async getTax(id: string): Promise<Tax> {
    const response = await api.get(`/payroll/taxes/${id}`)
    return response.data
  }

  async createTax(data: Omit<Tax, 'id' | 'created_at' | 'updated_at'>): Promise<Tax> {
    const response = await api.post('/payroll/taxes', data)
    return response.data
  }

  async updateTax(id: string, data: Partial<Tax>): Promise<Tax> {
    const response = await api.put(`/payroll/taxes/${id}`, data)
    return response.data
  }

  async deleteTax(id: string): Promise<{ message: string }> {
    const response = await api.delete(`/payroll/taxes/${id}`)
    return response.data
  }

  // Utility methods
  formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString()
  }

  getStatusColor(status: string): string {
    const colors: Record<string, string> = {
      draft: 'secondary',
      processing: 'warning',
      approved: 'success',
      paid: 'info',
      cancelled: 'danger'
    }
    return colors[status] || 'secondary'
  }

  getEmploymentTypeLabel(type: string): string {
    const labels: Record<string, string> = {
      full_time: 'Full Time',
      part_time: 'Part Time',
      contract: 'Contract',
      temporary: 'Temporary',
      intern: 'Intern'
    }
    return labels[type] || type
  }

  getPayFrequencyLabel(frequency: string): string {
    const labels: Record<string, string> = {
      weekly: 'Weekly',
      biweekly: 'Bi-weekly',
      monthly: 'Monthly',
      quarterly: 'Quarterly'
    }
    return labels[frequency] || frequency
  }
}

export const payrollService = new PayrollService()
export default payrollService