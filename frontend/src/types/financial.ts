/**
 * Financial Statement Types
 * Defines TypeScript interfaces for financial statements and related components
 */

export enum FinancialStatementType {
  BALANCE_SHEET = 'balance_sheet',
  INCOME_STATEMENT = 'income_statement',
  CASH_FLOW = 'cash_flow',
  CUSTOM = 'custom'
}

export enum LineType {
  HEADER = 'header',
  ACCOUNT = 'account',
  CALCULATION = 'calculation',
  TOTAL = 'total',
  SUBTOTAL = 'subtotal'
}

export interface FinancialStatementTemplate {
  id: string;
  name: string;
  description?: string;
  statement_type: FinancialStatementType;
  is_default: boolean;
  structure: FinancialStatementLine[];
  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
  company_id?: string;
  version?: number;
  is_active?: boolean;
}

export interface FinancialStatementLine {
  id: string;
  code: string;
  name: string;
  line_type: LineType;
  level: number;
  parent_id?: string | null;
  account_number?: string | null;
  calculation_formula?: string | null;
  display_order: number;
  is_bold: boolean;
  is_italic: boolean;
  is_underline: boolean;
  show_currency_symbol: boolean;
  show_thousands_separator: boolean;
  decimal_places: number;
  children?: FinancialStatementLine[];
  metadata?: Record<string, any>;
}

export interface FinancialStatementRequest {
  template_id: string;
  start_date?: string;
  end_date?: string;
  currency?: string;
  include_comparative?: boolean;
  include_budget?: boolean;
  include_ytd?: boolean;
  company_id?: string;
  parameters?: Record<string, any>;
}

export interface FinancialStatementResponse {
  id: string;
  template_id: string;
  template_name: string;
  statement_date: string;
  start_date: string;
  end_date: string;
  currency: string;
  data: FinancialStatementLine[];
  metadata: {
    generated_at: string;
    generated_by: string;
    parameters: Record<string, any>;
    totals?: Record<string, number>;
    company_info?: {
      name: string;
      tax_id?: string;
      address?: string;
      logo_url?: string;
    };
  };
}

export interface FinancialStatementExportOptions {
  format: 'pdf' | 'excel' | 'csv';
  include_notes?: boolean;
  include_company_info?: boolean;
  include_charts?: boolean;
  paper_size?: 'a4' | 'letter' | 'legal';
  orientation?: 'portrait' | 'landscape';
}

export interface FinancialStatementFilter {
  start_date?: string;
  end_date?: string;
  currency?: string;
  company_id?: string;
  template_id?: string;
  status?: 'draft' | 'final' | 'all';
  created_by?: string;
}

export interface FinancialStatementTemplateFilter {
  statement_type?: FinancialStatementType;
  is_default?: boolean;
  is_active?: boolean;
  company_id?: string;
  search?: string;
}

// For the template builder component
export interface TemplateBuilderNode {
  id: string;
  type: 'account' | 'calculation' | 'header' | 'total' | 'subtotal';
  label: string;
  data: Partial<FinancialStatementLine>;
  children?: TemplateBuilderNode[];
  isExpanded?: boolean;
  isSelected?: boolean;
}

// For the financial statement viewer component
export interface StatementViewerProps {
  data: FinancialStatementLine[];
  currency?: string;
  showAccountNumbers?: boolean;
  showFormulas?: boolean;
  onLineClick?: (line: FinancialStatementLine) => void;
  className?: string;
  style?: Record<string, any>;
}

// For the statement generation form
export interface StatementGenerationFormValues {
  template_id: string;
  start_date: string;
  end_date: string;
  currency: string;
  include_comparative: boolean;
  include_budget: boolean;
  include_ytd: boolean;
  parameters: Record<string, any>;
}

// For the template form
export interface TemplateFormValues {
  name: string;
  description: string;
  statement_type: FinancialStatementType;
  is_default: boolean;
  structure: FinancialStatementLine[];
}

// For API responses
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
  timestamp: string;
  pagination?: {
    total: number;
    page: number;
    limit: number;
    total_pages: number;
  };
}

export interface ErrorResponse {
  error: string;
  message: string;
  statusCode: number;
  timestamp: string;
  path: string;
  details?: Record<string, any>;
}
