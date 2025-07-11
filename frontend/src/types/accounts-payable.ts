export interface BillCreate {
  vendor_name: string;
  issue_date: string;
  due_date: string;
  notes?: string;
  bill_items: BillItemCreate[];
}
export interface BillItemCreate {
  description: string;
  quantity: number;
  unit_price: number;
  discount_percent: number;
  tax_rate: number;
}
export interface BillResponse extends BillCreate {
  id: string;
  bill_number: string;
  status: string;
  total_amount: number;
  created_at: string;
  updated_at: string;
}
export interface PaymentCreate {
  vendor_id: string;
  payment_date: string;
  amount: number;
  payment_method: string;
  reference_number?: string;
  notes?: string;
  bill_ids?: string[];
}
export interface PaymentResponse extends PaymentCreate {
  id: string;
  payment_number: string;
  status: string;
  created_at: string;
  updated_at: string;
}
export interface VendorCreate {
  name: string;
  contact_name?: string;
  email?: string;
  phone?: string;
  address?: string;
}
export interface VendorResponse extends VendorCreate {
  id: string;
  created_at: string;
  updated_at: string;
}
