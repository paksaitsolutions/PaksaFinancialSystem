/**
 * Payment method types
 */
export type PaymentMethod = 
  | 'bank_transfer'
  | 'credit_card'
  | 'debit_card'
  | 'paypal'
  | 'cash'
  | 'check'
  | 'direct_debit'
  | 'other';

/**
 * Payment status types
 */
export type PaymentStatus = 
  | 'pending'
  | 'processing'
  | 'completed'
  | 'failed'
  | 'cancelled'
  | 'refunded'
  | 'partially_refunded';

/**
 * Payment currency
 */
export type Currency = 'USD' | 'EUR' | 'GBP' | 'JPY' | 'AUD' | 'CAD' | 'CNY' | 'INR' | 'PKR' | 'SAR' | 'AED' | string;

/**
 * Base payment interface
 */
export interface BasePayment {
  id: string;
  amount: number;
  currency: Currency;
  status: PaymentStatus;
  paymentMethod: PaymentMethod;
  reference: string;
  description?: string;
  metadata?: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

/**
 * Payment details specific to bank transfers
 */
export interface BankTransferPayment extends BasePayment {
  paymentMethod: 'bank_transfer';
  bankName: string;
  accountNumber: string;
  routingNumber?: string;
  iban?: string;
  swiftCode?: string;
  beneficiaryName: string;
}

/**
 * Payment details specific to credit/debit cards
 */
export interface CardPayment extends BasePayment {
  paymentMethod: 'credit_card' | 'debit_card';
  cardLast4: string;
  cardBrand: string;
  cardExpiry: string; // MM/YY format
  cardholderName: string;
  billingAddress?: {
    line1: string;
    line2?: string;
    city: string;
    state: string;
    postalCode: string;
    country: string;
  };
}

/**
 * Payment details specific to PayPal
 */
export interface PayPalPayment extends BasePayment {
  paymentMethod: 'paypal';
  payerEmail: string;
  transactionId: string;
}

/**
 * Payment details for cash payments
 */
export interface CashPayment extends BasePayment {
  paymentMethod: 'cash';
  receivedBy: string;
  receiptNumber?: string;
}

/**
 * Payment details for check payments
 */
export interface CheckPayment extends BasePayment {
  paymentMethod: 'check';
  checkNumber: string;
  bankName: string;
  accountNumber: string;
  issueDate: string;
  clearedDate?: string;
}

/**
 * Payment details for direct debit payments
 */
export interface DirectDebitPayment extends BasePayment {
  paymentMethod: 'direct_debit';
  accountHolder: string;
  accountNumber: string;
  routingNumber: string;
  bankName: string;
  mandateId?: string;
}

/**
 * Payment details for other payment methods
 */
export interface OtherPayment extends BasePayment {
  paymentMethod: 'other';
  methodDetails: string;
  referenceNumber?: string;
}

/**
 * Union type for all payment methods
 */
export type Payment = 
  | BankTransferPayment
  | CardPayment
  | PayPalPayment
  | CashPayment
  | CheckPayment
  | DirectDebitPayment
  | OtherPayment;

/**
 * Payment creation DTO
 */
export interface CreatePaymentDto {
  amount: number;
  currency: Currency;
  paymentMethod: PaymentMethod;
  reference: string;
  description?: string;
  metadata?: Record<string, unknown>;
  
