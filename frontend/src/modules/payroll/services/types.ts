// Enums
export enum PayRunStatus {
  DRAFT = 'draft',
  PROCESSING = 'processing',
  PROCESSED = 'processed',
  APPROVED = 'approved',
  PAID = 'paid',
  CANCELLED = 'cancelled'
}

export enum PayFrequency {
  WEEKLY = 'weekly',
  BIWEEKLY = 'bi-weekly',
  SEMI_MONTHLY = 'semi-monthly',
  MONTHLY = 'monthly'
}

// Base interfaces
export interface PayRun {
  id: string;
  name: string;
  payPeriodId: string;
  status: PayRunStatus;
  paymentDate: string;
  notes?: string;
  employeeCount: number;
  totalEarnings: number;
  totalDeductions: number;
  totalTaxes: number;
  netPay: number;
  createdAt: string;
  updatedAt: string;
  processedAt?: string;
  approvedAt?: string;
  paidAt?: string;
  cancelledAt?: string;
  cancellationReason?: string;
}

export interface Payslip {
  id: string;
  employeeId: string;
  payRunId: string;
  status: 'draft' | 'pending' | 'approved' | 'paid' | 'cancelled';
  periodStart: string;
  periodEnd: string;
  paymentDate: string;
  netPay: number;
  totalEarnings: number;
  totalDeductions: number;
  totalTaxes: number;
  notes?: string;
  paymentMethod?: string;
  paidAt?: string;
  cancelledAt?: string;
  cancellationReason?: string;
}

export interface EmployeePayrollInfo {
  id: string;
  employeeId: string;
  salary: number;
  payFrequency: PayFrequency;
  taxId?: string;
  socialSecurityNumber?: string;
  bankAccountNumber?: string;
  bankName?: string;
  paymentMethod: 'bank' | 'check' | 'cash';
  isActive: boolean;
}

export interface PayPeriod {
  id: string;
  name: string;
  startDate: string;
  endDate: string;
  payDate: string;
  frequency: PayFrequency;
  status: 'open' | 'closed' | 'processing';
  notes?: string;
}

export interface PayrollSettings {
  id: string;
  companyId: string;
  defaultPayFrequency: PayFrequency;
  defaultPayDay: number;
  autoApproveTimesheets: boolean;
  autoProcessPayroll: boolean;
  autoApprovePayroll: boolean;
  autoProcessPayments: boolean;
  notifyEmployees: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface PayslipEarning {
  id: string;
  name: string;
  amount: number;
  type: string;
  isTaxable: boolean;
  glAccountCode?: string;
}

export interface PayslipDeduction {
  id: string;
  name: string;
  amount: number;
  type: string;
  isPreTax: boolean;
  glAccountCode?: string;
}

export interface PayslipTax {
  id: string;
  name: string;
  amount: number;
  type: string;
  glAccountCode?: string;
}

export interface PayrollUser {
  id: string;
  name: string;
  email: string;
  role: string;
  isActive: boolean;
  avatar?: string;
  department?: string;
  position?: string;
  employeeId?: string;
}

export interface PayRunWithDetails extends PayRun {
  payslips: PayslipWithDetails[];
  payPeriod: PayPeriod;
  benefits: Array<{
    id: string;
    name: string;
    employeeContribution: number;
    employerContribution: number;
    isPreTax: boolean;
    glAccountCode?: string;
  }>;
  createdByUser?: PayrollUser;
  updatedByUser?: PayrollUser;
}

export interface PayslipWithDetails extends Payslip {
  employee: PayrollUser & EmployeePayrollInfo;
  earnings: PayslipEarning[];
  deductions: PayslipDeduction[];
  taxes: PayslipTax[];
  benefits: Array<{
    id: string;
    name: string;
    employeeContribution: number;
    employerContribution: number;
    isPreTax: boolean;
    glAccountCode?: string;
  }>;
  totalBenefits: number;
  bankAccountNumber?: string;
  bankName?: string;
  paymentReference?: string;
}

export interface PayRunCreatePayload {
  name: string;
  payPeriodId: string;
  payDate: string;
  status?: PayRunStatus;
  notes?: string;
  employeeIds?: string[];
  companyId?: string;
  includeIncompleteTimesheets?: boolean;
  includeTerminatedEmployees?: boolean;
  processOffCyclePayments?: boolean;
  recalculateTaxes?: boolean;
  skipValidation?: boolean;
  processPayments?: boolean;
  paymentMethod?: string;
  paymentAccountId?: string;
  notifyEmployees?: boolean;
  customMessage?: string;
}

export interface PayPeriodCreateData {
  name: string;
  startDate: string;
  endDate: string;
  payDate: string;
  frequency: PayFrequency;
  status?: string;
  notes?: string;
  companyId?: string;
}

export interface YearToDateSummary {
  employeeId: string;
  employeeName: string;
  year: number;
  totalEarnings: number;
  totalRegularPay: number;
  totalOvertimePay: number;
  totalBonuses: number;
  totalCommissions: number;
  totalDeductions: number;
  totalPreTaxDeductions: number;
  totalPostTaxDeductions: number;
  totalTaxes: number;
  totalBenefits: number;
  netPay: number;
  ytdGrossPay: number;
  ytdTaxablePay: number;
  ytdTaxPaid: number;
  ytdNetPay: number;
  lastPayDate?: string;
  lastPayAmount?: number;
}

export interface PayrollApiResponse<T> {
  success: boolean;
  message?: string;
  data?: T;
  error?: string;
}

export interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  formats: string[];
  parameters: Array<{
    name: string;
    type: string;
    required: boolean;
    options?: any[];
    defaultValue?: any;
  }>;
}
