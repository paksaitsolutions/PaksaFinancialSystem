/**
 * Comprehensive API Response Types
 * Centralized type definitions for all API responses
 */

// ============================================================================
// Common Types
// ============================================================================

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: {
    code: string
    message: string
    details?: any
  }
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

export interface ListResponse<T> {
  items: T[]
  total: number
}

// ============================================================================
// Authentication & User Types
// ============================================================================

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface User {
  id: string
  email: string
  firstName?: string
  lastName?: string
  fullName?: string
  roles: string[]
  permissions: string[]
  isAdmin: boolean
  isActive: boolean
  createdAt?: string
  updatedAt?: string
}

// ============================================================================
// General Ledger Types
// ============================================================================

export interface GLAccount {
  id: string
  code: string
  name: string
  type: 'Asset' | 'Liability' | 'Equity' | 'Revenue' | 'Expense'
  balance: number
  isActive: boolean
  parentId?: string
  description?: string
  createdAt?: string
  updatedAt?: string
}

export interface JournalEntry {
  id: string
  entryNumber: string
  entryDate: string
  description: string
  totalAmount: number
  status: 'draft' | 'posted' | 'void'
  lines: JournalEntryLine[]
  createdBy?: string
  createdAt?: string
  updatedAt?: string
}

export interface JournalEntryLine {
  id: string
  accountId: string
  accountCode: string
  accountName: string
  debit: number
  credit: number
  description?: string
}

export interface TrialBalance {
  entries: TrialBalanceEntry[]
  totalDebit: number
  totalCredit: number
  difference: number
  isBalanced: boolean
  asOfDate: string
}

export interface TrialBalanceEntry {
  accountCode: string
  accountName: string
  accountType: string
  openingBalance: number
  periodActivity: number
  endingBalance: number
  debitAmount: number
  creditAmount: number
  balance: number
}

// ============================================================================
// Accounts Payable Types
// ============================================================================

export interface Vendor {
  id: string
  code: string
  name: string
  email?: string
  phone?: string
  address?: string
  balance: number
  paymentTerms: string
  status: 'active' | 'inactive'
  createdAt?: string
  updatedAt?: string
}

export interface APInvoice {
  id: string
  invoiceNumber: string
  vendorId: string
  vendorName?: string
  invoiceDate: string
  dueDate: string
  totalAmount: number
  paidAmount: number
  balance: number
  status: 'draft' | 'pending' | 'approved' | 'paid' | 'overdue' | 'void'
  description?: string
  createdAt?: string
  updatedAt?: string
}

export interface APPayment {
  id: string
  paymentNumber: string
  vendorId: string
  vendorName?: string
  amount: number
  paymentDate: string
  paymentMethod: 'check' | 'ach' | 'wire' | 'credit_card' | 'cash'
  reference?: string
  status: 'pending' | 'processed' | 'void'
  createdAt?: string
  updatedAt?: string
}

// ============================================================================
// Accounts Receivable Types
// ============================================================================

export interface Customer {
  id: string
  code?: string
  name: string
  email?: string
  phone?: string
  address?: string
  creditLimit: number
  balance: number
  paymentTerms: string
  status: 'active' | 'inactive'
  createdAt?: string
  updatedAt?: string
}

export interface ARInvoice {
  id: string
  invoiceNumber: string
  customerId: string
  customerName?: string
  invoiceDate: string
  dueDate: string
  totalAmount: number
  paidAmount: number
  balance: number
  status: 'draft' | 'sent' | 'paid' | 'overdue' | 'void'
  items?: ARInvoiceItem[]
  createdAt?: string
  updatedAt?: string
}

export interface ARInvoiceItem {
  id: string
  description: string
  quantity: number
  unitPrice: number
  amount: number
  taxAmount?: number
}

export interface ARPayment {
  id: string
  paymentNumber: string
  customerId: string
  customerName?: string
  amount: number
  paymentDate: string
  paymentMethod: 'check' | 'ach' | 'wire' | 'credit_card' | 'cash'
  reference?: string
  status: 'pending' | 'processed' | 'void'
  createdAt?: string
  updatedAt?: string
}

// ============================================================================
// Cash Management Types
// ============================================================================

export interface BankAccount {
  id: string
  accountName: string
  accountNumber: string
  bankName: string
  balance: number
  currency: string
  isActive: boolean
  createdAt?: string
  updatedAt?: string
}

export interface CashTransaction {
  id: string
  bankAccountId: string
  transactionType: 'deposit' | 'withdrawal' | 'transfer'
  amount: number
  transactionDate: string
  description: string
  reference?: string
  status: 'pending' | 'cleared' | 'void'
  createdAt?: string
  updatedAt?: string
}

// ============================================================================
// Budget Types
// ============================================================================

export interface Budget {
  id: string
  name: string
  year: number
  totalAmount: number
  status: 'draft' | 'active' | 'closed'
  departmentId?: string
  projectId?: string
  lines?: BudgetLine[]
  createdAt?: string
  updatedAt?: string
}

export interface BudgetLine {
  id: string
  accountId: string
  accountCode: string
  accountName: string
  budgetedAmount: number
  actualAmount: number
  variance: number
  variancePercent: number
}

// ============================================================================
// Payroll Types
// ============================================================================

