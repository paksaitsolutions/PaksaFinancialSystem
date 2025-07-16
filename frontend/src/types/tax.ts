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
  format: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  error?: string;
}