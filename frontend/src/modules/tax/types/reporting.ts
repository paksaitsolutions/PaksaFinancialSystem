import { BaseModel } from '../base';

export interface TaxLiabilityReport {
  company_id: string;
  start_date: string;
  end_date: string;
  tax_type: string;
  jurisdiction_code: string;
  currency: string;
  total_taxable_amount: number;
  total_tax_amount: number;
  total_collected: number;
  total_owed: number;
  periods: TaxLiabilityPeriod[];
  summary_by_tax_type: TaxLiabilitySummary[];
  summary_by_jurisdiction: TaxLiabilitySummary[];
}

export interface TaxLiabilityPeriod {
  period_start: string;
  period_end: string;
  period_name: string;
  tax_type: string;
  jurisdiction_code: string;
  taxable_amount: number;
  tax_amount: number;
  collected_amount: number;
  owed_amount: number;
  transactions_count: number;
}

export interface TaxLiabilitySummary {
  tax_type: string;
  jurisdiction_code: string;
  jurisdiction_name: string;
  taxable_amount: number;
  tax_amount: number;
  collected_amount: number;
  owed_amount: number;
  transactions_count: number;
}

export interface TaxFiling extends BaseModel {
  company_id: string;
  tax_authority_id: string;
  tax_authority_name: string;
  tax_type: string;
  jurisdiction_code: string;
  jurisdiction_name: string;
  period_start: string;
  period_end: string;
  filing_date: string;
  due_date: string;
  status: 'draft' | 'prepared' | 'submitted' | 'accepted' | 'rejected' | 'paid';
  reference_number?: string;
  total_amount: number;
  tax_amount: number;
  penalty_amount: number;
  interest_amount: number;
  payment_date?: string;
  payment_reference?: string;
  notes?: string;
  submitted_by?: string;
  submitted_at?: string;
  reviewed_by?: string;
  reviewed_at?: string;
  filing_data?: any;
  submission_data?: any;
  documents: TaxFilingDocument[];
}

export interface TaxFilingDocument extends BaseModel {
  filing_id: string;
  document_type: string;
  file_name: string;
  file_type: string;
  file_size: number;
  file_path: string;
  description?: string;
  uploaded_by: string;
  uploaded_at: string;
}

export interface TaxFilingCreate {
  tax_authority_id: string;
  tax_type: string;
  jurisdiction_code: string;
  period_start: string;
  period_end: string;
  due_date: string;
  include_transactions: boolean;
}

export interface TaxFilingSubmit {
  reference_number: string;
  notes?: string;
  submission_data?: any;
}

export interface TaxFilingResponse {
  success: boolean;
  message: string;
  data: TaxFiling;
}

export interface TaxComplianceStatus {
  company_id: string;
  overall_status: 'compliant' | 'warning' | 'non_compliant';
  last_updated: string;
  status_by_tax_type: TaxTypeComplianceStatus[];
  status_by_jurisdiction: JurisdictionComplianceStatus[];
  upcoming_deadlines: TaxDeadline[];
  recent_filings: TaxFiling[];
  open_issues: ComplianceIssue[];
}

export interface TaxTypeComplianceStatus {
  tax_type: string;
  tax_type_name: string;
  status: 'compliant' | 'warning' | 'non_compliant';
  last_filing_date?: string;
  next_due_date?: string;
  days_until_due?: number;
  open_issues_count: number;
}

export interface JurisdictionComplianceStatus {
  jurisdiction_code: string;
  jurisdiction_name: string;
  status: 'compliant' | 'warning' | 'non_compliant';
  tax_types: string[];
  last_filing_date?: string;
  next_due_date?: string;
  days_until_due?: number;
  open_issues_count: number;
}

export interface TaxDeadline {
  tax_type: string;
  tax_type_name: string;
  jurisdiction_code: string;
  jurisdiction_name: string;
  period_start: string;
  period_end: string;
  due_date: string;
  days_until_due: number;
  status: 'upcoming' | 'due_soon' | 'overdue';
  filing_frequency: string;
  last_filing_date?: string;
}

export interface ComplianceIssue {
  id: string;
  type: 'missing_filing' | 'discrepancy' | 'warning' | 'error';
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  title: string;
  description: string;
  tax_type?: string;
  jurisdiction_code?: string;
  period_start?: string;
  period_end?: string;
  due_date?: string;
  created_at: string;
  updated_at: string;
  assigned_to?: string;
  resolution_notes?: string;
  resolved_at?: string;
  resolved_by?: string;
}

export interface TaxFilingUpcoming {
  tax_type: string;
  jurisdiction_code: string;
  tax_authority_id: string;
  tax_authority_name: string;
  frequency: string;
  due_date: string;
  days_until_due: number;
  last_filing_date?: string;
  last_filing_period?: string;
}

export interface TaxReportFilter {
  start_date?: string;
  end_date?: string;
  tax_types?: string[];
  jurisdiction_codes?: string[];
  group_by?: 'day' | 'week' | 'month' | 'quarter' | 'year';
  statuses?: string[];
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}

export interface TaxReportResponse<T> {
  data: T[];
  pagination: {
    total: number;
    page: number;
    limit: number;
    total_pages: number;
  };
  summary?: {
    total_taxable_amount: number;
    total_tax_amount: number;
    total_collected: number;
    total_owed: number;
    transactions_count: number;
  };
}
