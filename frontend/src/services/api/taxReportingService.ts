import { TaxPolicy, TaxRate, TaxExemption, TaxCalculationRequest, TaxCalculationResponse } from '@/types/tax';
import { apiClient } from '@/utils/apiClient';

// Interfaces for tax reporting
export interface TaxLiabilityReportRequest {
  startDate: string | Date;
  endDate: string | Date;
  taxTypes?: string[];
  jurisdictionCodes?: string[];
  groupBy?: 'day' | 'week' | 'month' | 'quarter' | 'year';
  page?: number;
  pageSize?: number;
}

export interface TaxLiabilityReportResponse {
  company_id: string;
  start_date: string;
  end_date: string;
  total_taxable_amount: string;
  total_tax_amount: string;
  total_transactions: number;
  periods: Array<{
    period_start: string;
    period_end: string;
    tax_type: string;
    jurisdiction_code: string;
    taxable_amount: string;
    tax_amount: string;
    transaction_count: number;
  }>;
  pagination: {
    page: number;
    page_size: number;
    total_items: number;
    total_pages: number;
  };
  metadata: Record<string, any>;
}

export interface TaxComplianceStatus {
  status: 'compliant' | 'non_compliant' | 'at_risk';
  last_updated: string;
  outstanding_liabilities: number;
  upcoming_filings: number;
  recent_audits: Array<{
    id: string;
    type: string;
    status: 'passed' | 'failed' | 'in_progress';
    date: string;
  }>;
}

export interface TaxFiling {
  id: string;
  type: string;
  period_start: string;
  period_end: string;
  due_date: string;
  status: 'draft' | 'submitted' | 'paid' | 'overdue' | 'cancelled';
  tax_amount: number;
  penalty_amount: number;
  total_amount: number;
  payment_date?: string;
  reference_number?: string;
  documents: Array<{
    id: string;
    name: string;
    type: string;
    url: string;
    uploaded_at: string;
  }>;
  created_at: string;
  updated_at: string;
}

export interface TaxFilingCreate {
  type: string;
  period_start: string;
  period_end: string;
  tax_amount: number;
  payment_date?: string;
  reference_number?: string;
}

export interface TaxFilingSubmit extends TaxFilingCreate {
  payment_method: string;
  payment_reference: string;
  notes?: string;
}

export interface TaxFilingUpcoming {
  type: string;
  period_start: string;
  period_end: string;
  due_date: string;
  estimated_tax: number;
  is_recurring: boolean;
  frequency: 'monthly' | 'quarterly' | 'annually';
}

export interface TaxReportFilter {
  startDate?: string;
  endDate?: string;
  type?: string;
  status?: string;
  jurisdiction?: string;
  search?: string;
}

export interface TaxReportResponse<T> {
  data: T[];
  pagination: {
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
  };
}

export interface TaxFilingResponse {
  filing: TaxFiling;
  documents: Array<{
    id: string;
    name: string;
    type: string;
    url: string;
    uploaded_at: string;
  }>;
}

class TaxReportingService {
  private baseUrl = '/api/v1/tax';

