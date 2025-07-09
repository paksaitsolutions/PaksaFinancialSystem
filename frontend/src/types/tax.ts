import { type PaginatedResponse } from './common';

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
