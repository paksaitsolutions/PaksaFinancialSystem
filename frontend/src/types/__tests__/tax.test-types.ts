import { UUID } from '../common';

export interface TaxTransaction {
  id: UUID;
  transaction_date: string;
  reference_number: string;
  description: string;
  total_amount: number;
  tax_amount: number;
  status: 'draft' | 'posted' | 'void';
  void_reason?: string;
  created_at: string;
  updated_at: string;
}

export interface TaxTransactionCreate {
  transaction_date: string;
  reference_number: string;
  description: string;
  total_amount: number;
  tax_amount: number;
  [key: string]: any;
}

export interface TaxTransactionUpdate {
  description?: string;
  total_amount?: number;
  tax_amount?: number;
  [key: string]: any;
}

export interface TaxTransactionFilter {
  start_date?: string | Date;
  end_date?: string | Date;
  status?: 'draft' | 'posted' | 'void';
  reference_number?: string;
  [key: string]: any;
}

export interface TaxTransactionComponent {
  id: string;
  transaction_id: UUID;
  tax_rate_id: string;
  taxable_amount: number;
  tax_amount: number;
  tax_rate: number;
  [key: string]: any;
}