  // Method-specific fields (only include the ones relevant to the payment method)
  bankName?: string;
  accountNumber?: string;
  routingNumber?: string;
  iban?: string;
  swiftCode?: string;
  beneficiaryName?: string;
  cardLast4?: string;
  cardBrand?: string;
  cardExpiry?: string;
  cardholderName?: string;
  billingAddress?: {
    line1: string;
    line2?: string;
    city: string;
    state: string;
    postalCode: string;
    country: string;
  };
  payerEmail?: string;
  receivedBy?: string;
  receiptNumber?: string;
  checkNumber?: string;
  issueDate?: string;
  accountHolder?: string;
  methodDetails?: string;
  referenceNumber?: string;
}

/**
 * Payment update DTO
 */
export interface UpdatePaymentDto extends Partial<CreatePaymentDto> {
  status?: PaymentStatus;
  clearedDate?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Payment filter options
 */
export interface PaymentFilter {
  status?: PaymentStatus | PaymentStatus[];
  paymentMethod?: PaymentMethod | PaymentMethod[];
  minAmount?: number;
  maxAmount?: number;
  currency?: Currency;
  reference?: string;
  startDate?: string;
  endDate?: string;
  search?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}

/**
 * Payment summary statistics
 */
export interface PaymentSummary {
  totalAmount: number;
  completedAmount: number;
  pendingAmount: number;
  failedAmount: number;
  refundedAmount: number;
  count: number;
  byStatus: Array<{
    status: PaymentStatus;
    count: number;
    amount: number;
  }>;
  byMethod: Array<{
    method: PaymentMethod;
    count: number;
    amount: number;
  }>;
  byCurrency: Array<{
    currency: Currency;
    count: number;
    amount: number;
  }>;
}

/**
 * Payment export options
 */
export interface PaymentExportOptions {
  format: 'csv' | 'excel' | 'pdf';
  includeDetails?: boolean;
  includeAttachments?: boolean;
  dateRange?: {
    start: string;
    end: string;
  };
  filters?: Omit<PaymentFilter, 'page' | 'limit' | 'sortBy' | 'sortOrder'>;
}

/**
 * Payment webhook event types
 */
export type PaymentWebhookEvent = 
  | 'payment.created'
  | 'payment.updated'
  | 'payment.completed'
  | 'payment.failed'
  | 'payment.refunded'
  | 'payment.dispute.created'
  | 'payment.dispute.updated';

/**
 * Payment webhook payload
 */
export interface PaymentWebhookPayload {
  event: PaymentWebhookEvent;
  data: {
    payment: Payment;
    previousAttributes?: Partial<Payment>;
  };
  created: number;
  id: string;
  type: string;
}

/**
 * Payment method details for display
 */
export interface PaymentMethodDetails {
  id: string;
  type: PaymentMethod;
  displayName: string;
  icon: string;
  description: string;
  supportedCurrencies: Currency[];
  isAvailable: boolean;
  fees: {
    percentage: number;
    fixed: number;
    currency: Currency;
  };
  minAmount?: number;
  maxAmount?: number;
  supportedCountries?: string[];
  requiresVerification?: boolean;
  isDefault: boolean;
  metadata?: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

/**
 * Payment method creation DTO
 */
export interface CreatePaymentMethodDto {
  type: PaymentMethod;
  displayName: string;
  icon: string;
  description: string;
  supportedCurrencies: Currency[];
  isAvailable: boolean;
  fees: {
    percentage: number;
    fixed: number;
    currency: Currency;
  };
  minAmount?: number;
  maxAmount?: number;
  supportedCountries?: string[];
  requiresVerification?: boolean;
  isDefault?: boolean;
  metadata?: Record<string, unknown>;
}

/**
 * Payment method update DTO
 */
export type UpdatePaymentMethodDto = Partial<CreatePaymentMethodDto>;

/**
 * Payment method filter options
 */
export interface PaymentMethodFilter {
  type?: PaymentMethod | PaymentMethod[];
  isAvailable?: boolean;
  supportedCurrency?: Currency;
  search?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}

/**
 * Payment method summary statistics
 */
export interface PaymentMethodSummary {
  totalMethods: number;
  activeMethods: number;
  byType: Array<{
    type: PaymentMethod;
    count: number;
    totalAmount: number;
    currency: Currency;
  }>;
}

/**
 * Payment method export options
 */
export interface PaymentMethodExportOptions {
  format: 'csv' | 'excel' | 'pdf';
  includeDetails?: boolean;
  filters?: Omit<PaymentMethodFilter, 'page' | 'limit' | 'sortBy' | 'sortOrder'>;
}

/**
 * Payment method webhook event types
 */
export type PaymentMethodWebhookEvent = 
  | 'payment_method.created'
  | 'payment_method.updated'
  | 'payment_method.deleted';

/**
 * Payment method webhook payload
 */
export interface PaymentMethodWebhookPayload {
  event: PaymentMethodWebhookEvent;
  data: {
    paymentMethod: PaymentMethodDetails;
    previousAttributes?: Partial<PaymentMethodDetails>;
  };
  created: number;
  id: string;
  type: string;
}

/**
 * Payment method verification status
 */
export interface PaymentMethodVerification {
  id: string;
  paymentMethodId: string;
  status: 'pending' | 'verified' | 'failed';
  attempts: number;
  lastAttemptAt?: string;
  verifiedAt?: string;
  verificationMethod?: string;
  verifiedBy?: string;
  metadata?: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

/**
 * Payment method verification DTO
 */
export interface VerifyPaymentMethodDto {
  paymentMethodId: string;
  verificationMethod: string;
  verificationCode?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Payment method verification filter options
 */
export interface PaymentMethodVerificationFilter {
  paymentMethodId?: string;
  status?: 'pending' | 'verified' | 'failed';
  verificationMethod?: string;
  verifiedBy?: string;
  startDate?: string;
  endDate?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}

/**
 * Payment method verification summary statistics
 */
export interface PaymentMethodVerificationSummary {
  totalVerifications: number;
  pendingVerifications: number;
  verified: number;
  failed: number;
  byStatus: Array<{
    status: string;
    count: number;
  }>;
  byMethod: Array<{
    method: string;
    count: number;
  }>;
}

/**
 * Payment method verification export options
 */
export interface PaymentMethodVerificationExportOptions {
  format: 'csv' | 'excel' | 'pdf';
  includeDetails?: boolean;
  filters?: Omit<PaymentMethodVerificationFilter, 'page' | 'limit' | 'sortBy' | 'sortOrder'>;
}

/**
 * Payment method verification webhook event types
 */
export type PaymentMethodVerificationWebhookEvent = 
  | 'payment_method_verification.created'
  | 'payment_method_verification.updated'
  | 'payment_method_verification.completed';

/**
 * Payment method verification webhook payload
 */
export interface PaymentMethodVerificationWebhookPayload {
  event: PaymentMethodVerificationWebhookEvent;
  data: {
    verification: PaymentMethodVerification;
    previousAttributes?: Partial<PaymentMethodVerification>;
  };
  created: number;
  id: string;
  type: string;
}
