export interface TaxExemption {
  id: string;
  exemptionNumber: string;
  customerId: string;
  customerName?: string;
  taxCode: string;
  taxCodeDescription?: string;
  exemptionReason: string;
  exemptionCertificateNumber?: string;
  startDate: string;
  endDate?: string;
  status: 'active' | 'expired' | 'revoked' | 'pending';
  createdAt: string;
  updatedAt: string;
  createdBy?: string;
  updatedBy?: string;
  notes?: string;
  items?: TaxExemptionItem[];
  attachments?: TaxExemptionAttachment[];
  approvalStatus?: 'draft' | 'pending_approval' | 'approved' | 'rejected';
  approvedBy?: string;
  approvedAt?: string;
  rejectionReason?: string;
}

export interface TaxExemptionItem {
  id: string;
  exemptionId: string;
  productId?: string;
  productName?: string;
  productCode?: string;
  serviceId?: string;
  serviceName?: string;
  serviceCode?: string;
  taxCode: string;
  taxRate: number;
  exemptionRate: number; // 0-100%
  effectiveFrom: string;
  effectiveTo?: string;
  status: 'active' | 'expired' | 'revoked';
  createdAt: string;
  updatedAt: string;
}

export interface TaxExemptionAttachment {
  id: string;
  exemptionId: string;
  fileName: string;
  fileType: string;
  fileSize: number;
  fileUrl: string;
  uploadedBy: string;
  uploadedAt: string;
  description?: string;
}

export interface TaxExemptionFormData {
  customerId: string;
  taxCode: string;
  exemptionReason: string;
  exemptionCertificateNumber?: string;
  startDate: string;
  endDate?: string;
  status: 'active' | 'expired' | 'revoked' | 'pending';
  notes?: string;
  items: Omit<TaxExemptionItem, 'id' | 'exemptionId' | 'createdAt' | 'updatedAt' | 'status'>[];
}

