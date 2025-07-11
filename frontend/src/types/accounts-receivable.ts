export interface InvoiceCreate {
  customer_name: string;
  issue_date: string;
  due_date: string;
  notes?: string;
  invoice_items: InvoiceItemCreate[];
}
export interface InvoiceItemCreate {
  description: string;
  quantity: number;
  unit_price: number;
  discount_percent: number;
  tax_rate: number;
}
export interface InvoiceResponse extends InvoiceCreate {
  id: string;
  invoice_number: string;
  status: string;
  total_amount: number;
  created_at: string;
  updated_at: string;
}
export interface PaymentCreate {
  customer_id: string;
  payment_date: string;
  amount: number;
  payment_method: string;
  reference_number?: string;
  notes?: string;
  invoice_ids?: string[];
}
export interface PaymentResponse extends PaymentCreate {
  id: string;
  payment_number: string;
  status: string;
  created_at: string;
  updated_at: string;
}
export interface CreditNoteCreate {
  customer_id: string;
  issue_date: string;
  reference_invoice_id?: string;
  reason?: string;
  credit_note_items: CreditNoteItemCreate[];
}
export interface CreditNoteItemCreate {
  description: string;
  quantity: number;
  unit_price: number;
  tax_rate: number;
}
export interface CreditNoteResponse extends CreditNoteCreate {
  id: string;
  credit_note_number: string;
  status: string;
  total_amount: number;
  remaining_amount: number;
  created_at: string;
  updated_at: string;
}
