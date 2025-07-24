import { api } from '@/utils/api';

export interface CompanyReport {
  id: string;
  company_id: string;
  report_name: string;
  report_type: string;
  period_start: string;
  period_end: string;
  filters?: Record<string, any>;
  status: string;
  generated_at?: string;
  file_path?: string;
  file_format?: string;
  report_data?: Record<string, any>;
  generated_by: string;
  description?: string;
  created_at: string;
}

export interface ReportTemplate {
  id: string;
  company_id: string;
  template_name: string;
  report_type: string;
  template_config: Record<string, any>;
  is_default: boolean;
  is_active: boolean;
  created_at: string;
}

export interface ReportSchedule {
  id: string;
  company_id: string;
  schedule_name: string;
  report_type: string;
  cron_expression: string;
  is_active: boolean;
  report_config?: Record<string, any>;
  email_recipients?: string[];
  last_run?: string;
  next_run?: string;
  created_at: string;
}

/**
 * Enhanced Reports Service
 * Provides methods to interact with the enhanced reports API endpoints
 */
export default {
  /**
   * Generate Income Statement for company
   * @param companyId - Company ID
   * @param periodStart - Period start date
   * @param periodEnd - Period end date
   * @returns Promise with the generated report
   */
  async generateIncomeStatement(companyId: string, periodStart: Date, periodEnd: Date) {
    return api.post(`/enhanced-reports/${companyId}/income-statement`, {
      period_start: periodStart.toISOString(),
      period_end: periodEnd.toISOString()
    });
  },

  /**
   * Generate Balance Sheet for company
   * @param companyId - Company ID
   * @param asOfDate - As of date
   * @returns Promise with the generated report
   */
  async generateBalanceSheet(companyId: string, asOfDate: Date) {
    return api.post(`/enhanced-reports/${companyId}/balance-sheet`, {
      as_of_date: asOfDate.toISOString()
    });
  },

  /**
   * Generate Cash Flow Statement for company
   * @param companyId - Company ID
   * @param periodStart - Period start date
   * @param periodEnd - Period end date
   * @returns Promise with the generated report
   */
  async generateCashFlowStatement(companyId: string, periodStart: Date, periodEnd: Date) {
    return api.post(`/enhanced-reports/${companyId}/cash-flow`, {
      period_start: periodStart.toISOString(),
      period_end: periodEnd.toISOString()
    });
  },

  /**
   * Generate Aging Report for company
   * @param companyId - Company ID
   * @param agingType - Type of aging report (payables/receivables)
   * @param asOfDate - As of date
   * @returns Promise with the generated report
   */
  async generateAgingReport(companyId: string, agingType: string, asOfDate: Date) {
    return api.post(`/enhanced-reports/${companyId}/aging-report`, {
      aging_type: agingType,
      as_of_date: asOfDate.toISOString()
    });
  },

  /**
   * Generate Tax Summary Report for company
   * @param companyId - Company ID
   * @param periodStart - Period start date
   * @param periodEnd - Period end date
   * @param taxType - Tax type (VAT, GST, etc.)
   * @returns Promise with the generated report
   */
  async generateTaxSummaryReport(companyId: string, periodStart: Date, periodEnd: Date, taxType: string) {
    return api.post(`/enhanced-reports/${companyId}/tax-summary`, {
      period_start: periodStart.toISOString(),
      period_end: periodEnd.toISOString(),
      tax_type: taxType
    });
  },

  /**
   * Generate Audit Log Report for company
   * @param companyId - Company ID
   * @param periodStart - Period start date
   * @param periodEnd - Period end date
   * @returns Promise with the generated report
   */
  async generateAuditReport(companyId: string, periodStart: Date, periodEnd: Date) {
    return api.post(`/enhanced-reports/${companyId}/audit-report`, {
      period_start: periodStart.toISOString(),
      period_end: periodEnd.toISOString()
    });
  },

  /**
   * List reports for a company
   * @param companyId - Company ID
   * @param limit - Maximum number of records
   * @returns Promise with list of reports
   */
  async listCompanyReports(companyId: string, limit: number = 100) {
    return api.get(`/enhanced-reports/${companyId}/reports?limit=${limit}`);
  },

  /**
   * Get a specific report
   * @param reportId - Report ID
   * @returns Promise with report details
   */
  async getReport(reportId: string) {
    return api.get(`/enhanced-reports/report/${reportId}`);
  },

  /**
   * Create report template
   * @param companyId - Company ID
   * @param templateData - Template data
   * @returns Promise with created template
   */
  async createReportTemplate(companyId: string, templateData: {
    template_name: string;
    report_type: string;
    template_config: Record<string, any>;
    is_default?: boolean;
  }) {
    return api.post(`/enhanced-reports/${companyId}/templates`, templateData);
  },

  /**
   * Create report schedule
   * @param companyId - Company ID
   * @param scheduleData - Schedule data
   * @returns Promise with created schedule
   */
  async createReportSchedule(companyId: string, scheduleData: {
    schedule_name: string;
    report_type: string;
    cron_expression: string;
    report_config?: Record<string, any>;
    email_recipients?: string[];
  }) {
    return api.post(`/enhanced-reports/${companyId}/schedules`, scheduleData);
  },

  /**
   * Export report to PDF
   * @param reportId - Report ID
   * @returns Promise with PDF file
   */
  async exportReportToPDF(reportId: string) {
    return api.get(`/enhanced-reports/report/${reportId}/export/pdf`, {
      responseType: 'blob'
    });
  },

  /**
   * Export report to Excel
   * @param reportId - Report ID
   * @returns Promise with Excel file
   */
  async exportReportToExcel(reportId: string) {
    return api.get(`/enhanced-reports/report/${reportId}/export/excel`, {
      responseType: 'blob'
    });
  },

  /**
   * Export report to CSV
   * @param reportId - Report ID
   * @returns Promise with CSV file
   */
  async exportReportToCSV(reportId: string) {
    return api.get(`/enhanced-reports/report/${reportId}/export/csv`, {
      responseType: 'blob'
    });
  },

  /**
   * Utility functions for enhanced reports
   */
  utils: {
    /**
     * Format report type for display
     */
    formatReportType(type: string): string {
      const typeMap: Record<string, string> = {
        'income_statement': 'Income Statement',
        'balance_sheet': 'Balance Sheet',
        'cash_flow': 'Cash Flow Statement',
        'tax_summary': 'Tax Summary Report',
        'aging_report': 'Aging Report',
        'audit_log': 'Audit Log Report',
        'consolidated': 'Consolidated Report'
      };
      
      return typeMap[type] || type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    },

    /**
     * Get status color for UI
     */
    getStatusColor(status: string): string {
      const colorMap: Record<string, string> = {
        'pending': 'warning',
        'generating': 'info',
        'completed': 'success',
        'failed': 'error'
      };
      
      return colorMap[status] || 'grey';
    },

    /**
     * Get available report types
     */
    getReportTypes(): Array<{ value: string; label: string; description: string }> {
      return [
        {
          value: 'income_statement',
          label: 'Income Statement',
          description: 'Profit & Loss statement showing revenue and expenses'
        },
        {
          value: 'balance_sheet',
          label: 'Balance Sheet',
          description: 'Financial position showing assets, liabilities, and equity'
        },
        {
          value: 'cash_flow',
          label: 'Cash Flow Statement',
          description: 'Cash inflows and outflows from operations, investing, and financing'
        },
        {
          value: 'aging_report',
          label: 'Aging Report',
          description: 'Outstanding receivables or payables by age'
        },
        {
          value: 'tax_summary',
          label: 'Tax Summary',
          description: 'Summary of tax obligations and payments'
        },
        {
          value: 'audit_log',
          label: 'Audit Log Report',
          description: 'User activity and system changes audit trail'
        }
      ];
    },

    /**
     * Get available export formats
     */
    getExportFormats(): Array<{ value: string; label: string; icon: string }> {
      return [
        { value: 'pdf', label: 'PDF', icon: 'mdi-file-pdf-box' },
        { value: 'excel', label: 'Excel', icon: 'mdi-file-excel' },
        { value: 'csv', label: 'CSV', icon: 'mdi-file-delimited' }
      ];
    },

    /**
     * Format currency amount
     */
    formatCurrency(amount: number, currency: string = 'USD'): string {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
      }).format(amount);
    },

    /**
     * Format percentage
     */
    formatPercentage(value: number): string {
      return new Intl.NumberFormat('en-US', {
        style: 'percent',
        minimumFractionDigits: 1,
        maximumFractionDigits: 1
      }).format(value / 100);
    },

    /**
     * Calculate period label
     */
    getPeriodLabel(startDate: string, endDate: string): string {
      const start = new Date(startDate);
      const end = new Date(endDate);
      
      if (start.getFullYear() === end.getFullYear()) {
        if (start.getMonth() === end.getMonth()) {
          return `${start.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}`;
        } else {
          return `${start.toLocaleDateString('en-US', { month: 'short' })} - ${end.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}`;
        }
      } else {
        return `${start.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })} - ${end.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}`;
      }
    },

    /**
     * Validate date range
     */
    validateDateRange(startDate: Date, endDate: Date): { valid: boolean; message?: string } {
      if (startDate >= endDate) {
        return { valid: false, message: 'End date must be after start date' };
      }
      
      const maxRange = 365 * 2; // 2 years
      const daysDiff = (endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24);
      
      if (daysDiff > maxRange) {
        return { valid: false, message: 'Date range cannot exceed 2 years' };
      }
      
      return { valid: true };
    },

    /**
     * Get common date ranges
     */
    getCommonDateRanges(): Array<{ label: string; getValue: () => { start: Date; end: Date } }> {
      const now = new Date();
      const currentYear = now.getFullYear();
      const currentMonth = now.getMonth();
      
      return [
        {
          label: 'This Month',
          getValue: () => ({
            start: new Date(currentYear, currentMonth, 1),
            end: new Date(currentYear, currentMonth + 1, 0)
          })
        },
        {
          label: 'Last Month',
          getValue: () => ({
            start: new Date(currentYear, currentMonth - 1, 1),
            end: new Date(currentYear, currentMonth, 0)
          })
        },
        {
          label: 'This Quarter',
          getValue: () => {
            const quarterStart = Math.floor(currentMonth / 3) * 3;
            return {
              start: new Date(currentYear, quarterStart, 1),
              end: new Date(currentYear, quarterStart + 3, 0)
            };
          }
        },
        {
          label: 'This Year',
          getValue: () => ({
            start: new Date(currentYear, 0, 1),
            end: new Date(currentYear, 11, 31)
          })
        },
        {
          label: 'Last Year',
          getValue: () => ({
            start: new Date(currentYear - 1, 0, 1),
            end: new Date(currentYear - 1, 11, 31)
          })
        }
      ];
    }
  }
};