export interface TaxExemptionFilter {
  customerId?: string;
  taxCode?: string;
  status?: string;
  startDateFrom?: string;
  startDateTo?: string;
  endDateFrom?: string;
  endDateTo?: string;
  search?: string;
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface TaxRule {
  id: string;
  ruleName: string;
  description?: string;
  taxCode: string;
  taxRate: number;
  isActive: boolean;
  effectiveFrom: string;
  effectiveTo?: string;
  priority: number;
  conditions: TaxRuleCondition[];
  createdAt: string;
  updatedAt: string;
  createdBy?: string;
  updatedBy?: string;
}

export interface TaxRuleCondition {
  field: string;
  operator: 'equals' | 'not_equals' | 'contains' | 'starts_with' | 'ends_with' | 'greater_than' | 'less_than' | 'in' | 'not_in';
  value: string | number | boolean | (string | number)[];
}

export interface TaxRuleFormData {
  ruleName: string;
  description?: string;
  taxCode: string;
  taxRate: number;
  isActive: boolean;
  effectiveFrom: string;
  effectiveTo?: string;
  priority: number;
  conditions: TaxRuleCondition[];
}

export interface TaxRuleFilter {
  taxCode?: string;
  isActive?: boolean;
  effectiveDate?: string;
  search?: string;
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface TaxCode {
  id: string;
  code: string;
  description: string;
  rate: number;
  type: 'sales' | 'purchase' | 'withholding' | 'other';
  isRecoverable: boolean;
  isCompound: boolean;
  isActive: boolean;
  accountId?: string;
  accountName?: string;
  taxAuthorityId?: string;
  taxAuthorityName?: string;
  createdAt: string;
  updatedAt: string;
}

export interface TaxCodeFormData {
  code: string;
  description: string;
  rate: number;
  type: 'sales' | 'purchase' | 'withholding' | 'other';
  isRecoverable: boolean;
  isCompound: boolean;
  isActive: boolean;
  accountId?: string;
  taxAuthorityId?: string;
}

export interface TaxCodeFilter {
  type?: string;
  isActive?: boolean;
  search?: string;
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface TaxReport {
  id: string;
  reportName: string;
  reportType: 'sales' | 'purchase' | 'vat' | 'withholding' | 'custom';
  periodStart: string;
  periodEnd: string;
  status: 'draft' | 'submitted' | 'approved' | 'rejected' | 'filed';
  totalTaxAmount: number;
  totalTaxableAmount: number;
  totalExemptAmount: number;
  currency: string;
  filingDate?: string;
  dueDate: string;
  submittedBy?: string;
  submittedAt?: string;
  approvedBy?: string;
  approvedAt?: string;
  rejectionReason?: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface TaxReportFilter {
  reportType?: string;
  status?: string;
  periodStartFrom?: string;
  periodStartTo?: string;
  periodEndFrom?: string;
  periodEndTo?: string;
  search?: string;
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface TaxAuthority {
  id: string;
  name: string;
  code: string;
  taxId: string;
  contactPerson?: string;
  email?: string;
  phone?: string;
  addressLine1?: string;
  addressLine2?: string;
  city?: string;
  state?: string;
  postalCode?: string;
  country: string;
  isActive: boolean;
  paymentInstructions?: string;
  filingInstructions?: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface TaxAuthorityFormData {
  name: string;
  code: string;
  taxId: string;
  contactPerson?: string;
  email?: string;
  phone?: string;
  addressLine1?: string;
  addressLine2?: string;
  city?: string;
  state?: string;
  postalCode?: string;
  country: string;
  isActive: boolean;
  paymentInstructions?: string;
  filingInstructions?: string;
  notes?: string;
}

export interface TaxAuthorityFilter {
  isActive?: boolean;
  country?: string;
  search?: string;
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// Response types for API calls
export interface TaxExemptionResponse {
  data: TaxExemption | TaxExemption[];
  meta?: {
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  };
}

export interface TaxRuleResponse {
  data: TaxRule | TaxRule[];
  meta?: {
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  };
}

export interface TaxCodeResponse {
  data: TaxCode | TaxCode[];
  meta?: {
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  };
}

export interface TaxReportResponse {
  data: TaxReport | TaxReport[];
  meta?: {
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  };
}

export interface TaxAuthorityResponse {
  data: TaxAuthority | TaxAuthority[];
  meta?: {
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  };
}

// Enum for tax exemption statuses
export enum TaxExemptionStatus {
  DRAFT = 'draft',
  PENDING = 'pending',
  ACTIVE = 'active',
  EXPIRED = 'expired',
  REVOKED = 'revoked',
  REJECTED = 'rejected'
}

// Enum for tax report statuses
export enum TaxReportStatus {
  DRAFT = 'draft',
  SUBMITTED = 'submitted',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  FILED = 'filed'
}

// Type for tax calculation result
export interface TaxCalculationResult {
  taxableAmount: number;
  taxAmount: number;
  taxRate: number;
  taxCode: string;
  taxDescription?: string;
  isTaxable: boolean;
  isExempt: boolean;
  exemptionId?: string;
  exemptionReason?: string;
  taxBreakdown?: {
    baseAmount: number;
    taxAmount: number;
    taxName: string;
    taxRate: number;
  }[];
}

// Type for tax calculation request
export interface TaxCalculationRequest {
  customerId?: string;
  customerTaxGroupId?: string;
  taxDate: string;
  items: {
    id: string;
    type: 'product' | 'service' | 'shipping' | 'discount' | 'other';
    productId?: string;
    serviceId?: string;
    quantity: number;
    unitPrice: number;
    taxCode?: string;
    isTaxInclusive: boolean;
    discountAmount?: number;
    discountPercent?: number;
  }[];
  shippingAddress?: {
    country: string;
    state?: string;
    city?: string;
    postalCode?: string;
  };
  billingAddress?: {
    country: string;
    state?: string;
    city?: string;
    postalCode?: string;
  };
  currency: string;
  isTaxExempt?: boolean;
  exemptionCertificateNumber?: string;
  applyTaxHolidays?: boolean;
}

// Type for tax calculation response
export interface TaxCalculationResponse {
  success: boolean;
  message?: string;
  data?: {
    totalTaxableAmount: number;
    totalTaxAmount: number;
    totalAmount: number;
    currency: string;
    isTaxInclusive: boolean;
    taxDate: string;
    items: Array<{
      id: string;
      taxableAmount: number;
      taxAmount: number;
      totalAmount: number;
      taxBreakdown: Array<{
        taxCode: string;
        taxName: string;
        taxRate: number;
        taxAmount: number;
        isExempt: boolean;
        exemptionId?: string;
        exemptionReason?: string;
      }>;
    }>;
    taxSummary: Array<{
      taxCode: string;
      taxName: string;
      taxRate: number;
      taxableAmount: number;
      taxAmount: number;
    }>;
  };
  warnings?: string[];
  errors?: string[];
} { type PaginatedResponse } from './common';

export type TaxType = 'sales' | 'vat' | 'gst' | 'income' | 'withholding' | 'excise' | 'custom';

export interface TaxJurisdiction {
  countryCode: string;
  stateCode?: string;
  city?: string;
  isEu?: boolean;
  taxAuthority?: string;
  authorityWebsite?: string;
  [key: string]: any; // For additional properties
}

export interface TaxRate {
  rate: number;
  effectiveFrom: string; // ISO date string
  effectiveTo?: string; // ISO date string
  description?: string;
  isStandardRate?: boolean;
  [key: string]: any; // For additional properties
}

export interface TaxRule {
  id: string;
  code: string;
  name: string;
  description?: string;
  type: TaxType;
  jurisdiction: TaxJurisdiction;
  rates: TaxRate[];
  category?: string;
  isActive: boolean;
  requiresTaxId?: boolean;
  taxIdFormat?: string;
  taxIdValidationRegex?: string;
  accountingCode?: string;
  glAccountCode?: string;
  tags: string[];
  metadata: Record<string, any>;
  createdAt: string; // ISO date string
  updatedAt: string; // ISO date string
  createdBy: string;
  updatedBy: string;
  [key: string]: any; // For additional properties
}

export interface TaxExemption {
  id: string;
  exemptionCode: string;
  description: string;
  certificateRequired: boolean;
  validFrom: string; // ISO date string
  validTo?: string; // ISO date string
  taxTypes: TaxType[];
  jurisdictions: TaxJurisdiction[];
  metadata: Record<string, any>;
  createdAt: string; // ISO date string
  updatedAt: string; // ISO date string
  createdBy: string;
  updatedBy: string;
  [key: string]: any; // For additional properties
}

export interface TaxCalculationRequest {
  amount: number;
  taxType: TaxType;
  countryCode: string;
  stateCode?: string;
  city?: string;
  isBusiness?: boolean;
  taxExempt?: boolean;
  exemptionCode?: string;
  forDate?: string; // ISO date string
  lineItems?: Array<{
    id: string;
    amount: number;
    taxCode?: string;
    description?: string;
    [key: string]: any;
  }>;
  customerTaxId?: string;
  customerTaxIdType?: string;
  customerTaxIdValid?: boolean;
  customerType?: string;
  customerCountryCode?: string;
  customerStateCode?: string;
  customerCity?: string;
  customerZip?: string;
  customerName?: string;
  customerEmail?: string;
  customerPhone?: string;
  shippingAddressSameAsBilling?: boolean;
  shippingCountryCode?: string;
  shippingStateCode?: string;
  shippingCity?: string;
  shippingZip?: string;
  orderId?: string;
  orderDate?: string; // ISO date string
  currency?: string;
  metadata?: Record<string, any>;
  [key: string]: any; // For additional properties
}

export interface TaxCalculationResult {
  taxableAmount: number;
  taxAmount: number;
  taxRateUsed: number;
  taxRule: TaxRule;
  taxType: TaxType;
  jurisdiction: TaxJurisdiction;
  isExempt: boolean;
  exemption?: TaxExemption;
  breakdown: Array<{
    taxableAmount: number;
    rate: number;
    taxAmount: number;
    taxRuleCode: string;
    taxRuleName: string;
    jurisdiction: string;
    [key: string]: any;
  }>;
  metadata?: Record<string, any>;
  [key: string]: any; // For additional properties
}

export interface TaxValidationRequest {
  taxId: string;
  countryCode: string;
  taxType?: TaxType;
  companyName?: string;
  address?: string;
  city?: string;
  state?: string;
  zip?: string;
  vatValidation?: boolean;
  [key: string]: any; // For additional properties
}

export interface TaxValidationResponse {
  valid: boolean;
  taxId: string;
  countryCode: string;
  taxType?: TaxType;
  normalizedTaxId?: string;
  companyName?: string;
  address?: string;
  city?: string;
  state?: string;
  zip?: string;
  viesValid?: boolean;
  viesName?: string;
  viesAddress?: string;
  validationDate?: string; // ISO date string
  message?: string;
  [key: string]: any; // For additional properties
}

// Response types for API calls
export type TaxRulesResponse = PaginatedResponse<TaxRule>;
export type TaxRuleResponse = TaxRule;
export type TaxExemptionsResponse = PaginatedResponse<TaxExemption>;
export type TaxExemptionResponse = TaxExemption;

// Form interfaces for UI components
export interface TaxRuleFormData {
  code: string;
  name: string;
  description: string;
  type: TaxType;
  jurisdiction: {
    countryCode: string;
    stateCode?: string;
    city?: string;
    isEu: boolean;
    taxAuthority?: string;
    authorityWebsite?: string;
  };
  rates: Array<{
    rate: number;
    effectiveFrom: string;
    effectiveTo?: string;
    description: string;
    isStandardRate: boolean;
  }>;
  category?: string;
  isActive: boolean;
  requiresTaxId: boolean;
  taxIdFormat?: string;
  taxIdValidationRegex?: string;
  accountingCode?: string;
  glAccountCode?: string;
  tags: string[];
  metadata: Record<string, any>;
}

export interface TaxExemptionFormData {
  exemptionCode: string;
  description: string;
  certificateRequired: boolean;
  validFrom: string;
  validTo?: string;
  taxTypes: TaxType[];
  jurisdictions: Array<{
    countryCode: string;
    stateCode?: string;
    city?: string;
  }>;
  metadata: Record<string, any>;
}

// Filter interfaces
export interface TaxRuleFilter {
  taxType?: TaxType;
  countryCode?: string;
  stateCode?: string;
  city?: string;
  isActive?: boolean;
  category?: string;
  tags?: string[];
  search?: string;
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface TaxExemptionFilter extends Omit<TaxRuleFilter, 'taxType' | 'category'> {
  taxTypes?: TaxType[];
  validOn?: string; // ISO date string
}

// Utility types
export type TaxRateWithRule = TaxRate & {
  ruleId: string;
  ruleName: string;
  ruleCode: string;
};

export type TaxJurisdictionWithRates = TaxJurisdiction & {
  rates: TaxRateWithRule[];
};

export type TaxSummary = {
  taxableAmount: number;
  taxAmount: number;
  taxRates: Array<{
    rate: number;
    amount: number;
    ruleCode: string;
    ruleName: string;
  }>;
};
