// Vendor related types
export interface Vendor {
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
  currency?: string;
  status: 'active' | 'inactive' | 'on-hold';
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
  vendorId: string | number;
  vendor?: Vendor;
  invoiceNumber: string;
  reference?: string;
  orderNumber?: string;
  invoiceDate: string;
  dueDate: string;
  status: 'draft' | 'pending' | 'approved' | 'rejected' | 'paid' | 'partially_paid' | 'cancelled';
  subtotal: number;
  taxAmount: number;
  discountAmount: number;
  total: number;
  currency: string;
  notes?: string;
  termsAndConditions?: string;
  rejectionReason?: string;
  paidAmount: number;
  outstandingAmount: number;
  items: InvoiceItem[];
  attachments?: string[];
  createdBy?: string | number;
  approvedBy?: string | number;
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
  vendorId: string | number;
  vendor?: Vendor;
  paymentNumber: string;
  reference?: string;
  paymentDate: string;
  dueDate?: string;
  status: 'draft' | 'pending' | 'processed' | 'failed' | 'cancelled' | 'scheduled' | 'reconciled';
  amount: number;
  currency: string;
  exchangeRate?: number;
  paymentMethod: 'check' | 'bank_transfer' | 'credit_card' | 'cash' | 'other';
  paymentReference?: string;
  bankAccountId?: string | number;
  notes?: string;
  items: PaymentItem[];
  attachments?: string[];
  createdBy?: string | number;
  processedBy?: string | number;
  processedAt?: string;
  failureReason?: string;
  isRecurring: boolean;
  recurringId?: string | number;
  nextPaymentDate?: string;
  createdAt: string;
  updatedAt: string;
}

// Report related types
export interface APAgingReport {
  vendorId: string | number;
  vendorName: string;
  current: number;
  days30: number;
  days60: number;
  days90: number;
  days120: number;
  daysOver120: number;
  total: number;
}

export interface APVendorBalance {
  vendorId: string | number;
  vendorName: string;
  totalInvoices: number;
  totalAmount: number;
  paidAmount: number;
  outstandingAmount: number;
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
export interface VendorFormData extends Omit<Vendor, 'id' | 'createdAt' | 'updatedAt'> {}
export interface InvoiceFormData extends Omit<Invoice, 'id' | 'createdAt' | 'updatedAt' | 'items' | 'vendor'> {
  items: Omit<InvoiceItem, 'id' | 'invoiceId' | 'createdAt' | 'updatedAt'>[];
}
export interface PaymentFormData extends Omit<Payment, 'id' | 'createdAt' | 'updatedAt' | 'items' | 'vendor'> {
  items: Omit<PaymentItem, 'id' | 'paymentId' | 'createdAt' | 'updatedAt' | 'invoice'>[];
}

// Filter and query parameter types
export interface VendorFilterParams {
  search?: string;
  status?: string;
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface InvoiceFilterParams extends VendorFilterParams {
  vendorId?: string | number;
  status?: string;
  fromDate?: string;
  toDate?: string;
  minAmount?: number;
  maxAmount?: number;
  paidStatus?: 'paid' | 'unpaid' | 'overdue' | 'partial';
}

export interface PaymentFilterParams extends VendorFilterParams {
  vendorId?: string | number;
  status?: string;
  fromDate?: string;
  toDate?: string;
  paymentMethod?: string;
  minAmount?: number;
  maxAmount?: number;
}

// Enums
export enum InvoiceStatus {
  DRAFT = 'draft',
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  PAID = 'paid',
  PARTIALLY_PAID = 'partially_paid',
  CANCELLED = 'cancelled',
}

export enum PaymentStatus {
  DRAFT = 'draft',
  PENDING = 'pending',
  PROCESSED = 'processed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
  SCHEDULED = 'scheduled',
  RECONCILED = 'reconciled',
}

export enum PaymentMethod {
  CHECK = 'check',
  BANK_TRANSFER = 'bank_transfer',
  CREDIT_CARD = 'credit_card',
  CASH = 'cash',
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
