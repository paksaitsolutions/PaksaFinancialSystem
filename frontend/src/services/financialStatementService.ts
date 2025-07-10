/**
 * Financial Statement Service
 * Handles all API calls related to financial statements and templates
 */

import apiClient from './api';
import type { AxiosResponse } from 'axios';

// Types
export interface FinancialStatementTemplate {
  id: string;
  name: string;
  description?: string;
  statement_type: 'balance_sheet' | 'income_statement' | 'cash_flow' | 'custom';
  is_default: boolean;
  structure: FinancialStatementLine[];
  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
}

export interface FinancialStatementLine {
  id: string;
  code: string;
  name: string;
  line_type: 'header' | 'account' | 'calculation' | 'total' | 'subtotal';
  level: number;
  parent_id?: string;
  account_number?: string;
  calculation_formula?: string;
  display_order: number;
  is_bold: boolean;
  is_italic: boolean;
  is_underline: boolean;
  show_currency_symbol: boolean;
  show_thousands_separator: boolean;
  decimal_places: number;
  children?: FinancialStatementLine[];
  amount?: number;
  amount_prev?: number;
  amount_ytd?: number;
  isHeader?: boolean;
}

export interface FinancialStatementRequest {
  template_id?: string;
  start_date?: string;
  end_date?: string;
  as_of_date?: string;
  currency?: string;
  include_comparative?: boolean;
  include_budget?: boolean;
  include_ytd?: boolean;
  include_notes?: boolean;
  format_currency?: boolean;
}

// Statement Types
export interface BalanceSheet {
  assets: FinancialStatementSection;
  liabilities: FinancialStatementSection;
  equity: FinancialStatementSection;
  metadata: {
    as_of_date: string;
    currency: string;
    generated_at: string;
  };
}

export interface IncomeStatement {
  revenue: FinancialStatementSection;
  cogs: FinancialStatementSection;
  expenses: FinancialStatementSection;
  other_income: FinancialStatementSection;
  other_expenses: FinancialStatementSection;
  metadata: {
    start_date: string;
    end_date: string;
    currency: string;
    generated_at: string;
  };
}

export interface CashFlowStatement {
  operating_activities: FinancialStatementSection;
  investing_activities: FinancialStatementSection;
  financing_activities: FinancialStatementSection;
  metadata: {
    start_date: string;
    end_date: string;
    currency: string;
    generated_at: string;
  };
}

export interface FinancialStatementSection {
  name: string;
  total: number;
  total_prev?: number;
  total_ytd?: number;
  lines: FinancialStatementLine[];
}

export interface FinancialStatementResponse<T = any> {
  success: boolean;
  data: {
    statement: T;
    template?: FinancialStatementTemplate;
    generated_at: string;
  };
  message?: string;
  error?: string;
}

// Template Management
const getTemplates = async (): Promise<FinancialStatementTemplate[]> => {
  const response = await apiClient.get('/gl/financial-statement-templates/');
  return response.data;
};

const getTemplateById = async (id: string): Promise<FinancialStatementTemplate> => {
  const response = await apiClient.get(`/gl/financial-statement-templates/${id}`);
  return response.data;
};

const createTemplate = async (template: Omit<FinancialStatementTemplate, 'id' | 'created_at' | 'updated_at'>): Promise<FinancialStatementTemplate> => {
  const response = await apiClient.post('/gl/financial-statement-templates/', template);
  return response.data;
};

const updateTemplate = async (id: string, template: Partial<FinancialStatementTemplate>): Promise<FinancialStatementTemplate> => {
  const response = await apiClient.put(`/gl/financial-statement-templates/${id}`, template);
  return response.data;
};

const deleteTemplate = async (id: string): Promise<void> => {
  await apiClient.delete(`/gl/financial-statement-templates/${id}`);
};

const setDefaultTemplate = async (id: string, statementType: string): Promise<FinancialStatementTemplate> => {
  const response = await apiClient.post(`/gl/financial-statement-templates/${id}/set-default`, { statement_type: statementType });
  return response.data;
};

const cloneTemplate = async (id: string, newName: string): Promise<FinancialStatementTemplate> => {
  const response = await apiClient.post(`/gl/financial-statement-templates/${id}/clone`, { name: newName });
  return response.data;
};

// Statement Generation
const generateStatement = async (params: FinancialStatementRequest): Promise<FinancialStatementResponse> => {
  const response = await apiClient.post('/gl/financial-statements/generate', params);
  return response.data;
};

const getStatementById = async (id: string): Promise<FinancialStatementResponse> => {
  const response = await apiClient.get(`/gl/financial-statements/${id}`);
  return response.data;
};

const exportStatement = async (id: string, format: 'pdf' | 'excel' | 'csv' = 'pdf'): Promise<Blob> => {
  const response = await apiClient.get(`/gl/financial-statements/${id}/export?format=${format}`, {
    responseType: 'blob'
  });
  return response.data;
};

// Helper function to build the statement structure as a tree
const buildStatementTree = (lines: FinancialStatementLine[]): FinancialStatementLine[] => {
  const map = new Map<string, FinancialStatementLine>();
  const tree: FinancialStatementLine[] = [];

  // First pass: Create a map of all lines
  lines.forEach(line => {
    map.set(line.id, { ...line, children: [] });
  });

  // Second pass: Build the tree structure
  lines.forEach(line => {
    const node = map.get(line.id);
    if (node) {
      if (line.parent_id && map.has(line.parent_id)) {
        const parent = map.get(line.parent_id);
        if (parent && parent.children) {
          parent.children.push(node);
        }
      } else {
        tree.push(node);
      }
    }
  });

  // Sort children by display_order
  const sortChildren = (nodes: FinancialStatementLine[]) => {
    nodes.sort((a, b) => a.display_order - b.display_order);
    nodes.forEach(node => {
      if (node.children && node.children.length > 0) {
        sortChildren(node.children);
      }
    });
  };

  sortChildren(tree);
  return tree;
};

export default {
  // Template Management
  getTemplates,
  getTemplateById,
  createTemplate,
  updateTemplate,
  deleteTemplate,
  setDefaultTemplate,
  cloneTemplate,
  
  // Statement Generation
  generateStatement,
  getStatementById,
  exportStatement,
  
  // Helpers
  buildStatementTree
};
