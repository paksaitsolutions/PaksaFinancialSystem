// Customer related types
export interface Customer {
  id: string | number;
  name: string;
  code?: string;
  taxId?: string;
  vatNumber?: string;
  contactPerson?: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  postalCode?: string;
  country?: string;
  paymentTerms?: number; // in days
  creditLimit?: number;
  currency?: string;
  status: 'active' | 'inactive' | 'credit-hold';
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

// Invoice related types
export interface InvoiceItem {
  id: string | number;
  invoiceId: string | number;
  description: string;
  quantity: number;
  unitPrice: number;
  taxRate: number;
  taxAmount: number;
  total: number;
  glAccountId?: string | number;
  costCenterId?: string | number;
  projectId?: string | number;
  createdAt: string;
  updatedAt: string;
}

export interface Invoice {
  id: string | number;
  customerId: string | number;
  customer?: Customer;
  invoiceNumber: string;
  reference?: string;
  orderNumber?: string;
  invoiceDate: string;
  dueDate: string;
  status: 'draft' | 'sent' | 'viewed' | 'paid' | 'partially_paid' | 'overdue' | 'cancelled' | 'refunded';
  subtotal: number;
  taxAmount: number;
  discountAmount: number;
  total: number;
  currency: string;
  notes?: string;
  termsAndConditions?: string;
  paidAmount: number;
  outstandingAmount: number;
  items: InvoiceItem[];
  attachments?: string[];
  sentAt?: string;
  viewedAt?: string;
  paidAt?: string;
  paidBy?: string | number;
  paymentMethod?: string;
  paymentReference?: string;
  createdAt: string;
  updatedAt: string;
}

// Payment related types
export interface PaymentItem {
  id: string | number;
  paymentId: string | number;
  invoiceId: string | number;
  invoice?: Invoice;
  amount: number;
  discountAmount: number;
  taxAmount: number;
  total: number;
  glAccountId?: string | number;
  costCenterId?: string | number;
  projectId?: string | number;
  createdAt: string;
  updatedAt: string;
}

export interface Payment {
  id: string | number;
  customerId: string | number;
  customer?: Customer;
  paymentNumber: string;
  reference?: string;
  paymentDate: string;
  status: 'draft' | 'pending' | 'processed' | 'failed' | 'cancelled' | 'reconciled';
  amount: number;
  currency: string;
  exchangeRate?: number;
  paymentMethod: 'cash' | 'check' | 'credit_card' | 'bank_transfer' | 'other';
  paymentReference?: string;
  bankAccountId?: string | number;
  notes?: string;
  items: PaymentItem[];
  attachments?: string[];
  createdBy?: string | number;
  processedBy?: string | number;
  processedAt?: string;
  failureReason?: string;
  isPrepayment: boolean;
  createdAt: string;
  updatedAt: string;
}

// Credit Note related types
export interface CreditNoteItem {
  id: string | number;
  creditNoteId: string | number;
  description: string;
  quantity: number;
  unitPrice: number;
  taxRate: number;
  taxAmount: number;
  total: number;
  glAccountId?: string | number;
  costCenterId?: string | number;
  projectId?: string | number;
  createdAt: string;
  updatedAt: string;
}

export interface CreditNote {
  id: string | number;
  customerId: string | number;
  customer?: Customer;
  creditNoteNumber: string;
  reference?: string;
  invoiceId?: string | number;
  invoice?: Invoice;
  creditNoteDate: string;
  status: 'draft' | 'applied' | 'refunded' | 'void';
  reason?: string;
  subtotal: number;
  taxAmount: number;
  total: number;
  currency: string;
  notes?: string;
  appliedAmount: number;
  remainingAmount: number;
  items: CreditNoteItem[];
  attachments?: string[];
  createdBy?: string | number;
  appliedAt?: string;
  appliedBy?: string | number;
  refundedAt?: string;
  refundedBy?: string | number;
  refundTransactionId?: string;
  voidedAt?: string;
  voidedBy?: string | number;
  voidReason?: string;
  createdAt: string;
  updatedAt: string;
}

// Report related types
export interface ARAgingReport {
  customerId: string | number;
  customerName: string;
  current: number;
  days30: number;
  days60: number;
  days90: number;
  days120: number;
  daysOver120: number;
  total: number;
}

export interface ARCustomerBalance {
  customerId: string | number;
  customerName: string;
  totalInvoices: number;
  totalAmount: number;
  paidAmount: number;
  outstandingAmount: number;
  creditLimit: number;
  availableCredit: number;
  lastPaymentDate?: string;
  lastPaymentAmount?: number;
}

// API response types
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  meta?: {
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  };
}

