export interface TaxPolicy {
  id: string;
  name: string;
  description: string;
  effective_date: string;
  expiry_date?: string;
  tax_rates: TaxRate[];
  tax_exemptions: TaxExemption[];
  created_at: string;
  updated_at: string;
}

export interface TaxRate {
  id: string;
  name: string;
  rate: number;
  type: 'percentage' | 'fixed';
  category: string;
  effective_date: string;
  expiry_date?: string;
  is_active: boolean;
}

export interface TaxExemption {
  id: string;
  type: string;
  reason: string;
  effective_date: string;
  expiry_date?: string;
  terms: string[];
  is_active: boolean;
}