export interface Employee {
  id: string
  employeeNumber: string
  firstName: string
  lastName: string
  fullName: string
  email: string
  phone?: string
  department?: string
  position: string
  hireDate?: string
  baseSalary: number
  payFrequency: 'weekly' | 'biweekly' | 'monthly'
  status: 'active' | 'inactive' | 'terminated'
  createdAt?: string
  updatedAt?: string
}

export interface PayRun {
  id: string
  payPeriodStart: string
  payPeriodEnd: string
  payDate: string
  status: 'draft' | 'processing' | 'approved' | 'paid'
  totalGrossPay: number
  totalDeductions: number
  totalNetPay: number
  employeeCount: number
  createdAt?: string
  updatedAt?: string
}

export interface Payslip {
  id: string
  payRunId: string
  employeeId: string
  employeeName: string
  payPeriodStart: string
  payPeriodEnd: string
  payDate: string
  grossPay: number
  totalDeductions: number
  netPay: number
  status: 'draft' | 'paid'
  earnings: PayslipItem[]
  deductions: PayslipItem[]
  taxes: PayslipItem[]
}

export interface PayslipItem {
  name: string
  amount: number
  type: 'earning' | 'deduction' | 'tax'
}

// ============================================================================
// Tax Types
// ============================================================================

export interface TaxRate {
  id: string
  name: string
  rate: number
  jurisdiction: string
  taxType: string
  isActive: boolean
  effectiveDate?: string
  expiryDate?: string
}

export interface TaxReturn {
  id: string
  returnType: string
  taxPeriod: string
  jurisdiction: string
  dueDate: string
  filingDate?: string
  status: 'draft' | 'pending' | 'filed' | 'amended'
  amountDue: number
  amountPaid: number
  createdAt?: string
  updatedAt?: string
}

// ============================================================================
// Inventory Types
// ============================================================================

export interface InventoryItem {
  id: string
  sku: string
  name: string
  description?: string
  categoryId: string
  categoryName?: string
  quantity: number
  unitPrice: number
  totalValue: number
  reorderPoint: number
  unitOfMeasure: string
  status: 'in_stock' | 'low_stock' | 'out_of_stock'
  createdAt?: string
  updatedAt?: string
}

export interface InventoryCategory {
  id: string
  name: string
  description?: string
  itemCount: number
  totalValue: number
}

export interface InventoryLocation {
  id: string
  name: string
  code: string
  type: 'warehouse' | 'store' | 'other'
  address?: string
  capacity: number
  itemCount: number
  totalValue: number
}

// ============================================================================
// Fixed Assets Types
// ============================================================================

export interface FixedAsset {
  id: string
  assetNumber: string
  assetName: string
  description?: string
  assetCategory: string
  location?: string
  purchaseDate: string
  purchaseCost: number
  salvageValue: number
  usefulLifeYears: number
  depreciationMethod: 'straight_line' | 'declining_balance' | 'units_of_production'
  accumulatedDepreciation: number
  currentValue: number
  status: 'active' | 'disposed' | 'fully_depreciated'
  createdAt?: string
  updatedAt?: string
}

export interface MaintenanceRecord {
  id: string
  assetId: string
  assetName?: string
  maintenanceType: 'preventive' | 'corrective' | 'inspection'
  description: string
  scheduledDate: string
  completedDate?: string
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled'
  estimatedCost: number
  actualCost: number
  vendorName?: string
  notes?: string
}

// ============================================================================
// Dashboard & Analytics Types
// ============================================================================

export interface DashboardStats {
  totalRevenue: number
  netProfit: number
  customers: number
  overdue: number
}

export interface KPI {
  label: string
  value: number | string
  trend: 'up' | 'down' | 'neutral'
  changePercent: number
}

export interface ChartData {
  labels: string[]
  datasets: ChartDataset[]
}

export interface ChartDataset {
  label: string
  data: number[]
  backgroundColor?: string | string[]
  borderColor?: string
  fill?: boolean
}

// ============================================================================
// Report Types
// ============================================================================

export interface FinancialStatement {
  balanceSheet: BalanceSheet
  incomeStatement: IncomeStatement
  cashFlowStatement?: CashFlowStatement
  period: string
  generatedAt: string
}

export interface BalanceSheet {
  totalAssets: number
  totalLiabilities: number
  equity: number
  assets: AccountGroup[]
  liabilities: AccountGroup[]
}

export interface IncomeStatement {
  revenue: number
  expenses: number
  netIncome: number
  revenues: AccountGroup[]
  expenses: AccountGroup[]
}

export interface CashFlowStatement {
  operatingActivities: number
  investingActivities: number
  financingActivities: number
  netCashFlow: number
}

export interface AccountGroup {
  name: string
  amount: number
  accounts: GLAccount[]
}

// ============================================================================
// Settings Types
// ============================================================================

export interface SystemSetting {
  settingKey: string
  settingValue: string
  description?: string
  updatedAt?: string
}

export interface CompanySettings {
  companyName: string
  address?: string
  phone?: string
  email?: string
  taxId?: string
  fiscalYearStart: number
  currency: string
  timezone: string
}

// ============================================================================
// Notification Types
// ============================================================================

export interface Notification {
  id: string
  title: string
  message: string
  type: 'info' | 'success' | 'warning' | 'error'
  priority: 'low' | 'medium' | 'high'
  isRead: boolean
  actionUrl?: string
  createdAt: string
}

// ============================================================================
// Export all types
// ============================================================================

export type {
  ApiResponse,
  PaginatedResponse,
  ListResponse
}
