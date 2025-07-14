import { apiClient } from '@/services/apiClient';
import {
  TaxLiabilityReport,
  TaxFiling,
  TaxFilingCreate,
  TaxFilingSubmit,
  TaxComplianceStatus,
  TaxFilingUpcoming,
  TaxReportFilter,
  TaxReportResponse,
  TaxFilingResponse
} from '@/types/tax/reporting';

const BASE_PATH = '/api/tax';

/**
 * Tax Reporting API Service
 * Provides methods to interact with the tax reporting API endpoints
 */
class TaxReportingService {
  /**
   * Get tax liability report
   * @param filter Report filter parameters
   * @returns Tax liability report data
   */
  async getTaxLiabilityReport(filter: TaxReportFilter): Promise<TaxLiabilityReport> {
    try {
      const response = await apiClient.get(`${BASE_PATH}/reports/liability`, { params: filter });
      return response.data;
    } catch (error) {
      console.error('Error fetching tax liability report:', error);
      throw error;
    }
  }

  /**
   * Prepare a tax filing
   * @param filingData Tax filing data
   * @returns Created tax filing
   */
  async prepareTaxFiling(filingData: TaxFilingCreate): Promise<TaxFiling> {
    try {
      const response = await apiClient.post(`${BASE_PATH}/filings/prepare`, filingData);
      return response.data.data;
    } catch (error) {
      console.error('Error preparing tax filing:', error);
      throw error;
    }
  }

  /**
   * Submit a tax filing
   * @param filingId ID of the filing to submit
   * @param submissionData Submission data
   * @returns Updated tax filing
   */
  async submitTaxFiling(filingId: string, submissionData: TaxFilingSubmit): Promise<TaxFiling> {
    try {
      const response = await apiClient.post(
        `${BASE_PATH}/filings/${filingId}/submit`,
        submissionData
      );
      return response.data.data;
    } catch (error) {
      console.error('Error submitting tax filing:', error);
      throw error;
    }
  }

  /**
   * Get tax compliance status
   * @param taxTypes Optional filter by tax types
   * @param jurisdictionCodes Optional filter by jurisdiction codes
   * @returns Tax compliance status
   */
  async getTaxComplianceStatus(
    taxTypes?: string[],
    jurisdictionCodes?: string[]
  ): Promise<TaxComplianceStatus> {
    try {
      const params: any = {};
      if (taxTypes) params.tax_types = taxTypes.join(',');
      if (jurisdictionCodes) params.jurisdiction_codes = jurisdictionCodes.join(',');

      const response = await apiClient.get(`${BASE_PATH}/compliance/status`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching tax compliance status:', error);
      throw error;
    }
  }

  /**
   * Get upcoming tax filings
   * @param daysAhead Number of days to look ahead (default: 90)
   * @returns List of upcoming tax filings
   */
  async getUpcomingTaxFilings(daysAhead = 90): Promise<TaxFilingUpcoming[]> {
    try {
      const response = await apiClient.get(`${BASE_PATH}/filings/upcoming`, {
        params: { days_ahead: daysAhead }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching upcoming tax filings:', error);
      throw error;
    }
  }

  /**
   * Get tax filing by ID
   * @param filingId ID of the filing to retrieve
   * @returns Tax filing details
   */
  async getTaxFiling(filingId: string): Promise<TaxFiling> {
    try {
      const response = await apiClient.get(`${BASE_PATH}/filings/${filingId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching tax filing:', error);
      throw error;
    }
  }

  /**
   * Get tax filings with filtering and pagination
   * @param filter Filter parameters
   * @returns Paginated list of tax filings
   */
  async getTaxFilings(filter: Partial<TaxReportFilter> = {}): Promise<TaxReportResponse<TaxFiling>> {
    try {
      const response = await apiClient.get(`${BASE_PATH}/filings`, { params: filter });
      return response.data;
    } catch (error) {
      console.error('Error fetching tax filings:', error);
      throw error;
    }
  }

  /**
   * Download tax filing document
   * @param filingId ID of the filing
   * @param documentId ID of the document to download
   * @returns Blob of the document
   */
  async downloadFilingDocument(filingId: string, documentId: string): Promise<Blob> {
    try {
      const response = await apiClient.get(`${BASE_PATH}/filings/${filingId}/documents/${documentId}/download`, {
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error('Error downloading tax filing document:', error);
      throw error;
    }
  }

  /**
   * Upload document to tax filing
   * @param filingId ID of the filing
   * @param file File to upload
   * @param documentType Type of document
   * @param description Optional description
   * @returns Uploaded document details
   */
  async uploadFilingDocument(
    filingId: string,
    file: File,
    documentType: string,
    description?: string
  ) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('document_type', documentType);
      if (description) formData.append('description', description);

      const response = await apiClient.post(
        `${BASE_PATH}/filings/${filingId}/documents`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error uploading tax filing document:', error);
      throw error;
    }
  }

  /**
   * Delete tax filing document
   * @param filingId ID of the filing
   * @param documentId ID of the document to delete
   */
  async deleteFilingDocument(filingId: string, documentId: string): Promise<void> {
    try {
      await apiClient.delete(`${BASE_PATH}/filings/${filingId}/documents/${documentId}`);
    } catch (error) {
      console.error('Error deleting tax filing document:', error);
      throw error;
    }
  }

  /**
   * Export tax report to specified format
   * @param format Export format (csv, excel, pdf)
   * @param filter Filter parameters
   * @returns Blob of the exported file
   */
  async exportTaxReport(
    format: 'csv' | 'excel' | 'pdf',
    filter: TaxReportFilter
  ): Promise<Blob> {
    try {
      const response = await apiClient.get(`${BASE_PATH}/reports/export/${format}`, {
        params: filter,
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error(`Error exporting tax report to ${format}:`, error);
      throw error;
    }
  }
}

export const taxReportingService = new TaxReportingService();
export default taxReportingService;
