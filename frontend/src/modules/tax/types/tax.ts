// Import common types
import { UUID, Nullable } from './common';

export enum TaxTransactionStatus {
  DRAFT = 'draft',
  POSTED = 'posted',
  VOIDED = 'voided',
  ADJUSTED = 'adjusted'
}

export enum TaxTransactionType {
  SALE = 'sale',
  PURCHASE = 'purchase',
  USE = 'use',
  IMPORT = 'import',
  EXPORT = 'export',
  TAX_ADJUSTMENT = 'tax_adjustment'
}

// Core Entities
export interface TaxPolicy {
  id: UUID;
  name: string;
  description: string;
  effective_date: string;
  expiry_date?: string;
  tax_rates: TaxRate[];
  tax_exemptions: TaxExemption[];
  created_at: string;
  updated_at: string;
  created_by?: UUID;
  updated_by?: UUID;
}

export interface TaxRate {
  id: UUID;
  name: string;
  rate: number;
  type: 'percentage' | 'fixed';
  category: string;
  effective_date: string;
  expiry_date?: string;
  is_active: boolean;
  jurisdiction_code?: string;
  tax_jurisdiction_id?: UUID;
  created_at: string;
  updated_at: string;
  created_by?: UUID;
  updated_by?: UUID;
}

export interface TaxExemption {
  id: UUID;
  type: string;
  reason: string;
  effective_date: string;
  expiry_date?: string;
  terms: string[];
  is_active: boolean;
  jurisdiction_code?: string;
  tax_jurisdiction_id?: UUID;
  created_at: string;
  updated_at: string;
  created_by?: UUID;
  updated_by?: UUID;
}

export interface TaxJurisdiction {
  id: UUID;
  code: string;
  name: string;
  level: 'country' | 'state' | 'county' | 'city' | 'special';
  parent_id?: UUID;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Transaction Types
export interface TaxTransaction {
  id: UUID;
  transaction_date: string;
  posting_date?: string;
  document_number: string;
  reference_number?: string;
  company_id: UUID;
  tax_type: string;
  tax_rate_id: UUID;
  taxable_amount: number;
  tax_amount: number;
  total_amount: number;
  jurisdiction_code?: string;
  tax_jurisdiction_id?: UUID;
  status: TaxTransactionStatus;
  transaction_type: TaxTransactionType;
  source_document_type?: string;
  source_document_id?: UUID;
  notes?: string;
  created_at: string;
  updated_at: string;
  created_by: UUID;
  updated_by?: UUID;
  posted_by?: UUID;
  posted_at?: string;
  components?: TaxTransactionComponent[];
  tax_rate?: TaxRate;
  tax_jurisdiction?: TaxJurisdiction;
}

export interface TaxTransactionComponent {
  id: UUID;
  transaction_id: UUID;
  tax_component: string;
  tax_rate: number;
  taxable_amount: number;
  tax_amount: number;
  jurisdiction_level?: string;
  jurisdiction_name?: string;
  jurisdiction_code?: string;
  tax_jurisdiction_id?: UUID;
  is_tax_inclusive?: boolean;
  tax_basis?: number;
  tax_type?: string;
  tax_category?: string;
  tax_authority?: string;
  tax_authority_id?: string;
  tax_registration_number?: string;
  tax_exemption_reason?: string;
  tax_exemption_certificate_number?: string;
  tax_exemption_certificate_expiry_date?: string;
  created_at: string;
  updated_at: string;
  created_by?: UUID;
  updated_by?: UUID;
}

// Request/Response Types
export interface TaxTransactionCreate {
  transaction_date: string | Date;
  document_number: string;
  reference_number?: string;
  company_id: UUID;
  tax_type: string;
  tax_rate_id: UUID;
  taxable_amount?: number;
  tax_amount?: number;
  total_amount?: number;
  jurisdiction_code?: string;
  tax_jurisdiction_id?: UUID;
  transaction_type: TaxTransactionType;
  source_document_type?: string;
  source_document_id?: UUID;
  notes?: string;
  status?: TaxTransactionStatus;
  is_tax_inclusive?: boolean;
  currency_code?: string;
  exchange_rate?: number;
  components: TaxTransactionComponentCreate[];
  metadata?: Record<string, any>;
  attachments?: {
    name: string;
    url: string;
    type: string;
    size: number;
  }[];
  custom_fields?: Record<string, any>;
}

export interface TaxTransactionUpdate extends Partial<TaxTransactionCreate> {
  id?: UUID;
  status?: TaxTransactionStatus;
  posted_by?: UUID;
  posted_at?: string | Date;
  void_reason?: string;
  voided_by?: UUID;
  voided_at?: string | Date;
  adjusted_from_id?: UUID;
  adjustment_notes?: string;
  components?: Array<Partial<TaxTransactionComponentCreate> & { id?: UUID }>;
  metadata?: Record<string, any>;
  custom_fields?: Record<string, any>;
}

export interface TaxTransactionComponentCreate {
  tax_component: string;
  tax_rate: number;
  taxable_amount: number;
  tax_amount: number;
  tax_basis?: number;
  jurisdiction_level?: string;
  jurisdiction_name?: string;
  jurisdiction_code?: string;
  tax_jurisdiction_id?: UUID;
  tax_type?: string;
  tax_category?: string;
  tax_authority?: string;
  tax_authority_id?: string;
  tax_registration_number?: string;
  is_tax_inclusive?: boolean;
  tax_exemption_reason?: string;
  tax_exemption_certificate_number?: string;
  tax_exemption_certificate_expiry_date?: string | Date;
  notes?: string;
  custom_fields?: Record<string, any>;
}

export interface TaxTransactionFilter {
  company_id?: UUID;
  status?: TaxTransactionStatus;
  transaction_type?: TaxTransactionType;
  start_date?: string | Date;
  end_date?: string | Date;
  tax_type?: string;
  jurisdiction_code?: string;
  tax_jurisdiction_id?: UUID;
  source_document_type?: string;
  source_document_id?: UUID;
  search?: string;
  sort_by?: string;
  sort_direction?: 'asc' | 'desc';
  page?: number;
  page_size?: number;
}

// Analytics Types
export enum TaxPeriod {
  CURRENT_MONTH = 'current_month',
  CURRENT_QUARTER = 'current_quarter',
  CURRENT_YEAR = 'current_year',
  CUSTOM = 'custom'
}

export interface TaxMetrics {
  totalTax: number;
  avgTaxPerEmployee: number;
  complianceRate: number;
  exemptionUsage: Record<string, number>;
  jurisdictionalBreakdown: Record<string, number>;
}

export interface TaxAnalyticsRequest {
  period: TaxPeriod;
  start_date?: string;
  end_date?: string;
}

export interface TaxAnalyticsResponse {
  metrics: TaxMetrics;
  insights: {
    compliance: string;
    optimization: string;
    risk: string;
  };
  period: {
    start: string;
    end: string;
  };
  data?: Record<string, any>[];
  summary?: Record<string, any>;
  warnings?: string[];
}

export interface ExportAnalyticsRequest {
  period: TaxPeriod;
  format: 'csv' | 'excel' | 'pdf';
  start_date?: string;
  end_date?: string;
}

export interface ExportAnalyticsResponse {
  url: string;
  filename: string;
  format: 'csv' | 'excel' | 'pdf';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  error?: string;
  file_size?: number;
  expires_at?: string;
  downloaded_at?: Nullable<string>;
}