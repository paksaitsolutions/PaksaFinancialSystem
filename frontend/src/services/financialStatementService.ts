import { api } from '@/utils/api';
import { format } from 'date-fns';

/**
 * Financial Statement Service
 * Provides methods to interact with the financial statement API endpoints
 */
export default {
  /**
   * Generate all financial statements (balance sheet, income statement, cash flow)
   * @param companyId - The company ID
   * @param asOfDate - The date to generate statements for
   * @param options - Additional options
   * @returns Promise with the generated statements
   */
  async generateAllStatements(
    companyId: string,
    asOfDate: Date,
    options = {
      includeComparative: true,
      includeYtd: true,
      currency: 'USD',
      formatCurrency: true
    }
  ) {
    const formattedDate = format(asOfDate, 'yyyy-MM-dd');
    const params = new URLSearchParams({
      company_id: companyId,
      as_of_date: formattedDate,
      include_comparative: options.includeComparative.toString(),
      include_ytd: options.includeYtd.toString(),
      currency: options.currency,
      format_currency: options.formatCurrency.toString()
    });

    return api.get(`/financial-statements/generate-all?${params.toString()}`);
  },

  /**
   * Generate a balance sheet
   * @param companyId - The company ID
   * @param asOfDate - The date to generate the balance sheet for
   * @param options - Additional options
   * @returns Promise with the generated balance sheet
   */
  async generateBalanceSheet(
    companyId: string,
    asOfDate: Date,
    options = {
      includeComparative: true,
      currency: 'USD',
      formatCurrency: true
    }
  ) {
    const formattedDate = format(asOfDate, 'yyyy-MM-dd');
    const params = new URLSearchParams({
      company_id: companyId,
      as_of_date: formattedDate,
      include_comparative: options.includeComparative.toString(),
      currency: options.currency,
      format_currency: options.formatCurrency.toString()
    });

    return api.get(`/financial-statements/balance-sheet?${params.toString()}`);
  },

  /**
   * Generate an income statement
   * @param companyId - The company ID
   * @param startDate - Start date of the period
   * @param endDate - End date of the period
   * @param options - Additional options
   * @returns Promise with the generated income statement
   */
  async generateIncomeStatement(
    companyId: string,
    startDate: Date,
    endDate: Date,
    options = {
      includeComparative: true,
      includeYtd: true,
      currency: 'USD',
      formatCurrency: true
    }
  ) {
    const formattedStartDate = format(startDate, 'yyyy-MM-dd');
    const formattedEndDate = format(endDate, 'yyyy-MM-dd');
    const params = new URLSearchParams({
      company_id: companyId,
      start_date: formattedStartDate,
      end_date: formattedEndDate,
      include_comparative: options.includeComparative.toString(),
      include_ytd: options.includeYtd.toString(),
      currency: options.currency,
      format_currency: options.formatCurrency.toString()
    });

    return api.get(`/financial-statements/income-statement?${params.toString()}`);
  },

  /**
   * Generate a cash flow statement
   * @param companyId - The company ID
   * @param startDate - Start date of the period
   * @param endDate - End date of the period
   * @param options - Additional options
   * @returns Promise with the generated cash flow statement
   */
  async generateCashFlowStatement(
    companyId: string,
    startDate: Date,
    endDate: Date,
    options = {
      includeComparative: true,
      currency: 'USD',
      formatCurrency: true
    }
  ) {
    const formattedStartDate = format(startDate, 'yyyy-MM-dd');
    const formattedEndDate = format(endDate, 'yyyy-MM-dd');
    const params = new URLSearchParams({
      company_id: companyId,
      start_date: formattedStartDate,
      end_date: formattedEndDate,
      include_comparative: options.includeComparative.toString(),
      currency: options.currency,
      format_currency: options.formatCurrency.toString()
    });

    return api.get(`/financial-statements/cash-flow?${params.toString()}`);
  },

  /**
   * Get a financial statement by ID
   * @param statementId - The financial statement ID
   * @returns Promise with the financial statement
   */
  async getFinancialStatement(statementId: string) {
    return api.get(`/financial-statements/${statementId}`);
  },

  /**
   * List financial statements for a company
   * @param companyId - The company ID
   * @param options - Filter options
   * @returns Promise with the list of financial statements
   */
  async listFinancialStatements(
    companyId: string,
    options = {
      statementType: null,
      startDate: null,
      endDate: null,
      isFinal: null,
      skip: 0,
      limit: 100
    }
  ) {
    const params = new URLSearchParams({
      company_id: companyId,
      skip: options.skip.toString(),
      limit: options.limit.toString()
    });

    if (options.statementType) {
      params.append('statement_type', options.statementType);
    }

    if (options.startDate) {
      params.append('start_date', format(options.startDate, 'yyyy-MM-dd'));
    }

    if (options.endDate) {
      params.append('end_date', format(options.endDate, 'yyyy-MM-dd'));
    }

    if (options.isFinal !== null) {
      params.append('is_final', options.isFinal.toString());
    }

    return api.get(`/financial-statements/company/${companyId}?${params.toString()}`);
  },

  /**
   * Export a financial statement to PDF
   * @param statementId - The financial statement ID
   * @returns Promise with the PDF file
   */
  async exportToPdf(statementId: string) {
    return api.get(`/financial-statements/${statementId}/export/pdf`, {
      responseType: 'blob'
    });
  },

  /**
   * Export a financial statement to Excel
   * @param statementId - The financial statement ID
   * @returns Promise with the Excel file
   */
  async exportToExcel(statementId: string) {
    return api.get(`/financial-statements/${statementId}/export/excel`, {
      responseType: 'blob'
    });
  }
};