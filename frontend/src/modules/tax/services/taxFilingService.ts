import { http } from '@/api/axios';
import type { TaxFiling, TaxFilingCreate, TaxFilingUpdate, TaxFilingFilter } from '../types/taxFiling';
import type { TaxReturnAttachment } from '../types/taxAttachment';

export const TaxFilingService = {
  /**
   * Get all tax filings with optional filtering and pagination
   */
  async getFilings(params?: TaxFilingFilter & { page?: number; limit?: number }) {
    const response = await http.get('/api/v1/tax/filings', { params });
    return response.data;
  },

  /**
   * Get a single tax filing by ID
   */
  async getFilingById(id: string) {
    const response = await http.get(`/api/v1/tax/filings/${id}`);
    return response.data;
  },

  /**
   * Create a new tax filing
   */
  async createFiling(filing: TaxFilingCreate) {
    const response = await http.post('/api/v1/tax/filings', filing);
    return response.data;
  },

  /**
   * Update an existing tax filing
   */
  async updateFiling(id: string, updates: TaxFilingUpdate) {
    const response = await http.put(`/api/v1/tax/filings/${id}`, updates);
    return response.data;
  },

  /**
   * Submit a tax filing for processing
   */
  async submitFiling(id: string) {
    const response = await http.post(`/api/v1/tax/filings/${id}/submit`);
    return response.data;
  },

  /**
   * Get attachments for a tax filing
   */
  async getFilingAttachments(filingId: string) {
    const response = await http.get(`/api/v1/tax/filings/${filingId}/attachments`);
    return response.data;
  },

  /**
   * Get a pre-signed URL for uploading an attachment
   */
  async getUploadUrl(fileData: { 
    file_name: string; 
    file_type: string; 
    file_size: number; 
    attachment_type: string;
  }) {
    const response = await http.post('/api/v1/tax/attachments/upload-url', fileData);
    return response.data;
  },

  /**
   * Confirm an attachment upload and associate it with a filing
   */
  async confirmAttachmentUpload(attachmentId: string, filingId: string) {
    const response = await http.post(
      `/api/v1/tax/attachments/${attachmentId}/confirm`,
      { tax_return_id: filingId }
    );
    return response.data;
  },

  /**
   * Delete an attachment
   */
  async deleteAttachment(attachmentId: string) {
    await http.delete(`/api/v1/tax/attachments/${attachmentId}`);
  },

  /**
   * Get filing calendar for the organization
   */
  async getFilingCalendar(params: { 
    start_date: string; 
    end_date: string; 
    jurisdiction_code?: string;
  }) {
    const response = await http.get('/api/v1/tax/calendar', { params });
    return response.data;
  },

  /**
   * Get filing history for a specific tax type and period
   */
  async getFilingHistory(params: {
    tax_type: string;
    start_date: string;
    end_date: string;
    status?: string;
  }) {
    const response = await http.get('/api/v1/tax/filings/history', { params });
    return response.data;
  },

  /**
   * Download a filed return
   */
  async downloadFiling(filingId: string, format: 'pdf' | 'excel' | 'csv' = 'pdf') {
    const response = await http.get(`/api/v1/tax/filings/${filingId}/download`, {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  },

  /**
   * Get filing statistics
   */
  async getFilingStats(params?: { 
    start_date?: string; 
    end_date?: string; 
    tax_type?: string;
  }) {
    const response = await http.get('/api/v1/tax/filings/stats', { params });
    return response.data;
  },
};