  async getCurrentPolicy(): Promise<TaxPolicy> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/policy/current`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch tax policy');
    }
  }

  async updatePolicy(policy: Partial<TaxPolicy>): Promise<TaxPolicy> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/policy`, policy);
      return response.data;
    } catch (error) {
      throw new Error('Failed to update tax policy');
    }
  }

  async addTaxRate(rate: TaxRate): Promise<TaxRate> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/rates`, rate);
      return response.data;
    } catch (error) {
      throw new Error('Failed to add tax rate');
    }
  }

  async updateTaxRate(rateId: string, updates: Partial<TaxRate>): Promise<TaxRate> {
    try {
      const response = await apiClient.put(`${this.baseUrl}/rates/${rateId}`, updates);
      return response.data;
    } catch (error) {
      throw new Error('Failed to update tax rate');
    }
  }

  async removeTaxRate(rateId: string): Promise<void> {
    try {
      await apiClient.delete(`${this.baseUrl}/rates/${rateId}`);
    } catch (error) {
      throw new Error('Failed to remove tax rate');
    }
  }

  async addTaxExemption(exemption: TaxExemption): Promise<TaxExemption> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/exemptions`, exemption);
      return response.data;
    } catch (error) {
      throw new Error('Failed to add tax exemption');
    }
  }

  async updateTaxExemption(exemptionId: string, updates: Partial<TaxExemption>): Promise<TaxExemption> {
    try {
      const response = await apiClient.put(`${this.baseUrl}/exemptions/${exemptionId}`, updates);
      return response.data;
    } catch (error) {
      throw new Error('Failed to update tax exemption');
    }
  }

  async removeTaxExemption(exemptionId: string): Promise<void> {
    try {
      await apiClient.delete(`${this.baseUrl}/exemptions/${exemptionId}`);
    } catch (error) {
      throw new Error('Failed to remove tax exemption');
    }
  }

  async calculateTaxes(request: TaxCalculationRequest): Promise<TaxCalculationResponse> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/calculate`, request);
      return response.data;
    } catch (error) {
      throw new Error('Failed to calculate taxes');
    }
  }

  // Tax Reporting Methods
  
  /**
   * Generate a tax liability report
   */
  async generateTaxLiabilityReport(
    params: TaxLiabilityReportRequest
  ): Promise<{ data: TaxLiabilityReportResponse }> {
    try {
      // Convert dates to ISO string if they are Date objects
      const queryParams = {
        ...params,
        startDate: params.startDate instanceof Date ? params.startDate.toISOString().split('T')[0] : params.startDate,
        endDate: params.endDate instanceof Date ? params.endDate.toISOString().split('T')[0] : params.endDate,
      };
      
      const response = await apiClient.get(`${this.baseUrl}/reports/liability`, { params: queryParams });
      return response.data;
    } catch (error) {
      console.error('Error generating tax liability report:', error);
      throw new Error('Failed to generate tax liability report');
    }
  }
  
  /**
   * Generate a tax liability report asynchronously
   */
  async generateTaxLiabilityReportAsync(
    params: TaxLiabilityReportRequest
  ): Promise<{ report_id: string; status_endpoint: string }> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/reports/liability/async`, params);
      return response.data;
    } catch (error) {
      console.error('Error scheduling tax liability report:', error);
      throw new Error('Failed to schedule tax liability report');
    }
  }
  
  /**
   * Get the status of an async tax report
   */
  async getTaxReportStatus(reportId: string): Promise<{ status: string; progress?: number; report?: any }> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/reports/status/${reportId}`);
      return response.data;
    } catch (error) {
      console.error('Error getting tax report status:', error);
      throw new Error('Failed to get tax report status');
    }
  }
  
  /**
   * Get tax compliance status
   */
  async getTaxComplianceStatus(companyId: string): Promise<{ data: TaxComplianceStatus }> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/compliance/status`, { 
        params: { company_id: companyId } 
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching tax compliance status:', error);
      throw new Error('Failed to fetch tax compliance status');
    }
  }
  
  /**
   * Get upcoming tax filings
   */
  async getUpcomingTaxFilings(companyId: string): Promise<{ data: TaxFilingUpcoming[] }> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/filings/upcoming`, { 
        params: { company_id: companyId } 
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching upcoming tax filings:', error);
      throw new Error('Failed to fetch upcoming tax filings');
    }
  }
  
  /**
   * Get tax filing by ID
   */
  async getTaxFiling(filingId: string): Promise<{ data: TaxFilingResponse }> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/filings/${filingId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching tax filing:', error);
      throw new Error('Failed to fetch tax filing');
    }
  }
  
  /**
   * Get paginated list of tax filings
   */
  async getTaxFilings(
    companyId: string, 
    filter: TaxReportFilter = {},
    page: number = 1,
    pageSize: number = 20
  ): Promise<TaxReportResponse<TaxFiling>> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/filings`, { 
        params: { 
          company_id: companyId,
          ...filter,
          page,
          page_size: pageSize
        } 
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching tax filings:', error);
      throw new Error('Failed to fetch tax filings');
    }
  }
  
  /**
   * Prepare a new tax filing
   */
  async prepareTaxFiling(filing: TaxFilingCreate): Promise<{ data: TaxFiling }> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/filings`, filing);
      return response.data;
    } catch (error) {
      console.error('Error preparing tax filing:', error);
      throw new Error('Failed to prepare tax filing');
    }
  }
  
  /**
   * Submit a tax filing
   */
  async submitTaxFiling(filingId: string, data: TaxFilingSubmit): Promise<{ data: TaxFiling }> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/filings/${filingId}/submit`, data);
      return response.data;
    } catch (error) {
      console.error('Error submitting tax filing:', error);
      throw new Error('Failed to submit tax filing');
    }
  }
  
  /**
   * Download a tax filing document
   */
  async downloadFilingDocument(filingId: string, documentId: string): Promise<Blob> {
    try {
      const response = await apiClient.get(
        `${this.baseUrl}/filings/${filingId}/documents/${documentId}/download`,
        { responseType: 'blob' }
      );
      return response.data;
    } catch (error) {
      console.error('Error downloading tax document:', error);
      throw new Error('Failed to download tax document');
    }
  }
  
  /**
   * Upload a document to a tax filing
   */
  async uploadFilingDocument(
    filingId: string, 
    file: File, 
    documentType: string
  ): Promise<{ data: { id: string; name: string; type: string; url: string } }> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('document_type', documentType);
      
      const response = await apiClient.post(
        `${this.baseUrl}/filings/${filingId}/documents`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      
      return response.data;
    } catch (error) {
      console.error('Error uploading tax document:', error);
      throw new Error('Failed to upload tax document');
    }
  }
  
  /**
   * Delete a document from a tax filing
   */
  async deleteFilingDocument(filingId: string, documentId: string): Promise<void> {
    try {
      await apiClient.delete(`${this.baseUrl}/filings/${filingId}/documents/${documentId}`);
    } catch (error) {
      console.error('Error deleting tax document:', error);
      throw new Error('Failed to delete tax document');
    }
  }
  
  /**
   * Export a tax report
   */
  async exportTaxReport(
    format: 'pdf' | 'excel' | 'csv',
    params: TaxLiabilityReportRequest
  ): Promise<Blob> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/reports/export/${format}`, {
        params,
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error('Error exporting tax report:', error);
      throw new Error(`Failed to export tax report as ${format.toUpperCase()}`);
    }
  }
}

export const taxReportingService = new TaxReportingService();