// Form types for creating/updating entities
export interface CustomerFormData extends Omit<Customer, 'id' | 'createdAt' | 'updatedAt'> {}

export interface InvoiceFormData extends Omit<Invoice, 'id' | 'createdAt' | 'updatedAt' | 'items' | 'customer'> {
  items: Omit<InvoiceItem, 'id' | 'invoiceId' | 'createdAt' | 'updatedAt'>[];
}

export interface PaymentFormData extends Omit<Payment, 'id' | 'createdAt' | 'updatedAt' | 'items' | 'customer'> {
  items: Omit<PaymentItem, 'id' | 'paymentId' | 'createdAt' | 'updatedAt' | 'invoice'>[];
  invoiceIds?: (string | number)[]; // For applying payments to specific invoices
}

export interface CreditNoteFormData extends Omit<CreditNote, 'id' | 'createdAt' | 'updatedAt' | 'items' | 'customer' | 'invoice'> {
  items: Omit<CreditNoteItem, 'id' | 'creditNoteId' | 'createdAt' | 'updatedAt'>[];
  applyToInvoice?: boolean;
  invoiceId?: string | number;
}

// Filter and query parameter types
export interface CustomerFilterParams {
  search?: string;
  status?: string;
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface InvoiceFilterParams extends CustomerFilterParams {
  customerId?: string | number;
  status?: string;
  fromDate?: string;
  toDate?: string;
  minAmount?: number;
  maxAmount?: number;
  paidStatus?: 'paid' | 'unpaid' | 'overdue' | 'partial';
}

export interface PaymentFilterParams extends CustomerFilterParams {
  customerId?: string | number;
  status?: string;
  fromDate?: string;
  toDate?: string;
  paymentMethod?: string;
  minAmount?: number;
  maxAmount?: number;
}

export interface CreditNoteFilterParams extends CustomerFilterParams {
  customerId?: string | number;
  status?: string;
  fromDate?: string;
  toDate?: string;
  minAmount?: number;
  maxAmount?: number;
  invoiceId?: string | number;
}

// Enums
export enum InvoiceStatus {
  DRAFT = 'draft',
  SENT = 'sent',
  VIEWED = 'viewed',
  PAID = 'paid',
  PARTIALLY_PAID = 'partially_paid',
  OVERDUE = 'overdue',
  CANCELLED = 'cancelled',
  REFUNDED = 'refunded',
}

export enum PaymentStatus {
  DRAFT = 'draft',
  PENDING = 'pending',
  PROCESSED = 'processed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
  RECONCILED = 'reconciled',
}

export enum CreditNoteStatus {
  DRAFT = 'draft',
  APPLIED = 'applied',
  REFUNDED = 'refunded',
  VOID = 'void',
}

export enum PaymentMethod {
  CASH = 'cash',
  CHECK = 'check',
  CREDIT_CARD = 'credit_card',
  BANK_TRANSFER = 'bank_transfer',
  OTHER = 'other',
}

// Utility types
export type KeyValuePair = {
  [key: string]: any;
};

export type SelectOption = {
  label: string;
  value: string | number;
  [key: string]: any;
};
