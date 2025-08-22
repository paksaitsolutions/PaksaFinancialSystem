/**
 * Payroll Types
 * 
 * This file contains all the TypeScript interfaces and types
 * used throughout the payroll module.
 */

import { User } from '@/types';

/**
 * Pay Period
 */
export interface PayPeriod {
  id: string;
  name: string;
  startDate: string;
  endDate: string;
  status: 'draft' | 'open' | 'processing' | 'processed' | 'paid' | 'closed';
  payDate: string;
  fiscalYear: number;
  periodNumber: number;
  companyId: string;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  updatedBy: string;
}

/**
 * Pay Run
 */
export interface PayRun {
  id: string;
  name: string;
  payPeriodId: string;
  status: 'draft' | 'processing' | 'processed' | 'approved' | 'paid' | 'cancelled';
  paymentDate: string;
  totalGross: number;
  totalTax: number;
  totalDeductions: number;
  totalNet: number;
  currency: string;
  notes?: string;
  companyId: string;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  updatedBy: string;
  payPeriod?: PayPeriod;
}

/**
 * Employee Payroll Info
 */
export interface EmployeePayrollInfo {
  id: string;
  employeeId: string;
  employeeNumber: string;
  fullName: string;
  department: string;
  position: string;
  employmentType: 'full-time' | 'part-time' | 'contractor' | 'temporary';
  baseSalary: number;
  hourlyRate: number;
  paymentMethod: 'bank' | 'check' | 'cash' | 'other';
  bankName?: string;
  bankAccountNumber?: string;
  bankRoutingNumber?: string;
  taxId?: string;
  taxStatus: 'single' | 'married' | 'head_of_household';
  taxAllowances: number;
  additionalTaxAmount: number;
  isActive: boolean;
  hireDate: string;
  terminationDate?: string;
}

/**
 * Payslip
 */
export interface Payslip {
  id: string;
  payRunId: string;
  employeeId: string;
  employeeNumber: string;
  employeeName: string;
  department: string;
  position: string;
  payPeriod: string;
  paymentDate: string;
  paymentMethod: string;
  bankAccountNumber?: string;
  currency: string;
  status: 'draft' | 'pending' | 'approved' | 'paid' | 'cancelled';
  
  // Earnings
  regularHours: number;
  regularRate: number;
  regularPay: number;
  overtimeHours: number;
  overtimeRate: number;
  overtimePay: number;
  bonus: number;
  commission: number;
  reimbursement: number;
  otherEarnings: number;
  totalEarnings: number;
  
  // Deductions
  taxWithheld: number;
  socialSecurity: number;
  medicare: number;
  retirement401k: number;
  healthInsurance: number;
  otherDeductions: number;
  totalDeductions: number;
  
  // Net Pay
  netPay: number;
  
  // YTD Totals
  ytdGross: number;
  ytdTax: number;
  ytdDeductions: number;
  ytdNet: number;
  
  // Metadata
  notes?: string;
  companyId: string;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  updatedBy: string;
  
  // Relations
  payRun?: PayRun;
  employee?: EmployeePayrollInfo;
  earnings?: PayslipEarning[];
  deductions?: PayslipDeduction[];
  taxes?: PayslipTax[];
  benefits?: PayslipBenefit[];
}

/**
 * Payslip Earning
 */
export interface PayslipEarning {
  id: string;
  payslipId: string;
  type: 'regular' | 'overtime' | 'bonus' | 'commission' | 'reimbursement' | 'other';
  name: string;
  description?: string;
  amount: number;
  rate?: number;
  hours?: number;
  isTaxable: boolean;
  isPensionable: boolean;
  glAccountCode?: string;
  createdAt: string;
  updatedAt: string;
}

/**
 * Payslip Deduction
 */
export interface PayslipDeduction {
  id: string;
  payslipId: string;
  type: 'tax' | 'benefit' | 'garnish' | 'loan' | 'other';
  name: string;
  description?: string;
  amount: number;
  isPreTax: boolean;
  glAccountCode?: string;
  createdAt: string;
  updatedAt: string;
}

