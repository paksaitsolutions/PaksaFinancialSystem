import { apiClient } from '@/shared/services/api';
import type { AxiosResponse } from 'axios';
import type { GlAccount } from '../types/gl-account';

/**
 * Service for handling import/export operations for GL Accounts
 */
class GlImportExportService {
  /**
   * Export GL accounts to a file
   * @param format - The export format (csv, xlsx, pdf)
   * @param filters - Optional filters for the export
   * @returns Promise that resolves with the exported file data
   */
  async exportAccounts(
    format: 'csv' | 'xlsx' | 'pdf',
    filters: Record<string, any> = {}
  ): Promise<Blob> {
    const response = await apiClient.post<Blob>(
      `/gl/accounts/export?format=${format}`,
      filters,
      {
        responseType: 'blob',
        headers: {
          'Accept': this.getMimeType(format)
        }
      }
    );
    return response.data;
  }

  /**
   * Import GL accounts from a file
   * @param file - The file to import
   * @param options - Import options
   * @returns Promise that resolves with the import result
   */
  async importAccounts(
    file: File,
    options: {
      updateExisting: boolean;
      onProgress?: (progress: number) => void;
    } = { updateExisting: false }
  ): Promise<{ success: boolean; imported: number; updated: number; errors: string[] }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('updateExisting', options.updateExisting.toString());

    const response = await apiClient.post<{
      success: boolean;
      imported: number;
      updated: number;
      errors: string[];
    }>('/gl/accounts/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        if (options.onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          options.onProgress(progress);
        }
      }
    });

    return response.data;
  }

  /**
   * Download a template file for importing GL accounts
   * @param format - The template format (csv, xlsx)
   * @returns Promise that resolves with the template file data
   */
  async downloadTemplate(format: 'csv' | 'xlsx' = 'xlsx'): Promise<Blob> {
    const response = await apiClient.get<Blob>(
      `/gl/accounts/template.${format}`,
      {
        responseType: 'blob',
        headers: {
          'Accept': this.getMimeType(format)
        }
      }
    );
    return response.data;
  }

  /**
   * Get the MIME type for a given file format
   * @param format - The file format
   * @returns The corresponding MIME type
   */
  private getMimeType(format: string): string {
    const mimeTypes: Record<string, string> = {
      csv: 'text/csv',
      xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      pdf: 'application/pdf'
    };
    return mimeTypes[format] || 'application/octet-stream';
  }
}

export const glImportExportService = new GlImportExportService();

export default glImportExportService;
