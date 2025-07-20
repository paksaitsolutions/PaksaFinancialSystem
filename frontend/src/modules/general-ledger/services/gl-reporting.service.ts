import { ref } from 'vue';
import axios from 'axios';
import type { 
  AccountType,
  GlAccountFilters 
} from '../types/gl-account';

export const API_BASE_URL = '/api/gl/reports';

// Report types
type ReportFormat = 'pdf' | 'excel' | 'csv' | 'json';
type ReportPeriod = 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly' | 'custom';

interface ReportParameters {
  startDate?: string;
  endDate?: string;
  period?: ReportPeriod;
  accountIds?: string[];
  accountTypes?: AccountType[];
  includeDetails?: boolean;
  includeSummary?: boolean;
  includeCharts?: boolean;
  compareWithPrevious?: boolean;
  currency?: string;
}

interface ReportGenerationOptions {
  format: ReportFormat;
  includeCharts?: boolean;
  includeAppendices?: boolean;
  passwordProtect?: boolean;
  watermark?: boolean;
  language?: string;
}

interface ReportMetadata {
  id: string;
  name: string;
  description: string;
  category: string;
  availableFormats: ReportFormat[];
  supportsScheduling: boolean;
  supportsComparison: boolean;
  requiresDateRange: boolean;
}

class GlReportingService {
  private loading = ref(false);
  private error = ref<string | null>(null);

  /**
   * Get list of available reports with metadata
   */
  async getAvailableReports(): Promise<ReportMetadata[]> {
    try {
      this.loading.value = true;
      const response = await axios.get<ReportMetadata[]>(`${API_BASE_URL}/list`);
      return response.data;
    } catch (err) {
      this.handleError('Failed to fetch available reports', err);
      throw err;
    } finally {
      this.loading.value = false;
    }
  }

  /**
   * Generate a standard financial statement
   */
  async generateFinancialStatement(
    statementType: 'balance-sheet' | 'income-statement' | 'cash-flow' | 'retained-earnings',
    params: ReportParameters,
    options: ReportGenerationOptions
  ) {
    try {
      this.loading.value = true;
      const response = await axios.post(
        `${API_BASE_URL}/${statementType}`,
        { params, options },
        { responseType: this.getResponseType(options.format) }
      );
      return this.handleReportResponse(response, options.format);
    } catch (err) {
      this.handleError(`Failed to generate ${statementType}`, err);
      throw err;
    } finally {
      this.loading.value = false;
    }
  }

  /**
   * Generate a general ledger report
   */
  async generateGeneralLedgerReport(
    filters: GlAccountFilters,
    options: ReportGenerationOptions
  ) {
    try {
      this.loading.value = true;
      const response = await axios.post(
        `${API_BASE_URL}/general-ledger`,
        { filters, options },
        { responseType: this.getResponseType(options.format) }
      );
      return this.handleReportResponse(response, options.format);
    } catch (err) {
      this.handleError('Failed to generate general ledger report', err);
      throw err;
    } finally {
      this.loading.value = false;
    }
  }

  /**
   * Generate a trial balance report
   */
  async generateTrialBalance(
    asOfDate: string,
    options: ReportGenerationOptions
  ) {
    try {
      this.loading.value = true;
      const response = await axios.post(
        `${API_BASE_URL}/trial-balance`,
        { asOfDate, options },
        { responseType: this.getResponseType(options.format) }
      );
      return this.handleReportResponse(response, options.format);
    } catch (err) {
      this.handleError('Failed to generate trial balance', err);
      throw err;
    } finally {
      this.loading.value = false;
    }
  }

  /**
   * Generate an account activity report
   */
  async generateAccountActivityReport(
    accountId: string,
    startDate: string,
    endDate: string,
    options: ReportGenerationOptions
  ) {
    try {
      this.loading.value = true;
      const response = await axios.post(
        `${API_BASE_URL}/account-activity`,
        { accountId, startDate, endDate, options },
        { responseType: this.getResponseType(options.format) }
      );
      return this.handleReportResponse(response, options.format);
    } catch (err) {
      this.handleError('Failed to generate account activity report', err);
      throw err;
    } finally {
      this.loading.value = false;
    }
  }

  /**
   * Schedule a recurring report
   */
  async scheduleReport(
    reportId: string,
    schedule: {
      frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
      time: string;
      recipients: string[];
      format: ReportFormat;
      startDate?: string;
      endDate?: string;
    }
  ) {
    try {
      this.loading.value = true;
      const response = await axios.post(`${API_BASE_URL}/schedule`, {
        reportId,
        ...schedule
      });
      return response.data;
    } catch (err) {
      this.handleError('Failed to schedule report', err);
      throw err;
    } finally {
      this.loading.value = false;
    }
  }

  /**
   * Get report generation status
   */
  async getReportStatus(reportJobId: string) {
    try {
      this.loading.value = true;
      const response = await axios.get(`${API_BASE_URL}/status/${reportJobId}`);
      return response.data;
    } catch (err) {
      this.handleError('Failed to get report status', err);
      throw err;
    } finally {
      this.loading.value = false;
    }
  }

  /**
   * Download a previously generated report
   */
  async downloadReport(reportId: string, format: ReportFormat = 'pdf') {
    try {
      this.loading.value = true;
      const response = await axios.get(`${API_BASE_URL}/download/${reportId}`, {
        params: { format },
        responseType: this.getResponseType(format)
      });
      return this.handleReportResponse(response, format);
    } catch (err) {
      this.handleError('Failed to download report', err);
      throw err;
    } finally {
      this.loading.value = false;
    }
  }

  // Helper method to determine response type based on format
  private getResponseType(format: ReportFormat): 'json' | 'blob' | 'arraybuffer' | 'document' | 'text' | 'stream' {
    switch (format) {
      case 'json':
        return 'json';
      case 'pdf':
      case 'excel':
      case 'csv':
        return 'blob';
      default:
        return 'json';
    }
  }

  // Helper method to handle different report response types
  private handleReportResponse(response: any, format: ReportFormat) {
    if (format === 'json') {
      return response.data;
    } else {
      // For file downloads, return the blob and suggested filename
      const contentDisposition = response.headers['content-disposition'] || '';
      const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^\n]*)/);
      const filename = filenameMatch ? filenameMatch[1].replace(/['"]/g, '') : `report.${format}`;
      
      return {
        data: response.data,
        filename
      };
    }
  }

  // Helper method to handle errors consistently
  private handleError(message: string, error: unknown): void {
    const errorMessage = error instanceof Error ? error.message : String(error);
    console.error(`${message}:`, error);
    this.error.value = errorMessage;
    // Could integrate with a global error handling service here
  }

  // Getters for reactive state
  get isLoading() {
    return this.loading.value;
  }

  get hasError() {
    return this.error.value !== null;
  }

  get errorMessage() {
    return this.error.value;
  }
}

export const glReportingService = new GlReportingService();