/**
 * Payslip Tax
 */
export interface PayslipTax {
  id: string;
  payslipId: string;
  code: string;
  name: string;
  description?: string;
  amount: number;
  isEmployerTax: boolean;
  glAccountCode?: string;
  createdAt: string;
  updatedAt: string;
}

/**
 * Payslip Benefit
 */
export interface PayslipBenefit {
  id: string;
  payslipId: string;
  benefitPlanId: string;
  name: string;
  description?: string;
  employeeContribution: number;
  employerContribution: number;
  isPreTax: boolean;
  glAccountCode?: string;
  createdAt: string;
  updatedAt: string;
}

/**
 * Payroll Settings
 */
export interface PayrollSettings {
  id: string;
  companyId: string;
  defaultPayFrequency: 'weekly' | 'bi-weekly' | 'semi-monthly' | 'monthly';
  defaultPayDay: number; // Day of month (1-31) or day of week (0-6) depending on frequency
  defaultCurrency: string;
  defaultPaymentMethod: 'bank' | 'check' | 'cash' | 'other';
  defaultBankId?: string;
  taxYearStartMonth: number; // 1-12
  taxYearEndMonth: number;   // 1-12
  taxFilingId?: string;
  taxRegistrationNumber?: string;
  taxOffice?: string;
  taxOfficeAddress?: string;
  taxOfficePhone?: string;
  taxOfficeEmail?: string;
  isAutoApproveTimesheets: boolean;
  isAutoApproveExpenses: boolean;
  isAutoApproveTimeOff: boolean;
  isAutoProcessPayroll: boolean;
  isAutoApprovePayroll: boolean;
  isAutoPayEmployees: boolean;
  isAutoFileTaxes: boolean;
  isAutoSubmitTaxPayments: boolean;
  isAutoSubmitTaxFilings: boolean;
  isAutoSubmitTaxForms: boolean;
  isAutoSubmitTaxW2s: boolean;
  isAutoSubmitTax1099s: boolean;
  isAutoSubmitTax941: boolean;
  isAutoSubmitTax940: boolean;
  isAutoSubmitTaxState: boolean;
  isAutoSubmitTaxLocal: boolean;
  isAutoSubmitTaxOther: boolean;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  updatedBy: string;
}

/**
 * Payroll Form Data
 */
export interface PayrollFormData {
  payPeriodId: string;
  paymentDate: string;
  employeeIds: string[];
  includeRegularPay: boolean;
  includeOvertime: boolean;
  includeBonuses: boolean;
  includeCommissions: boolean;
  includeReimbursements: boolean;
  includeOtherEarnings: boolean;
  includeTaxes: boolean;
  includeDeductions: boolean;
  includeBenefits: boolean;
  processPayroll: boolean;
  approvePayroll: boolean;
  processPayments: boolean;
  sendPayslips: boolean;
  notes?: string;
}

/**
 * Payroll Process Result
 */
export interface PayrollProcessResult {
  success: boolean;
  message: string;
  payRunId?: string;
  payslipsProcessed: number;
  totalGross: number;
  totalTax: number;
  totalDeductions: number;
  totalNet: number;
  errors?: string[];
  warnings?: string[];
}

/**
 * Payroll Report
 */
export interface PayrollReport {
  id: string;
  name: string;
  description?: string;
  type: 'summary' | 'detailed' | 'tax' | 'benefits' | 'custom';
  format: 'pdf' | 'excel' | 'csv' | 'json';
  period: 'daily' | 'weekly' | 'bi-weekly' | 'monthly' | 'quarterly' | 'yearly' | 'custom';
  startDate?: string;
  endDate?: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  fileUrl?: string;
  fileSize?: number;
  fileType?: string;
  companyId: string;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  updatedBy: string;
}

/**
 * Payroll API Response
 */
export interface PayrollApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  errors?: Record<string, string[]>;
  meta?: {
    total?: number;
    page?: number;
    limit?: number;
    pages?: number;
  };
}

/**
 * Payroll Paginated Response
 */
export interface PayrollPaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}
