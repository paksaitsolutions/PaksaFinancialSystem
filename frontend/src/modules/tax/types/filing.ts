export interface TaxFiling {
  id?: string;
  company_id: string;
  tax_type: string;
  tax_period_id: string;
  jurisdiction_id: string;
  due_date: string;
  filing_date?: string;
  status?: 'draft' | 'submitted' | 'approved' | 'rejected' | 'paid' | 'overdue';
  currency: string;
  tax_amount: number;
  penalty_amount?: number;
  interest_amount?: number;
  total_amount?: number;
  notes?: string;
  metadata?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
  submitted_by?: string;
  reviewed_by?: string;
  reviewed_at?: string;
  payment_reference?: string;
  payment_date?: string;
  payment_method?: string;
  payment_status?: 'pending' | 'partial' | 'paid' | 'failed' | 'refunded';
  attachments?: TaxFilingAttachment[];
}

export interface TaxFilingAttachment {
  id: string;
  filing_id: string;
  file_name: string;
  file_type: string;
  file_size: number;
  file_url: string;
  attachment_type: 'return' | 'supporting_document' | 'receipt' | 'other';
  description?: string;
  uploaded_by: string;
  uploaded_at: string;
  metadata?: Record<string, any>;
}

export interface TaxFilingFilter {
  tax_type?: string;
  jurisdiction_id?: string;
  tax_period_id?: string;
  status?: string;
  payment_status?: string;
  due_date_from?: string;
  due_date_to?: string;
  filing_date_from?: string;
  filing_date_to?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  page?: number;
  per_page?: number;
}

export interface TaxFilingStats {
  total: number;
  draft: number;
  submitted: number;
  approved: number;
  rejected: number;
  paid: number;
  overdue: number;
  total_tax_amount: number;
  total_penalty_amount: number;
  total_interest_amount: number;
  total_amount: number;
  by_tax_type: Array<{
    tax_type: string;
    count: number;
    amount: number;
  }>;
  by_jurisdiction: Array<{
    jurisdiction_id: string;
    jurisdiction_name: string;
    count: number;
    amount: number;
  }>;
  by_period: Array<{
    period_id: string;
    period_name: string;
    count: number;
    amount: number;
  }>;
}

export interface TaxFilingCreateRequest extends Omit<TaxFiling, 'id' | 'created_at' | 'updated_at' | 'status' | 'total_amount' | 'attachments'> {
  attachments?: Array<{
    file_name: string;
    file_type: string;
    file_size: number;
    file_data: string; // base64 encoded file
    attachment_type: 'return' | 'supporting_document' | 'receipt' | 'other';
    description?: string;
  }>;
}

export interface TaxFilingUpdateRequest extends Partial<Omit<TaxFiling, 'id' | 'company_id' | 'created_at' | 'updated_at' | 'submitted_by' | 'submitted_at'>> {
  attachments_to_delete?: string[];
  new_attachments?: Array<{
    file_name: string;
    file_type: string;
    file_size: number;
    file_data: string; // base64 encoded file
    attachment_type: 'return' | 'supporting_document' | 'receipt' | 'other';
    description?: string;
  }>;
}

export interface TaxFilingSubmitRequest {
  submit_notes?: string;
  submit_date?: string;
  notify_recipients?: string[];
}

export interface TaxFilingApproveRequest {
  review_notes?: string;
  approval_date?: string;
  next_steps?: string;
  notify_recipients?: string[];
}

export interface TaxFilingRejectRequest {
  rejection_reason: string;
  rejection_notes?: string;
  rejection_date?: string;
  resubmission_deadline?: string;
  notify_recipients?: string[];
}

export interface TaxFilingPaymentRequest {
  payment_amount: number;
  payment_date: string;
  payment_method: string;
  payment_reference: string;
  payment_notes?: string;
  receipt_file?: {
    file_name: string;
    file_type: string;
    file_size: number;
    file_data: string; // base64 encoded file
  };
  notify_recipients?: string[];
}

export interface TaxFilingExportRequest {
  format: 'pdf' | 'excel' | 'csv';
  include_attachments: boolean;
  include_notes: boolean;
  include_audit_trail: boolean;
  password_protect?: boolean;
  password?: string;
  email_to?: string;
  email_subject?: string;
  email_body?: string;
}

export interface TaxFilingImportRequest {
  file: File;
  mapping: Record<string, string>;
  options: {
    create_new: boolean;
    update_existing: boolean;
    skip_errors: boolean;
    validate_only: boolean;
  };
}
