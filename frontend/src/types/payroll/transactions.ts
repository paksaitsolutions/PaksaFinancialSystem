import { PaymentMethod, PaymentStatus } from './payments';

export interface PayrollTransaction {
  id: string;
  transactionDate: string;
  description: string;
  type: 'salary' | 'bonus' | 'commission' | 'reimbursement' | 'tax' | 'other';
  amount: number;
  currency: string;
  status: PaymentStatus;
  reference: string;
  employeeId: string;
  employeeName: string;
  accountId: string;
  accountName: string;
  paymentMethod?: PaymentMethod;
  notes?: string;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
  metadata?: Record<string, unknown>;
}

export interface PayrollTransactionCreate {
  employeeId: string;
  transactionDate: string;
  description: string;
  type: string;
  amount: number;
  currency: string;
  accountId: string;
  paymentMethod?: PaymentMethod;
  notes?: string;
  metadata?: Record<string, unknown>;
}

export interface PayrollTransactionUpdate extends Partial<PayrollTransactionCreate> {
  status?: PaymentStatus;
}

export interface PayrollTransactionFilter {
  employeeId?: string;
  type?: string;
  status?: PaymentStatus | PaymentStatus[];
  startDate?: string;
  endDate?: string;
  search?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}

export interface PayrollTransactionSummary {
  totalAmount: number;
  completedCount: number;
  pendingCount: number;
  failedCount: number;
  byType: Array<{
    type: string;
    count: number;
    amount: number;
  }>;
  byStatus: Array<{
    status: string;
    count: number;
    amount: number;
  }>;
}

export interface PayrollTransactionExportOptions {
  format: 'csv' | 'excel' | 'pdf';
  includeDetails?: boolean;
  includeAttachments?: boolean;
  dateRange?: {
    start: string;
    end: string;
  };
  filters?: Omit<PayrollTransactionFilter, 'page' | 'limit' | 'sortBy' | 'sortOrder'>;
}

export const PAYROLL_TRANSACTION_TYPES = [
  { value: 'salary', label: 'Salary' },
  { value: 'bonus', label: 'Bonus' },
  { value: 'commission', label: 'Commission' },
  { value: 'reimbursement', label: 'Reimbursement' },
  { value: 'tax', label: 'Tax' },
  { value: 'other', label: 'Other' },
] as const;

export function getTransactionTypeLabel(type: string): string {
  const found = PAYROLL_TRANSACTION_TYPES.find(t => t.value === type);
  return found ? found.label : type;
}

export function getTransactionTypeColor(type: string): string {
  const colors: Record<string, string> = {
    salary: 'primary',
    bonus: 'success',
    commission: 'info',
    reimbursement: 'warning',
    tax: 'error',
    other: 'secondary',
  };
  return colors[type] || 'grey';
}
