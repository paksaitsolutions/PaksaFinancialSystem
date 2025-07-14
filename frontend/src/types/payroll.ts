import { TaxPolicy, TaxRate, TaxExemption } from './tax';

export interface PayRun {
  id: string;
  period_id: string;
  period_start: string;
  period_end: string;
  status: 'draft' | 'processing' | 'completed' | 'cancelled';
  created_at: string;
  updated_at: string;
  total_employees: number;
  total_amount: number;
  tax_amount: number;
  tax_breakdown: {
    [key: string]: number;
  };
  exemptions: {
    [key: string]: number;
  };
  payslips: Payslip[];
}

export interface PayPeriod {
  id: string;
  name: string;
  start_date: string;
  end_date: string;
  status: 'active' | 'closed' | 'draft';
  created_at: string;
  updated_at: string;
}

export interface Payslip {
  id: string;
  pay_run_id: string;
  employee_id: string;
  period_start: string;
  period_end: string;
  status: 'draft' | 'processed' | 'cancelled';
  gross_income: number;
  net_income: number;
  tax_amount: number;
  tax_breakdown: {
    [key: string]: number;
  };
  exemptions: {
    [key: string]: number;
  };
  earnings: PayslipEarning[];
  deductions: PayslipDeduction[];
  created_at: string;
  updated_at: string;
}

export interface PayslipEarning {
  id: string;
  payslip_id: string;
  type: string;
  description: string;
  amount: number;
  taxable: boolean;
  tax_category?: string;
}

export interface PayslipDeduction {
  id: string;
  payslip_id: string;
  type: string;
  description: string;
  amount: number;
  tax_deductible: boolean;
  tax_category?: string;
}

export interface EmployeePayrollInfo {
  id: string;
  employee_id: string;
  tax_id: string;
  tax_category: string;
  tax_status: string;
  year_to_date: {
    gross_income: number;
    net_income: number;
    tax_amount: number;
    tax_breakdown: {
      [key: string]: number;
    };
    exemptions: {
      [key: string]: number;
    };
  };
}

export interface PayrollSettings {
  tax_policy_id: string;
  default_tax_category: string;
  tax_calculation_method: 'period' | 'ytd';
  tax_withholding_threshold: number;
  tax_filing_frequency: 'monthly' | 'quarterly' | 'annually';
}

export interface PayrollApiResponse<T> {
  success: boolean;
  message?: string;
  data?: T;
}

export interface PayRunCreatePayload {
  period_id: string;
  notes?: string;
  tax_policy_id?: string;
  custom_tax_rates?: TaxRate[];
  custom_exemptions?: TaxExemption[];
}

export interface PayPeriodCreateData {
  name: string;
  start_date: string;
  end_date: string;
  status?: 'active' | 'draft';
}

export interface ReportTemplate {
  id: string;
  name: string;
  type: string;
  description: string;
  fields: string[];
  format: 'pdf' | 'excel' | 'csv' | 'json';
}

export interface YearToDateSummary {
  gross_income: number;
  net_income: number;
  tax_amount: number;
  tax_breakdown: {
    [key: string]: number;
  };
  exemptions: {
    [key: string]: number;
  };
  earnings_summary: {
    [key: string]: number;
  };
  deductions_summary: {
    [key: string]: number;
  };
}
