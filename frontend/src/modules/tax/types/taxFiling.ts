import type { TaxJurisdiction } from './taxJurisdiction';
import type { TaxPeriod } from './taxPeriod';

export interface TaxFiling {
  id: string;
  company_id: string;
  tax_period_id: string;
  tax_period?: TaxPeriod;
  jurisdiction_id: string;
  jurisdiction?: TaxJurisdiction;
  tax_type: string;
  filing_reference: string;
  filing_date: string | null;
  due_date: string;
  status: 'draft' | 'in_review' | 'approved' | 'filed' | 'accepted' | 'rejected' | 'paid' | 'overdue';
  payment_status: 'unpaid' | 'partial' | 'paid' | 'refunded' | 'overdue';
  total_amount: number;
  tax_amount: number;
  penalty_amount: number;
  interest_amount: number;
  paid_amount: number;
  balance_due: number;
  currency: string;
  notes: string | null;
  metadata: Record<string, any>;
  created_by: string;
  updated_by: string | null;
  created_at: string;
  updated_at: string;
  submitted_at: string | null;
  approved_at: string | null;
  filed_at: string | null;
  paid_at: string | null;
}

export interface TaxFilingCreate {
  company_id: string;
  tax_period_id: string;
  jurisdiction_id: string;
  tax_type: string;
  due_date: string;
  total_amount: number;
  tax_amount: number;
  penalty_amount?: number;
  interest_amount?: number;
  currency: string;
  notes?: string;
  metadata?: Record<string, any>;
}

export interface TaxFilingUpdate {
  tax_period_id?: string;
  jurisdiction_id?: string;
  tax_type?: string;
  filing_reference?: string;
  filing_date?: string | null;
  due_date?: string;
  status?: string;
  payment_status?: string;
  total_amount?: number;
  tax_amount?: number;
  penalty_amount?: number;
  interest_amount?: number;
  paid_amount?: number;
  balance_due?: number;
  currency?: string;
  notes?: string | null;
  metadata?: Record<string, any>;
  submitted_at?: string | null;
  approved_at?: string | null;
  filed_at?: string | null;
  paid_at?: string | null;
}

export interface TaxFilingFilter {
  company_id?: string;
  tax_period_id?: string;
  jurisdiction_id?: string;
  tax_type?: string;
  status?: string[];
  payment_status?: string[];
  start_date?: string;
  end_date?: string;
  due_date_start?: string;
  due_date_end?: string;
  search?: string;
}

export interface TaxFilingStats {
  total_filings: number;
  total_tax_amount: number;
  total_paid: number;
  total_outstanding: number;
  by_status: Array<{
    status: string;
    count: number;
    amount: number;
  }>;
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
}

export interface TaxFilingCalendarEvent {
  id: string;
  title: string;
  type: 'filing_due' | 'payment_due' | 'extension' | 'other';
  due_date: string;
  status: 'upcoming' | 'due_soon' | 'overdue' | 'completed' | 'extended';
  tax_type: string;
  jurisdiction_id: string;
  jurisdiction_name: string;
  filing_id?: string;
  notes?: string;
}

export interface TaxFilingFormData {
  tax_period_id: string;
  jurisdiction_id: string;
  tax_type: string;
  due_date: string;
  total_amount: number;
  tax_amount: number;
  penalty_amount: number;
  interest_amount: number;
  currency: string;
  notes: string;
  attachments: File[];
}

export interface TaxFilingSubmissionResult {
  success: boolean;
  filing: TaxFiling;
  message?: string;
  errors?: Record<string, string[]>;
  warnings?: string[];
}
